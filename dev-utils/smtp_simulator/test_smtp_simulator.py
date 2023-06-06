#!/usr/bin/env python3

import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# The HTML body of the email.
LOSTPWD_BODY_HTML = """<html>
<head></head>
<body>
<p>Confirm Your Registration</p>
<hr />
<p>Welcome!</p>
<p>Click the link below to complete verification:</p>
<table style="margin-top: 12px; margin-bottom: 12px; height: 45px; width: 138px;" border="0" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td style="width: 142px;">
<table style="height: 48px;" border="0" width="136" cellspacing="0" cellpadding="0">
<tbody>
<tr>
<td style="border-radius: 3px; width: 132px;" align=""><a class="btn" style="display: inline-block; color: #fff; font-weight: 400; border-left: 15px solid; border-right: 15px solid; border-top: 12px solid; border-bottom: 12px solid; font-size: 17px; text-decoration: none; text-align: center; -webkit-text-size-adjust: none; -webkit-border-radius: 3px; -moz-border-radius: 3px; border-radius: 3px; font-family: 'Benton Sans', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica neue', Helvetica, Tahoma, Arial, sans-serif; background-color: #95c11f; border-color: #95c11f;" href="
            """

LOSTPWD_BODY_HTML2 = """
" target="_blank" rel="noopener"><span style="padding-left: 5px; padding-right: 5px;">Verify Email</span></a></td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<p>This email was sent to 
            """
LOSTPWD_BODY_HTML3 = """            <br />
 <br />All rights reserved.</p></body>
</html>
            """

msg = MIMEMultipart('alternative')
msg['Subject'] = "Password Reset Request"
msg['From'] = email.utils.formataddr(("Sender", "me@me.me"))
msg['To'] = "local.user@local.test"

_s = LOSTPWD_BODY_HTML + 'http://localhost:8080/express/ui/v0.1' + '/1234' + LOSTPWD_BODY_HTML2 + "local.user@local.test" + LOSTPWD_BODY_HTML3
part2 = MIMEText(_s, 'html')

msg.attach(part2)
msg.add_header('Content-Type', 'text/html')

try:
    smtpObj = smtplib.SMTP('localhost', 1025)
    smtpObj.set_debuglevel(1)
    smtpObj.sendmail(msg['From'], msg['To'], msg.as_string())
    print("Successfully sent email")
except Exception:
    print("Error: unable to send email")
finally:
    smtpObj.quit()
