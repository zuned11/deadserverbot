from dotenv import load_dotenv

load_dotenv()

import logging

log = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='../logs/app.log', level=logging.INFO)

if __name__ == "__main__":
    main()
