import time
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from config import OWNER_ID, SUPPORT_GRP
from nexichat import _boot_, get_readable_time
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users
from nexichat.database.chatbot import get_user_nickname

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    bot_id = (await cli.get_me()).id
    users = len(await get_served_users(bot_id))
    chats = len(await get_served_chats(bot_id))
    
    await message.reply_text(
        f"""{(await cli.get_me()).mention} Reaction Bot Stats:

➻ **Chats:** {chats}
➻ **Users:** {users}"""
    )


@Client.on_message(filters.command("id"))
async def getid(client: Client, message: Message):
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )


@Client.on_message(filters.command(["profile", "me"]))
async def user_profile(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    
    uptime = get_readable_time(time.time() - _boot_)
    is_owner = (user.id == int(OWNER_ID))
    role = "👑 ᴏᴡɴᴇʀ / ʙᴏss" if is_owner else "💎 ᴠɪᴘ ᴍᴇᴍʙᴇʀ"
    
    nickname = await get_user_nickname(user.id)
    nick_str = f"│ ✦ **ɴɪᴄᴋɴᴀᴍᴇ :** `{nickname}`\n" if nickname else ""
    
    text = f"""**
╭━━━━━〔 👑 ᴜsᴇʀ ᴠɪᴘ ᴘʀᴏғɪʟᴇ 👑 〕━━━━━╮

  🌸 **ʜᴇʟʟᴏ {user.mention}!**
  ʜᴇʀᴇ ɪs ʏᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴠɪᴘ ᴘʀᴏғɪʟᴇ ᴄᴀʀᴅ.

╭────────────────────────────────╮
│ ✦ **ɴᴀᴍᴇ :** {user.first_name}
│ ✦ **ᴜsᴇʀ ɪᴅ :** `{user.id}`
│ ✦ **ᴜsᴇʀɴᴀᴍᴇ :** @{user.username if user.username else 'None'}
{nick_str}│ ✦ **sᴛᴀᴛᴜs :** {role}
│ ✦ **ᴅᴄ ɪᴅ :** `{user.dc_id or 'Unknown'}`
│ ✦ **ʙᴏᴛ ᴜᴘᴛɪᴍᴇ :** `{uptime}`
╰────────────────────────────────╯

📡 **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :** [ᴀᴍʀɪᴛ ғᴇᴇʟ](https://t.me/{SUPPORT_GRP}) 💞**
"""
    await message.reply_text(text, disable_web_page_preview=True)
