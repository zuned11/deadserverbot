import logging
import os

import discord
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='../logs/discord.log', encoding='utf-8', mode='a')

#bot = commands.Bot(command_prefix='?', intents=intents)


class ClientConnection(discord.Client):
    #suppresses errors on User attr being None
    user: discord.ClientUser

    async def on_ready(self):
        print(f'Logged on as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        print(f'received message: {message}')
        if message.author == self.user:
            return #ignore messages sent by ourselves :)

        if message.content == 'ping':
            await message.channel.send('pong')


intents = discord.Intents.none()
intents.message_content = True
intents.guild_messages = True

client = ClientConnection(intents=intents)
client.run(token)
