from os.path import exists
from asyncio import get_event_loop
from pyrogram import Client
from logging import basicConfig, FileHandler, StreamHandler, getLogger, INFO, WARNING
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

basicConfig(
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        FileHandler("logs.txt"),
        StreamHandler()
    ],
    level=INFO
)

LOGGER = getLogger(__name__)
getLogger("pyrogram").setLevel(WARNING)

is_config = exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

mongo_client = MongoClient(MONGO_URL)
db = mongo_client.bot

ALLOWED_CHAT = SUDO_CHATS_ID

async def load_auth():
    global ALLOWED_CHAT
    sudoersdb = db.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    for user_id in ALLOWED_CHAT:
        if user_id not in sudoers:
            sudoers.append(user_id)
            await sudoersdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"sudoers": sudoers}},
                upsert=True,
            )
    ALLOWED_CHAT = (ALLOWED_CHAT + sudoers) if sudoers else ALLOWED_CHAT
    


loop = get_event_loop()
loop.run_until_complete(load_auth())

# Input Your Own ID or Hash if u want
app = Client(
    ":memory:", 
    bot_token=BOT_TOKEN, 
    api_id=API_ID,
    api_hash=API_HASH
)

app.start()