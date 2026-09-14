import os

from dotenv import load_dotenv
from hcloud import Client, ServerType

load_dotenv()

CLIENT_TOKEN = os.getenv("HETZNER_CLIENT_TOKEN")

client = Client(
        token=CLIENT_TOKEN,
        application_name="valheimers",
        application_version="v1.0.0",
        )

TARGET_SERVER_TYPE = os.getenv("TARGET_SERVER_TYPE") or ServerType(name="cx23")
#SSH_KEYS = client

def get_server_instances():
        return client.servers.get_all()

def create_server():
        response = client.servers.create(
                        name = 'valheim',
                       server_type=TARGET_SERVER_TYPE,
ssh_keys=client.ssh_keys.get_all(),
)

