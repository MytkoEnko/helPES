import os
import base64
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (Mail, Attachment, FileContent, FileName, FileType, Disposition)

def send_mail(date=datetime.utcnow(),file_path = 'shot/screen_to_mail.png'):

    message = Mail(
        from_email='pes-python@dmytro.pl',
        to_emails='deass@ukr.net',
        subject='PES script hang mail ' + str(date),
        html_content='<strong>and easy to do anywhere, even with Python</strong> <img src="cid:my_content_id"></img>')

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
        sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sendgrid_client.send(message)
        print(response.status_code,response.body,response.headers)
    except Exception as e:
        print(e.message)
