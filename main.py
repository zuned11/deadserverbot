import json
import logging
import os
import pathlib

from dotenv import load_dotenv

import app.discordClient as ds

load_dotenv()
logs = logging.getLogger('vikings')

token = os.getenv("DISCORD_TOKEN")

def start_logging():
    config_file = pathlib.Path('config_log.json')
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)

def main():

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
