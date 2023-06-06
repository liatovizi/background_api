from natapp import db
from natapp.users import models as users_models


def add_maillog(session, user_id, template_id, parameters, status):
    newmail = users_models.Maillog(user_id=user_id, template_id=template_id, parameters=parameters, status=status)
    session.add(newmail)
    session.flush()
    return newmail.maillog_id


def get_user_maillog(session, user_id, page, per_page):
    maillog_records = session.query(users_models.Maillog).filter(users_models.Maillog.user_id == user_id).order_by(
        users_models.Maillog.sent.asc()).paginate(page=page, per_page=per_page, error_out=False)
    maillogs = []
    for r in maillog_records.items:
        maillogs.append({  #'maillog_id':r.maillog_id,
            'template_id': r.template_id,
            'parameters': r.parameters,
            'sent': r.sent,
            'status': r.status
        })
    return {
        'maillogs': {
            'pagination': {
                'page': page,
                'perPage': per_page,
                'total': maillog_records.total
            },
            'maillogs': maillogs
        }
    }
