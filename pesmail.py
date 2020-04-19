import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)
from secrets import sendgrid_api_key

def send_mail(date=datetime.utcnow(),file_path = 'shot/screen_to_mail.png'):

    with open("pes-f.log", 'r') as f:
        data = f.readlines()
    tail = data[-30:]
    body = ''
    for i in tail:
        body += i + "<br>"

    message = Mail(
        from_email='pes-python@dmytro.pl',
        to_emails='dmytro.aleksieiev@gmail.com',
        subject='PES script hang mail ' + str(date),
        html_content=f'<strong>Last 30 lines of pes-f.log</strong> <br> {body} <br> <img src="cid:my_content_id"></img>')

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
    except Exception as e:
        print(e.message)
