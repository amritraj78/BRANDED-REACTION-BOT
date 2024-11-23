from pyrogram import Client, filters
from pyrogram.types import Message
from nexichat import nexichat

@Client.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    await message.reply_text(
        f"ʜᴇʟʟᴏ {message.from_user.first_name}! 👋\n\n"
        "ɪ'ᴍ ʏᴏᴜʀ ʀᴇᴀᴄᴛɪᴏɴ ʙᴏᴛ! ɪ'ʟʟ ʀᴇᴀᴄᴛ ᴛᴏ ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ ɪɴ ɢʀᴏᴜᴘs, ᴄʜᴀɴɴᴇʟs, ᴀɴᴅ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛs ᴡɪᴛʜ ᴀ 👍 ᴇᴍᴏᴊɪ.\n\n"
        "ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴡᴀᴛᴄʜ ᴍᴇ ɪɴ ᴀᴄᴛɪᴏɴ! 🚀\n\n"
        "**ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ʏᴏᴜʀ ʙᴏᴛ ʙʏ /clone😁**"
    )
