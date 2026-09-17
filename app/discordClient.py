import asyncio
import logging
import logging.handlers

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logs = logging.getLogger(__name__)

description = """
This bot provides basic functions to stand up and interact with a server running a game.
"""

logs.debug("initializing intents")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
logs.debug('initializing bot commands')
bot = commands.bot(command_prefix="!", description=description, intents=intents)


@bot.event
async def on_ready(self):
    assert bot.user is not None
    logs.info(f"Logged on as {self.user} (ID: {self.user.id})")


async def on_message(self, message):
    logs.info(f"Received message: {message}")
    if message.author == self.user:
        return  # ignore messages sent by ourselves :)

    # message for testing recieve/sending messages
    if message.content == "ping":
        logs.info(message.channel)
        # await message.channel.send('pong')
        await self.send_message_to_channel("pong", message.channel)

    # if message is !server prefix:
    # ! server status


async def send_message_to_channel(self, message: str, channel: discord.TextChannel):
    logs.info(f"sending message {message} to {channel}")
    async with channel.typing():
        await asyncio.sleep(1)
        await channel.send(message)
