import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText
import json

import logging
from mylogging import log_setup
from myexceptions import FileEmptyException

# set up logging configuration
log_setup()
logger = logging.getLogger(__name__)

RECIPIENT_FILENAME = 'recipients.txt'
DEV_EMAIL = 'ashishkandu43@gmail.com'


class Mailer:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 587
        self.recipients = self.get_recipients()
        try:
            with open('credentials.json') as file:
                data: dict = json.load(file)
        except FileNotFoundError:
            open('credentials.json', 'w').close()
            raise SystemExit("Save your credentials on credentials.json file")
        else:
            self.email: str = data.get('email')
            self.password: str = data.get('password')
            logger.debug("Email and password setting complete")

    def get_recipients(self):
        try:
            with open(RECIPIENT_FILENAME) as file:
                recipients: list = file.readlines()
                if not recipients:
                    recipients = [DEV_EMAIL]
                    raise FileEmptyException
        except (FileNotFoundError, FileEmptyException):
            with open(RECIPIENT_FILENAME, 'w') as file:
                file.write(DEV_EMAIL)
        return recipients

    def send_email(self, title: str, content: str):
        """sends email to the to_email and returns dict if error occurs"""
        context = ssl.create_default_context()
        msg = MIMEText(content, _charset='utf-8')
        msg['From'] = self.email
        msg['To'] = ", ".join(self.recipients)
        msg['Subject'] = Header(title, 'utf-8')
        msg.set_payload(content)

        logger.info("Initiating mail connection...")

        # Establishing connection
        connection = smtplib.SMTP(host=self.host, port=self.port, timeout=10)
        connection.set_debuglevel(0)  # Debugging off
        logger.info("SMTP connection establsihed")

        connection.starttls(context=context)
        logger.info("SMTP connection secured")

        # Try establishing connection and send email
        try:
            result = connection.login(user=self.email, password=self.password)
            logger.debug(result)

            response = connection.sendmail(
                from_addr=self.email, to_addrs=self.recipients, msg=msg.as_string())
            logger.info("Mail sent")
        except Exception as e:
            logger.exception(e)
            response = {'error': e}

        finally:
            connection.close()
            logger.info('SMTP connection closed')
            return response
