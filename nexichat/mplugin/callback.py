import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL
from nexichat import nexichat, mongo
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery
import asyncio
import config
from nexichat import LOGGER, nexichat, db
from nexichat.modules.helpers import (
    ABOUT_BTN,
    ABOUT_READ,
    ADMIN_READ,
    BACK,
    CHATBOT_BACK,
    CHATBOT_READ,
    AI_CHATBOT_READ,
    DEV_OP,
    HELP_BTN,
    HELP_READ,
    HELP_GAMES_READ,
    HELP_GROUP_READ,
    MUSIC_BACK_BTN,
    START,
    TOOLS_DATA_READ,
    
)


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    if data == "HELP":
        await query.message.edit_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "CLOSE":
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.answer("Closed menu! 🌸", show_alert=False)
    elif data in ["BACK", "SBACK"]:
        first_name = query.from_user.first_name if query.from_user else "Friend"
        bot_info = await client.get_me()
        bot_title = (bot_info.first_name or "VIP REACTION").upper()
        back_text = (
            f"╭━━━━━━━〔 ❖ **{bot_title}** ❖ 〕━━━━━━━╮\n\n"
            f"  🌸 **ʜᴇʏ {first_name}! ᴡᴇʟᴄᴏᴍᴇ ʙᴀʙʏ** 💖\n\n"
            f"  ɪ ᴀᴍ ʏᴏᴜʀ sᴍᴀʀᴛ **ᴀɪ ɢɪʀʟғʀɪᴇɴᴅ & ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛɪᴏɴ ʙᴏᴛ**! ✨\n"
            f"  ɪ ᴄʜᴀᴛ ᴡɪᴛʜ ʏᴏᴜ ʟɪᴋᴇ ᴀ sᴡᴇᴇᴛ ɢɪʀʟ, ʀᴇᴘʟʏ ᴛᴏ sᴛɪᴄᴋᴇʀs, \n"
            f"  ᴠᴏɪᴄᴇ ɴᴏᴛᴇs, ᴘʜᴏᴛᴏs, ᴠɪᴅᴇᴏs & ʀᴇᴀᴄᴛ ᴛᴏ ᴍᴇssᴀɢᴇs! ⚡\n\n"
            f"╭────────────────────────────────╮\n"
            f"│ ✦ **ᴘᴇʀsᴏɴᴀ** : sᴡᴇᴇᴛ ᴀɪ ɢɪʀʟ 🌸\n"
            f"│ ✦ **ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛ** : ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟs ⚡\n"
            f"│ ✦ **sᴍᴀʀᴛ ᴄʜᴀᴛ** : ᴛᴇxᴛ, sᴛɪᴄᴋᴇʀ, ᴠᴏɪᴄᴇ 🎙️\n"
            f"│ ✦ **ᴍᴇᴍᴏʀʏ** : sᴇʟғ-ʟᴇᴀʀɴɪɴɢ Q&A 🧠\n"
            f"│ ✦ **ᴄʀᴇᴀᴛᴏʀ** : [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns) 👑\n"
            f"╰────────────────────────────────╯\n\n"
            f"👇 **ᴛᴀᴘ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍᴏʀᴇ!**"
        )
        await query.message.edit_text(
            text=back_text,
            reply_markup=InlineKeyboardMarkup(DEV_OP),
            disable_web_page_preview=True
        )
        await query.answer()
    elif data == "ABOUT":
        await query.message.edit_text(
            text=ABOUT_READ,
            reply_markup=InlineKeyboardMarkup(ABOUT_BTN),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "ADMINS":
        await query.message.edit_text(
            text=ADMIN_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "HELP_GAMES":
        await query.message.edit_text(
            text=HELP_GAMES_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "HELP_GROUP":
        await query.message.edit_text(
            text=HELP_GROUP_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "TOOLS_DATA":
        await query.message.edit_text(
            text=TOOLS_DATA_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "BACK_HELP" or data == "CHATBOT_BACK":
        await query.message.edit_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "CHATBOT_CMD":
        await query.message.edit_text(
            text=CHATBOT_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "AI_CHATBOT_CMD":
        await query.message.edit_text(
            text=AI_CHATBOT_READ,
            reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            disable_web_page_preview=True,
        )
        await query.answer()
    elif data == "soon":
        await query.answer("🚀 This feature is coming soon in the next update! Stay tuned! 🌸", show_alert=True)
    else:
        query.continue_propagation()

    
    
