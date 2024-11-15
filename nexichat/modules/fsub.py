from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, ChatWriteForbidden, ChatAdminRequired
from pymongo import MongoClient
from nexichat import nexichat as app, mongo
import asyncio
from config import OWNER_ID

db = mongo['bot_database']
collection = db['must_join_channel']

MUST_JOIN = collection.find_one({"_id": "must_join_channel"})['channel_id'] if collection.find_one({"_id": "must_join_channel"}) else None

@app.on_message(filters.command("setfsub") & filters.user(int(OWNER_ID)))
async def set_channel(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /setfsub <channel_username/channel_id>")
    
    channel = message.command[1]
    
    if channel.startswith('@'): 
        link = f"https://t.me/{channel.lstrip('@')}"
    elif channel.isdigit(): 
        link = f"https://t.me/c/{channel}"
    else:
        return await message.reply_text("Invalid channel. Please provide a valid channel username or channel ID.")

    try:
        chat_info = await client.get_chat(channel)
        
        
        bot_member = await client.get_chat_member(channel, client.me.id)
        if not bot_member.can_invite_users:
            return await message.reply_text(f"Please promote me to admin in {channel} with 'Invite to Group via Link' permissions.")
        
        
        collection.update_one(
            {"_id": "must_join_channel"},
            {"$set": {"channel_id": channel}},
            upsert=True
        )
        await message.reply_text(f"Force subscription channel has been set to: {channel}. Link: {link}")

    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@app.on_message(filters.incoming & filters.private)
async def must_join_channel(app: Client, msg: Message):
    if MUST_JOIN:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if MUST_JOIN.isalpha():
                link = f"https://t.me/{MUST_JOIN}"
            else:
                chat_info = await app.get_chat(MUST_JOIN)
                link = chat_info.invite_link

            try:
                photo="https://envs.sh/Tn_.jpg",
            caption=(f"**👋 ʜᴇʟʟᴏ {message.from_user.mention},**\n\n**ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({link}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=link)]]))
        
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    else:
        await msg.reply_text("Force subscription is disabled, you can use the bot without joining any channel.")