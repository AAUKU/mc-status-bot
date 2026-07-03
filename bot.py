import os
import asyncio
import socket

from telegram import Bot
from mcstatus import BedrockServer
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

bot = Bot(token=BOT_TOKEN)

last_status = None
last_players = 0
