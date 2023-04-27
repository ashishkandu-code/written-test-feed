import requests
import logging
from datetime import datetime
import json
import smtplib
import ssl
from email.header import Header
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO,
                    format='(%(levelname)s) - %(asctime)s : %(message)s', datefmt='%b-%d %I:%M:%S %p',
                    filename='logs.log')

written_forms_endpoint = 'http://103.69.127.113:8080/notice-ws/api/v1/dotm/written-forms'
download_endpoint = 'http://103.69.127.113/uploads'

DEFAULT_VALUE = 1203  # Can be any random number (integer)
host = 'smtp.gmail.com'
port = 587

recipients = ['ashishkandu43@gmail.com', ]


def send_email(from_email: str, to_email: str, password: str, message: str):
    """sends email to the to_email and returns dict if error occurs"""
    context = ssl.create_default_context()
    logging.info("Initiating connection")

    # Establishing connection
    connection = smtplib.SMTP(host=host, port=port, timeout=10)
    connection.set_debuglevel(0)  # Debugging off
    logging.info("Connection establsihed")

    connection.starttls(context=context)
    logging.info("Connection secured")

    # Try establishing connection and send email
    try:
        result = connection.login(user=from_email, password=password)
        logging.debug(result)

        response = connection.sendmail(
            from_addr=from_email, to_addrs=to_email, msg=message)
        logging.info("Message sent")
    except Exception as e:
        logging.exception(e)
        response = {'error': e}

    finally:
        connection.close()
        logging.info('Connection closed')
        return response


def fetch_written_forms_response():

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8,ms-MY;q=0.7,ms;q=0.6,en-GB;q=0.5',
        'Connection': 'keep-alive',
        'Origin': 'http://tmolicense.lumbini.gov.np',
        'Referer': 'http://tmolicense.lumbini.gov.np/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    params = {
        'pageNo': '0',
        'pageSize': '10',
    }

    logging.info('Fetching written forms')
    response = requests.get(
        written_forms_endpoint,
        params=params,
        headers=headers,
        verify=False,
    )

    response.raise_for_status()

    try:
        latest_data_object: dict = response.json()['responseObject']['data'][0]
        latest_id: int = latest_data_object.get('id', None)
    except TypeError as te:
        logging.error(te)
    except KeyError as ke:
        logging.error(ke)
    else:
        # store_id = DEFAULT_VALUE # Default value is 1205
        try:
            with open('id.txt', 'r') as f:
                store_id = f.read()
                if store_id:
                    store_id = int(store_id)
                else:
                    store_id = DEFAULT_VALUE
                    logging.info('Using default stored id')
        except FileNotFoundError:
            logging.info('File not found; Using default stored id')
            store_id = DEFAULT_VALUE
        logging.info(f'Current cached id: {store_id}')
        if not latest_id == store_id:
            logging.info(f'New entry found! id: {latest_id}')
            title = latest_data_object['title']
            fileUrl = latest_data_object['fileUrl']
            createdDate = latest_data_object['createdDate']

            download_fileUrl = "/".join((download_endpoint, fileUrl))
            formatted_date = datetime.strptime(
                createdDate, '%Y-%m-%dT%H:%M:%S.%f').strftime('%b/%d %I:%M %p')

            return latest_id, formatted_date, title, download_fileUrl
        return None


def main():

    response_result = fetch_written_forms_response()
    if response_result:
        latest_id, formatted_date, title, download_fileUrl = response_result
        content = f'[Notice]\n{title}\n\nPublished date: {formatted_date}\n\nDownload PDF:\n{download_fileUrl}\n\nThanks,\nAshish Bot'.encode(
            'utf-8')

        # msg = Message()
        msg = MIMEText(content, _charset='utf-8')
        msg['From'] = email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = Header(title, 'utf-8')
        f"{formatted_date}"
        msg.set_payload(content)

        result = send_email(from_email=email, to_email=recipients,
                            password=password, message=msg.as_string())

        # logs in case result is not empty, for any errors
        if result:
            logging.error(result)
        else:
            with open('id.txt', 'w') as f:
                f.write(str(latest_id))
            logging.info('New ID write success!')

    logging.info('==== Check completed ====')


if __name__ == '__main__':

    logging.info('==== Program starting ====')
    try:
        with open('credentials.json') as file:
            data: dict = json.load(file)
            logging.debug("File loaded sucessfully!")
    except FileNotFoundError:
        open('credentials.json', 'w').close()
        raise SystemExit("Save your credentials on credentials.json file")
    else:
        email: str = data.get('email')
        password: str = data.get('password')
        logging.debug("Email and password setting complete")

    # Calling main function
    main()
    logging.info('==== Execution finished ====')
