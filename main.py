import logging
from mailer import Mailer
from fetcher import Fetcher
from endpoints import news_events_endpoint, trial_forms_endpoint, written_forms_endpoint
from mylogging import log_setup

#set up logging configuration
log_setup()
logger = logging.getLogger(__name__)

endpoints_to_check = (news_events_endpoint, trial_forms_endpoint, written_forms_endpoint)

def main():
    fetch = Fetcher()

    for endpoint_toc_check in endpoints_to_check:
        response = fetch.fetch_forms(endpoint_toc_check)
        contents = fetch.response_hanlder(response, endpoint_toc_check)
        if contents:
            body = ''
            if len(contents) == 5:
                body += '\nLatest feeds:\n'
            for content in contents:
                title, download_fileUrl, formatted_date, endpoint_name = content
                body += f'\n{title} - {formatted_date}\nDownload PDF:\n{download_fileUrl}\n'

            content = f'[{endpoint_name} notice]\n{body}\nThanks,\nAshish Bot'.encode(
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
