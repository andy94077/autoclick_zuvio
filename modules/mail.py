from getpass import getpass
import os
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Literal, Union

from dotenv import load_dotenv

load_dotenv()


class Mail():
    SERVER = {'ntu': 'mail.ntu.edu.tw', 'gmail': 'smtp.gmail.com', 'other': 'xxx'}

    def __init__(self, sender: str, receiver: str, mail_server_type: Literal['ntu', 'gmail', 'other', None] = None, mail_server: Union[str, None] = None, port: str = '587'):
        self.sender = sender
        self.receiver = receiver
        self.subject = 'Auto click on Zuvio: signed in class {class_no}'
        if mail_server_type is None:
            if re.match('.+@ntu\.edu\.tw$', sender):
                mail_server_type = 'ntu'
            elif re.match('.+gmail\.com$', sender) or re.match('.+@g.ntu.edu.tw$', sender):
                mail_server_type = 'gmail'
            else:
                print('Error! The mail server cannot be found automatically.')
                exit()

        assert mail_server_type in self.SERVER
        self.server = mail_server if mail_server is not None else self.SERVER[mail_server_type]
        self.port = port
        if mail_server_type == 'ntu':
            if int(sender[1:3]) >= 9:
                print('Error! Only the old ntumail (<= 108) is supported.')
                exit()
            self.token = getpass(f'Enter the password of {sender}: ')
            print('INFO: Your password will only be used during this exection and not be stored anywhere.')
        else:
            self.token = os.getenv('MAIL_TOKEN')

    def __call__(self, logger: Dict[str, Any]) -> None:
        content = MIMEMultipart()
        content['from'] = self.sender
        content['to'] = self.receiver
        content['subject'] = self.subject.format(class_no=logger['class_no'])
        content.attach(MIMEText(f"[{logger['time']}] User {logger['user']} signed in class {logger['class_no']}"))

        with smtplib.SMTP(host=self.server, port=self.port) as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.sender, self.token)
                smtp.send_message(content)
                print(f'[{ time.strftime("%H:%M:%S", time.localtime())}] Message is sent to {self.receiver}!')
            except Exception as e:
                print(f'Error on sending mail. Please try another one. Error message: {e}')


if __name__ == '__main__':
    # mail = 'r10922066@g.ntu.edu.tw'
    mail = 'b06902001@ntu.edu.tw'
    bot = Mail(mail, 'b06902001@ntu.edu.tw')
    bot(dict(class_no=12345, time=time.strftime("%H:%M:%S", time.localtime()), user='r10922066'))
