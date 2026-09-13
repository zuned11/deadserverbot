import logging
import os

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

def main():
    log_level = logging.INFO
    if os.getenv('LOGGING_LEVEL') == 'debug':
        log_level = logging.DEBUG
    logging.basicConfig(filename='../logs/app.log', level=log_level)

    #initiate discord api

    #initiate hetzner connection

    #initiate game manager

if __name__ == "__main__":
    main()
