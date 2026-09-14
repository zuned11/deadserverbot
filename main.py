import json
import logging
import os
import pathlib
from logging.config import dictConfig

from dotenv import load_dotenv

import app.discordClient as ds

load_dotenv()
logs = logging.getLogger('vikings')

token = os.getenv("DISCORD_TOKEN")

def start_logging():
    # RotatingFileHandler opens its file eagerly; the dir must exist first.
    pathlib.Path('logs').mkdir(exist_ok=True)
    config_file = pathlib.Path('config_log.json')
    with open(config_file) as f_in:
        config = json.load(f_in)
    dictConfig(config)

def main():
    start_logging()
    #initiate discord api
    intents = ds.discord.Intents.none()
    intents.message_content = True
    intents.guild_messages = True

    client = ds.get_connection_from_env()
    client.run(token)
    #initiate hetzner connection

    #initiate game manager

if __name__ == "__main__":
    main()
