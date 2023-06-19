import smtplib
import ssl
from email.header import Header
from email.utils import formataddr, formatdate, COMMASPACE
from email.mime.text import MIMEText
import os

import logging
from mylogging import log_setup

# set up logging configuration
log_setup()
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError as ie:
    logger.warning(ie)
    print("could not load dotenv")
else:
    load_dotenv()

RECIPIENT_FILENAME = 'recipients.txt'
DEV_EMAIL = 'ashishkandu43@gmail.com'
SENDER_NAME = 'Ashish Bot'


class Mailer:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 587
        self.recipients = self.get_recipients()
        self.email: str = os.getenv('SENDER_EMAIL')
        self.password: str = os.getenv('PASSWORD')
        logger.debug("Email and password setting complete")

    def get_recipients(self):
        """
        Returns a list of recipients found in the environment it returns self.email 
        if could not find the key.
        """
        try:
            recipients:list[str] = os.environ['RECIPIENTS'].split(',')
        except KeyError as key_error:
            logger.error(f'recipients not found in env! {key_error}')
            recipients = [self.email, ]
        return recipients

    def send_email(self, title: str, content: str):
        """sends email to the to_email and returns dict if error occurs"""
        context = ssl.create_default_context()
        msg = MIMEText(content, _charset='utf-8')
        msg['From'] = formataddr((str(Header(SENDER_NAME, 'utf-8')), self.email))
        msg['Date'] = formatdate(localtime=True)
        msg['To'] = COMMASPACE.join(self.recipients)
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
