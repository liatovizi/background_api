import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app as app
from flask import render_template_string

from natapp.libs.naterrors import Errors

import natapp.libs.natutility as utils
from natapp.libs.natemailtemplate import EmailTemplate
from natapp.users.db import user as users_user
from natapp.users.db import maillog


def email_sender(session, templ_id, parameters):
    if not templ_id:
        app.logger.error('SENDMAIL_missing_001 Missing template id')
        return Errors.SENDMAIL_missing_001

    if templ_id not in EmailTemplate.EMAIL_TEMPLATES:
        app.logger.error(f'SENDMAIL_invalid_001 Invalid template id: {templ_id}')
        return Errors.SENDMAIL_invalid_001

    if not parameters:
        app.logger.error('SENDMAIL_missing_003 Missing parameters for template')
        return Errors.SENDMAIL_missing_003

    current_template = EmailTemplate.EMAIL_TEMPLATES[templ_id]
    _len_of_curent_template = len(current_template['parameters'])
    _len_of_parameters = len(parameters)
    if _len_of_curent_template != _len_of_parameters:
        app.logger.error(
            f'SENDMAIL_invalid_002 Invalid number of parameters. {_len_of_parameters} is given, but {_len_of_curent_template} expected.'
        )
        return Errors.SENDMAIL_invalid_002

    if 'recipient' not in parameters:
        app.logger.error('SENDMAIL_missing_004 Missing recipient address')
        return Errors.SENDMAIL_missing_004

    _recpt = parameters['recipient']
    _user_id = int(parameters['customer_id'])

    if not utils.isValidEmail(_recpt):
        app.logger.error(f'SENDMAIL_invalid_003 Invalid recipient address: {_recpt}')
        return Errors.SENDMAIL_invalid_003

    c = users_user.get_users_by_email(_recpt)
    _lang = str(c[0]['language'])
    if _lang not in current_template:
        _lang = 'hu'

    _f = {}
    _f['subject'] = current_template[_lang].get('subject')
    for i in current_template['parameters']:
        if i not in parameters:
            app.logger.error(f'SENDMAIL_missing_005 Missing parameter: {i}')
            return Errors.SENDMAIL_missing_005
        _f[i] = parameters[i]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = current_template[_lang].get('subject')
    msg['From'] = email.utils.formataddr((app.config['SMTP_SENDERNAME'], app.config['SMTP_SENDER']))
    msg['To'] = _recpt

    templ_file = 'natapp/libs/email_templates/' + current_template[_lang].get('file_name')
    try:
        with open(templ_file, mode='r') as msg_template:
            msg_template_content = msg_template.read()
        _s = render_template_string(msg_template_content, **_f)
    except IOError as e:
        app.logger.error(f"SENDMAIL_error_001 Error in opening template file: {e}")
        return Errors.SENDMAIL_error_001

    #part1 = MIMEText(_t, 'plain')
    part2 = MIMEText(_s, 'html')

    #msg.attach(part1)
    msg.attach(part2)

    #####################
    # For test only config!!!!!!
    # SMTP_TESTMODE = 1
    # SMTP_HOST = 'localhost'
    # SMTP_PORT = 1025
    # SMTP_USER = 'somebody'
    # SMTP_PASSWORD = 'something'
    # SMTP_SENDER = 'info@natcoin.hu'
    #####################

    #####################
    # For production only config!!!!!!
    #SMTP_TESTMODE = 0
    #SMTP_HOST = 'TODO email server'
    #SMTP_PORT = 587
    #SMTP_USER = ''
    #SMTP_PASSWORD = ''
    #SMTP_SENDER = 'info@natcoin.hu'
    #####################
    if not app.config['SMTP_TESTMODE']:
        try:
            server = smtplib.SMTP(app.config['SMTP_HOST'], app.config['SMTP_PORT'])
            server.ehlo()
            server.starttls()
            # stmplib docs recommend calling ehlo() before & after starttls()
            server.ehlo()
            server.login(app.config['SMTP_USER'], app.config['SMTP_PASSWORD'])
            server.sendmail(app.config['SMTP_SENDER'], _recpt, msg.as_string())
            server.close()
        # Display an error message if something goes wrong.
        except Exception as e:
            maillog.add_maillog(session, _user_id, templ_id, str(parameters), 0)
            app.logger.error(f"Failed to send {templ_id}")
            app.logger.error(f"Error: {e}")
            return Errors.SENDMAIL_error_002
        else:
            maillog.add_maillog(session, _user_id, templ_id, str(parameters), 1)
            app.logger.info("Email sent!")
            app.logger.info(f"Successfully sent {templ_id}")
    else:
        try:
            server = smtplib.SMTP(app.config['SMTP_HOST'], app.config['SMTP_PORT'])
            server.set_debuglevel(1)
            server.sendmail(app.config['SMTP_SENDER'], _recpt, msg.as_string())
            server.close()
        # Display an error message if something goes wrong.
        except Exception as e:
            maillog.add_maillog(session, _user_id, templ_id, str(parameters), 0)
            app.logger.error(f"Failed to send {templ_id}")
            app.logger.error(f"Error: {e}")
            return Errors.SENDMAIL_error_002
        else:
            maillog.add_maillog(session, _user_id, templ_id, str(parameters), 1)
            app.logger.info("Email sent!")
            app.logger.info(f"Successfully sent {templ_id}")
