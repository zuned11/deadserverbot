import asyncio
import logging

import discord
from dotenv import load_dotenv

load_dotenv()


logs = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guild_message = True

bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)


class ClientConnection(discord.Client):
    #suppresses errors on User attr being None
    user: discord.ClientUser

    async def on_ready(self):
        logs.info(f'Logged on as {self.user} (ID: {self.user.id})')
        logs.info('------')

    async def on_message(self, message):
        logs.info(f'received message: {message}')
        if message.author == self.user:
            return #ignore messages sent by ourselves :)

        if message.content == 'ping':
            logs.info(message.channel)
            #await message.channel.send('pong')
            await self.send_message_to_channel('pong', message.channel)

        #if message is !server prefix:
            #!server status

    async def send_message_to_channel(self, message: str, channel: discord.TextChannel):
        logs.info(f"sending message {message} to {channel}")
        async with channel.typing():
            await asyncio.sleep(1)
            await channel.send(message)

def get_connection_from_env() -> ClientConnection:
    return ClientConnection(intents=intents)
