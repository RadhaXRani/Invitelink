import os
import logging
import json
import time
import threading
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load Configurations
with open("config.json", "r") as f:
    DATA = json.load(f)

def getenv(var):
    return os.environ.get(var) or DATA.get(var, None)

# Environment Variables
bot_token = getenv("TOKEN")
api_hash = getenv("HASH")
api_id = getenv("ID")

# Validate Environment Variables
if not bot_token or not api_hash or not api_id:
    logging.error("❌ Missing TOKEN, HASH, or ID in environment variables or config.json.")
    exit(1)

# Initialize Clients
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
ss = getenv("STRING")
acc = None
if ss:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()

# Progress Writer
def progress(current, total, message, type):
    with open(f"{message.id}_{type}_status.txt", "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# Download & Upload Status
def status_checker(statusfile, message, status_type):
    while not os.path.exists(statusfile):
        time.sleep(1)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as status_read:
            txt = status_read.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__{status_type}__: **{txt}**")
            time.sleep(5)
        except:
            time.sleep(5)

# Start Command
@bot.on_message(filters.command(["start"]))
def send_start(client, message):
    bot.send_message(
        message.chat.id,
        f"👋 Hi {message.from_user.mention}, I am Save Restricted Bot!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]
        ),
        reply_to_message_id=message.id,
    )

# Handle Links & Messages
@bot.on_message(filters.text)
def save(client, message):
    logging.info(f"Received message: {message.text}")

    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        if acc is None:
            bot.send_message(message.chat.id, "❌ **String Session is not Set**", reply_to_message_id=message.id)
            return

        try:
            acc.join_chat(message.text)
            bot.send_message(message.chat.id, "✅ **Chat Joined Successfully**", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "⚠️ **Already in the Chat**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "❌ **Invalid Link**", reply_to_message_id=message.id)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ **Error:** {e}", reply_to_message_id=message.id)
    
    elif "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        toID = int(temp[1].strip()) if len(temp) > 1 else fromID

        for msgid in range(fromID, toID + 1):
            username = datas[3] if "https://t.me/c/" not in message.text else int("-100" + datas[4])

            try:
                msg = bot.get_messages(username, msgid)
                bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
            except UsernameNotOccupied:
                bot.send_message(message.chat.id, "❌ **Username Not Found**", reply_to_message_id=message.id)
            except:
                if acc is None:
                    bot.send_message(message.chat.id, "❌ **String Session is not Set**", reply_to_message_id=message.id)
                    return
                handle_private(message, username, msgid)
            
            time.sleep(2)

# Handle Private Chats
def handle_private(message, chatid, msgid):
    msg = acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)

    if msg_type == "Text":
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = bot.send_message(message.chat.id, "📥 **Downloading...**", reply_to_message_id=message.id)
    status_thread = threading.Thread(target=status_checker, args=(f"{message.id}_down_status.txt", smsg, "Downloaded"), daemon=True)
    status_thread.start()

    file = acc.download_media(msg, progress=progress, progress_args=[message, "down"])
    os.remove(f"{message.id}_down_status.txt")

    up_status_thread = threading.Thread(target=status_checker, args=(f"{message.id}_up_status.txt", smsg, "Uploaded"), daemon=True)
    up_status_thread.start()

    bot.send_document(message.chat.id, file, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
    
    os.remove(file)
    os.remove(f"{message.id}_up_status.txt")
    bot.delete_messages(message.chat.id, [smsg.id])

# Get Message Type
def get_message_type(msg):
    try: return "Document" if msg.document else None
    except: pass
    try: return "Video" if msg.video else None
    except: pass
    try: return "Animation" if msg.animation else None
    except: pass
    try: return "Sticker" if msg.sticker else None
    except: pass
    try: return "Voice" if msg.voice else None
    except: pass
    try: return "Audio" if msg.audio else None
    except: pass
    try: return "Photo" if msg.photo else None
    except: pass
    try: return "Text" if msg.text else None
    except: pass

logging.info("🚀 Bot is running...")
bot.run()
