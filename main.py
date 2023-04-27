import logging
from mailer import Mailer
from fetcher import Fetcher
from endpoints import news_events_endpoint
from mylogging import log_setup

#set up logging configuration
log_setup()
logger = logging.getLogger(__name__)


def main():
    fetch = Fetcher()

    response = fetch.fetch_forms(news_events_endpoint)
    contents = fetch.response_hanlder(response, news_events_endpoint)
    if contents:
        body = ''
        for content in contents:
            title, download_fileUrl, formatted_date, endpoint_name = content
            body += f'\n{title} - {formatted_date}\nDownload PDF:\n{download_fileUrl}\n'

        content = f'[{endpoint_name} Notice]\n{body}\nThanks,\nAshish Bot'.encode(
            'utf-8')

        mailbot = Mailer()

        result = mailbot.send_email(title=contents[0][0], content=content)

        # logs in case result is not empty, for any errors
        if result:
            logger.error(result)

    logger.info('==== Check completed ====')


if __name__ == '__main__':

    logger.info('==== Program starting ====')

    # Calling main function
    main()
    logger.info('==== Execution finished ====')
