import os

from dotenv import load_dotenv
from hcloud import Client

load_dotenv()

CLIENT_TOKEN = os.getenv("HETZNER_CLIENT_TOKEN")

client = Client(
        token=CLIENT_TOKEN,
        application_name="valheimers",
        application_version="v1.0.0",
        )

