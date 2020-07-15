import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)


def send_mail(date=datetime.utcnow(),file_path = 'shot/screen_to_mail.png', sendgrid_api_key='',to_email='', alt_content='',alt_subject=''):

    try:
        with open("helPES.log", 'r') as f:
            data = f.readlines()
        tail = data[-30:]
        body = ''
        for i in tail:
            body += i + "<br>"
    except:
        body = "Could not read logs"

    message = Mail(
        from_email='pes-python@dmytro.pl',
        to_emails=to_email,
        subject=alt_subject + " " + str(date) if alt_subject else 'helPES script hang mail ' + str(date),
        html_content=alt_content + '<br> <img src="cid:my_content_id"></img>' if alt_content else f'<strong>Last 30 lines of helPES.log</strong> <br> {body} <br> <img src="cid:my_content_id"></img>')

    with open(file_path, 'rb') as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment(
        FileContent(encoded),
        FileName('pes_screen_capture.png'),
        FileType('image/png'),
        Disposition('inline'), #inline, attachment
        content_id='my_content_id'
    )
    message.attachment = attachment
    try:
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        response = sendgrid_client.send(message)
        print(response.status_code,response.body,response.headers)
        return response.status_code
    except Exception as e:
        return 500
