import logging

from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty
import migrate.versioning.api

from .dbbase import *


class NATAppDbException(Exception):
    def __init__(self, ex):
        self.ex = ex


def catch_db_error(f):
    def catch_db_error_wrap(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            logging.getLogger().info(f"Successful call at {f}: {result}")
            return result
        except Exception as ex:
            logging.getLogger().error(f"Exception at {f}: {ex}")
            raise NATAppDbException(ex)

    return catch_db_error_wrap


#session utilities
class FlaskDBSessionInterface:  #simulate previous sqlalchemy version
    def __getattr__(self, name):  #forward methods to flask app.db.session
        from flask import current_app as app
        if hasattr(app.db.session, name):
            return getattr(app.db.session, name)


class Connection:
    def __init__(self, uri):
        self._engine = create_engine(uri)
        self._connection = self._engine.connect()
        self._sessionmaker = sessionmaker(bind=self._engine, autoflush=False, autocommit=False)

    def new_session(self):
        return scoped_session(self._sessionmaker)

    def close(self):
        self._connection.close()


class AutoSession:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        self._session = self._conn.new_session()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
        return False


#db consistency
def check_column_compatibility(table, dbcol, modelcol):
    logger = logging.getLogger()
    errors = False
    #logger.debug(f"Column type check for `{table}.{modelcol.key}` (db:{dbcol['type']} model:{modelcol.type})")
    if dbcol['type'] != modelcol.__dict__['type']:
        #practical check rules, convert the string representation of column types (db and schema) to compare them each other
        dbcoltype = str(dbcol['type'])
        modelcoltype = str(modelcol.type)
        if dbcoltype.startswith("VARCHAR"):
            dbcoltype = dbcoltype.split()[0]
        if dbcoltype.startswith("TEXT"):
            dbcoltype = dbcoltype.split()[0]
        elif dbcoltype.startswith("INTEGER"):
            i = dbcoltype.find("(")
            if i >= 0:
                dbcoltype = dbcoltype[:i]
        elif dbcoltype.startswith("SMALLINT"):
            i = dbcoltype.find("(")
            if i >= 0:
                dbcoltype = dbcoltype[:i]
        elif dbcoltype.startswith("BIGINT"):
            i = dbcoltype.find("(")
            if i >= 0:
                dbcoltype = dbcoltype[:i]
        elif dbcoltype.startswith("ENUM"):  # ENUM check
            if repr(modelcol.type).startswith("Enum("):
                dbcoltype = "Enum(%s)" % dbcol['type'].enums
                modelcoltype = "Enum(%s)" % modelcol.type.enums
            else:
                modelcoltype = repr(modelcol.type)
        elif dbcoltype == "TINYINT(1)" and modelcoltype == "BOOLEAN":
            dbcoltype = "BOOLEAN"
        elif repr(dbcol['type']).replace("DATETIME(", "TimestampMS(") == repr(modelcol.type):
            dbcoltype = modelcoltype
        # and the compare
        if dbcoltype != modelcoltype:
            logger.error(
                f"Column type not compatible for column `{table}.{modelcol.key}` (db:{repr(dbcol['type'])} model:{repr(modelcol.type)})"
            )
            errors = True
    if dbcol['nullable'] != modelcol.nullable:
        logger.error(
            f"Column nullable definition different for column `{table}.{modelcol.key}` (db:{dbcol['nullable']} model:{modelcol.nullable})"
        )
        errors = True

    return errors


def is_sane_database(Base, session):
    """Check whether the current database matches the models declared in model base.

    Currently we check that all tables exist with all columns. What is not checked

    * Column types are not verified

    * Relationships are not verified at all (TODO)

    :param Base: Declarative Base for SQLAlchemy models to check

    :param session: SQLAlchemy session bound to an engine

    :return: True if all declared models have corresponding tables and columns.
    """

    logger = logging.getLogger()
    engine = session.get_bind()
    iengine = inspect(engine)

    errors = False

    #check db/schema charset and collation params
    #MYSQL specific db check
    r = session.execute("SELECT @@character_set_database, @@collation_database").fetchall()
    #logger.debug(f"DB Schema charset/collation {r}")
    if r[0][0].upper() != "UTF8MB4":
        logger.error(f"DB/Schema charset is not utf8mb4 ({r[0][0]})")
        errors = True
    elif r[0][1].upper() != "UTF8MB4_UNICODE_CI":
        logger.error(f"DB/Schema collation is not utf8mb4_unicode_ci ({r[0][1]})")
        errors = True

    tables = iengine.get_table_names()

    # Go through all SQLAlchemy models
    for name, klass in Base._decl_class_registry.items():
        if isinstance(klass, _ModuleMarker):
            # Not a model
            continue

        table = klass.__tablename__
        if table in tables:
            #check table charset and collation
            #MYSQL specific db check
            r = session.execute(
                f"SELECT CCSA.character_set_name, TABLE_COLLATION FROM information_schema.`TABLES` T, information_schema.`COLLATION_CHARACTER_SET_APPLICABILITY` CCSA WHERE CCSA.collation_name = T.table_collation AND T.table_schema = database() AND T.table_name = '{table}'"
            ).fetchall()
            #logger.debug(f"Table {table} charset/collation {r}")
            if r[0][0].upper() != "UTF8MB4":
                logger.error(f"Table {table} charset is not utf8mb4 ({r[0][0]})")
                errors = True
            elif r[0][1].upper() != "UTF8MB4_UNICODE_CI":
                logger.error(f"Table {table} collation is not utf8mb4_unicode_ci ({r[0][1]})")
                errors = True

            # Check all columns are found
            # Looks like [{'default': "nextval('sanity_check_test_id_seq'::regclass)", 'autoincrement': True, 'nullable': False, 'type': INTEGER(), 'name': 'id'}]
            columns = [c["name"] for c in iengine.get_columns(table)]
            coldescs = {c["name"]: c for c in iengine.get_columns(table)}
            mapper = inspect(klass)
            dbcolumns = dict()
            for column_prop in mapper.attrs:
                if isinstance(column_prop, RelationshipProperty):
                    # TODO: Add sanity checks for relations
                    pass
                else:
                    for column in column_prop.columns:
                        dbcolumns[column.key] = column
                        # Assume normal flat column
                        if not column.key in columns:
                            logger.error("Model `%s` declares column `%s` which does not exist in database %s",
                                         klass.__name__, column.key, engine)
                            errors = True
                        else:  #schema column exists in db
                            #check table column charset and collation params
                            #MYSQL specific db check
                            r = session.execute(
                                f"select CHARACTER_SET_NAME, COLLATION_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table}' AND COLUMN_NAME='{column.key}' AND TABLE_SCHEMA=database()"
                            ).fetchall()
                            if r[0][0] is not None and r[0][1] is not None:
                                #logger.debug(f"Table column {table}.{column.key} charset/collation {r}")
                                if r[0][0].upper() != "UTF8MB4":
                                    logger.error(f"Table column {table}.{column.key} is not utf8mb4 ({r[0][0]})")
                                    errors = True
                                elif r[0][1].upper() != "UTF8MB4_UNICODE_CI":
                                    logger.error(
                                        f"Table column {table}.{column.key} collation is not utf8mb4_unicode_ci ({r[0][1]})"
                                    )
                                    errors = True

                            if check_column_compatibility(table, coldescs[column.key], column):
                                errors = True
            for column in columns:
                if column not in dbcolumns.keys():
                    logger.error("Column `%s` which exists in database %s does not declared in Model `%s`", column,
                                 engine, klass.__name__)
                    errors = True
        else:
            logger.error("Model `%s` declares table `%s` which does not exist in database %s", klass.__name__, table,
                         engine)
            errors = True

    return not errors


def check_version(app):
    version = migrate.versioning.api.version("db-migration/nat_repository")
    db_version = migrate.versioning.api.db_version(app.config['SQLALCHEMY_DATABASE_URI'], "db-migration/nat_repository")
    if version != db_version:
        app.logger.error(
            f"DB migration version is wrong. Migration repo version={version}, DB version={db_version}. Exiting...")
        return False
    return True


def check(session_param):
    return is_sane_database(Model, session_param)


session = FlaskDBSessionInterface()
