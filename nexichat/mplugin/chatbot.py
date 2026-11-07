# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin Chatbot Controller)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye AI Chatbot Controller hai. Cloned bots bhi sweet
  girl persona me baat karte hain, group conversations se learn karte hain,
  aur AI reply pehle dete hain.
================================================================================
"""

import os
import re
import random
import asyncio
import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery
)

from config import OWNER_ID
from nexichat import SUDOERS
from nexichat.database.chatbot import (
    is_chatbot_enabled,
    set_chatbot_enabled,
    save_chat_reply,
    save_sticker,
    get_random_sticker,
    save_user_nickname,
    get_user_nickname,
    format_api_usage_dashboard
)
from nexichat.mplugin.helpers.media_gen import generate_ai_image
from nexichat.database.clonestats import add_served_cuser, add_served_cchat
from nexichat.mplugin.helpers.ai import (
    generate_conversational_response,
    calculate_love,
    get_random_shayari,
    get_random_joke,
    is_abusive,
    get_abuse_refusal,
    get_voice_reply,
    get_photo_reply,
    get_video_reply,
    get_animation_reply
)

logger = logging.getLogger(__name__)

_message_counts = {}
_blocklist = {}


async def is_admin_or_sudo(client: Client, message: Message) -> bool:
    """Check if the sender is an admin or sudo."""
    if not message.from_user:
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            return True
        return False

    user_id = message.from_user.id
    if user_id in SUDOERS or user_id == int(OWNER_ID):
        return True

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return True
        except Exception:
            return False

    return False


@Client.on_message(filters.command(["chatbot", "chat"]))
async def chatbot_toggle_cmd(client: Client, message: Message):
    """
    Toggle or check chatbot status:
    /chatbot on -> Turn chatbot ON
    /chatbot off -> Turn chatbot OFF
    /chatbot -> Show interactive toggle menu
    """
    chat_id = message.chat.id

    if len(message.command) > 1:
        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            if not await is_admin_or_sudo(client, message):
                return await message.reply_text("❌ **Only administrators can change chatbot settings.**")

        action = message.command[1].lower()
        if action in ["on", "enable", "yes", "true"]:
            await set_chatbot_enabled(chat_id, True)
            return await message.reply_text("🤖 **AI Chatbot is now ENABLED for this chat!** 🌸\nMain ab yahan sabhi messages, stickers aur voice notes ka reply dungi ji! 🥰")
        elif action in ["off", "disable", "no", "false"]:
            await set_chatbot_enabled(chat_id, False)
            return await message.reply_text("🛑 **AI Chatbot is now DISABLED for this chat.** 😴")
        else:
            return await message.reply_text("ℹ️ **Usage:** `/chatbot on` or `/chatbot off`")

    enabled = await is_chatbot_enabled(chat_id)
    status_icon = "🟢 **ENABLED**" if enabled else "🔴 **DISABLED**"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Enable", callback_data="cb_enable_chatbot"),
            InlineKeyboardButton("🔴 Disable", callback_data="cb_disable_chatbot"),
        ],
        [
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])

    text = (
        f"╭━━━━━━━〔 🤖 **AI CHATBOT SETTINGS** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {message.chat.title or message.chat.first_name or 'This Chat'}\n"
        f"  ✦ **sᴛᴀᴛᴜs :** {status_icon}\n"
        f"  ✦ **ᴘᴇʀsᴏɴᴀ :** sᴡᴇᴇᴛ ᴀɪ ɢɪʀʟ 🌸\n\n"
        f"When enabled, I will reply to messages, questions, stickers, photos, and voice notes!\n\n"
        f"**Quick Commands:**\n"
        f"• `/chatbot on` - Turn Chatbot ON\n"
        f"• `/chatbot off` - Turn Chatbot OFF\n"
        f"• `/ask <query>` - Ask any AI question\n"
        f"• `/love <name1> <name2>` - Love calculator\n"
        f"• `/shayri` - Poetic shayaris\n"
        f"• `/joke` - Funny jokes"
    )
    await message.reply_text(text, reply_markup=btn)


@Client.on_callback_query(filters.regex(r"^cb_(enable|disable)_chatbot$"))
async def chatbot_callback_handler(client: Client, query: CallbackQuery):
    """Handles inline button clicks for enabling/disabling chatbot."""
    chat_id = query.message.chat.id

    if query.message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(chat_id, query.from_user.id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] and query.from_user.id not in SUDOERS and query.from_user.id != int(OWNER_ID):
                return await query.answer("❌ Only admins can toggle chatbot settings!", show_alert=True)
        except Exception:
            return await query.answer("❌ Admin verification failed.", show_alert=True)

    action = query.data.split("_")[1]
    if action == "enable":
        await set_chatbot_enabled(chat_id, True)
        await query.answer("Chatbot enabled!", show_alert=False)
    else:
        await set_chatbot_enabled(chat_id, False)
        await query.answer("Chatbot disabled!", show_alert=False)

    enabled = await is_chatbot_enabled(chat_id)
    status_icon = "🟢 **ENABLED**" if enabled else "🔴 **DISABLED**"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Enable", callback_data="cb_enable_chatbot"),
            InlineKeyboardButton("🔴 Disable", callback_data="cb_disable_chatbot"),
        ],
        [
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])

    text = (
        f"╭━━━━━━━〔 🤖 **AI CHATBOT SETTINGS** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {query.message.chat.title or query.message.chat.first_name or 'This Chat'}\n"
        f"  ✦ **sᴛᴀᴛᴜs :** {status_icon}\n"
        f"  ✦ **ᴘᴇʀsᴏɴᴀ :** sᴡᴇᴇᴛ ᴀɪ ɢɪʀʟ 🌸\n\n"
        f"When enabled, I will reply to messages, questions, stickers, photos, and voice notes!\n\n"
        f"**Quick Commands:**\n"
        f"• `/chatbot on` - Turn Chatbot ON\n"
        f"• `/chatbot off` - Turn Chatbot OFF\n"
        f"• `/ask <query>` - Ask any AI question\n"
        f"• `/love <name1> <name2>` - Love calculator\n"
        f"• `/shayri` - Poetic shayaris\n"
        f"• `/joke` - Funny jokes"
    )
    try:
        await query.message.edit_text(text, reply_markup=btn)
    except Exception:
        pass


@Client.on_message(filters.command(["api", "usage", "quota"]))
async def api_usage_cmd(client: Client, message: Message):
    """
    VIP AI API Usage & Daily Quota Dashboard for Creator / Sudoers.
    Displays live percentage used & remaining for Groq and Gemini daily limits.
    """
    user_id = message.from_user.id if message.from_user else 0
    if user_id not in SUDOERS and user_id != int(OWNER_ID):
        return await message.reply_text("❌ **This API Quota Dashboard is reserved for the Bot Creator/Sudoers.**")

    dashboard_text = await format_api_usage_dashboard()
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="cb_refresh_api_usage"),
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])
    await message.reply_text(dashboard_text, reply_markup=btn)


@Client.on_callback_query(filters.regex(r"^cb_refresh_api_usage$"))
async def api_usage_callback_handler(client: Client, query: CallbackQuery):
    """Refreshes the live API usage dashboard on demand for Creator/Sudoers."""
    user_id = query.from_user.id
    if user_id not in SUDOERS and user_id != int(OWNER_ID):
        return await query.answer("❌ Only the Creator/Sudoers can view this dashboard!", show_alert=True)

    dashboard_text = await format_api_usage_dashboard()
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="cb_refresh_api_usage"),
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])
    try:
        await query.message.edit_text(dashboard_text, reply_markup=btn)
        await query.answer("✅ API Quota Dashboard refreshed!", show_alert=False)
    except Exception:
        await query.answer("✅ Dashboard is up to date!")


@Client.on_message(filters.command(["ask", "ai", "gemini", "gpt", "chatgpt"]))
async def ask_ai_command(client: Client, message: Message):
    """Ask AI any question directly via command with animated typing effect."""
    if len(message.command) < 2 and not (message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption)):
        return await message.reply_text(
            "💡 **Usage:** `/ask <your question>` or reply to a message with `/ask`\n\n"
            "**Example:** `/ask who is cm of bihar`\n"
            "**Example:** `/ask how day is long`"
        )

    query = " ".join(message.command[1:]) if len(message.command) > 1 else (message.reply_to_message.text or message.reply_to_message.caption)
    user_name = message.from_user.first_name if message.from_user else "Friend"

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    status_msg = await message.reply_text("✍️ **ᴛʏᴘɪɴɢ...** 🌸")

    response = await generate_conversational_response(query, user_name, is_question_mode=True, client=client)

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await status_msg.edit_text("💭 **sᴏᴄʜ ʀᴀʜɪ ʜᴏᴏɴ...** ✨")
        await asyncio.sleep(0.5)
        await status_msg.edit_text(response)
    except Exception:
        try:
            await status_msg.edit_text(response)
        except Exception:
            await message.reply_text(response)


@Client.on_message(filters.command(["love", "crush"]))
async def love_command(client: Client, message: Message):
    """Calculate love compatibility percentage with typing animation."""
    if len(message.command) < 3:
        return await message.reply_text(
            "❤️ **Usage:** `/love <Name1> <Name2>`\n\n"
            "**Example:** `/love Rahul Anshika`"
        )

    name1 = message.command[1]
    name2 = message.command[2]

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    status_msg = await message.reply_text("❤️ **ᴄᴀʟᴄᴜʟᴀᴛɪɴɢ ʟᴏᴠᴇ...** 🔮")
    await asyncio.sleep(0.7)
    result = calculate_love(name1, name2)
    try:
        await status_msg.edit_text(result)
    except Exception:
        await message.reply_text(result)


@Client.on_message(filters.command(["shayri", "shayari"]))
async def shayari_command(client: Client, message: Message):
    """Get a random poetic shayari with typing animation."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    status_msg = await message.reply_text("✍️ **ᴛʏᴘɪɴɢ sʜᴀʏᴀʀɪ...** 🌸")
    await asyncio.sleep(0.6)
    shayari = get_random_shayari()
    try:
        await status_msg.edit_text(shayari)
    except Exception:
        await message.reply_text(shayari)


@Client.on_message(filters.command(["joke", "jokes"]))
async def joke_command(client: Client, message: Message):
    """Get a random funny joke with typing animation."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    status_msg = await message.reply_text("✍️ **ᴛʏᴘɪɴɢ ᴊᴏᴋᴇ...** 😂")
    await asyncio.sleep(0.6)
    joke = get_random_joke()
    try:
        await status_msg.edit_text(joke)
    except Exception:
        await message.reply_text(joke)



@Client.on_message(filters.command(["draw", "imagine", "art", "gen"]))
async def draw_command(client: Client, message: Message):
    """Generate high-quality AI image from prompt for cloned bots."""
    if len(message.command) < 2 and not (message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption)):
        return await message.reply_text(
            "🎨 **Usage:** `/draw <your prompt>`\n\n"
            "**Example:** `/draw cute anime girl with flowers`\n"
            "**Example:** `/draw cyberpunk lord shiva 4k`"
        )

    prompt = " ".join(message.command[1:]) if len(message.command) > 1 else (message.reply_to_message.text or message.reply_to_message.caption)

    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    except Exception:
        pass
    status_msg = await message.reply_text("🎨 **ɢᴇɴᴇʀᴀᴛɪɴɢ ʏᴏᴜʀ ᴀɪ ᴀʀᴛ...** ✨\n*Please wait 5-10 seconds...* ⏳")

    img_path = generate_ai_image(prompt)
    if not img_path or not os.path.exists(img_path):
        return await status_msg.edit_text("❌ Image generate nahi ho payi ji, please dusra prompt try karein!")

    try:
        await message.reply_photo(
            photo=img_path,
            caption=(
                f"╭━━━━━━━〔 🎨 **AI GENERATED ART** 〕━━━━━━━╮\n\n"
                f"  ✦ **ᴘʀᴏᴍᴘᴛ :** `{prompt}`\n"
                f"  ✦ **ɢᴇɴᴇʀᴀᴛᴇᴅ ʙʏ :** {client.me.mention or 'VIP AI'}\n"
                f"  ✦ **ᴄʀᴇᴀᴛᴏʀ :** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns) 👑\n\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Failed to send drawn photo: {e}")
        await status_msg.edit_text("❌ Photo upload nahi ho saki ji!")
    finally:
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                pass


@Client.on_message(filters.command(["setname", "nickname", "myname"]))
async def setname_command(client: Client, message: Message):
    """Set custom nickname so cloned bot addresses user by this name."""
    if len(message.command) < 2:
        return await message.reply_text(
            "🏷️ **Usage:** `/setname <your nickname>`\n\n"
            "**Example:** `/setname Vicky`"
        )

    new_name = " ".join(message.command[1:]).strip()
    await save_user_nickname(message.from_user.id, new_name)
    await message.reply_text(f"🌸 **Maine yaad kar liya ji!** 🥰\nAb se main aapko **{new_name}** bulaungi! ✨")


# Automatic conversational listener for cloned bots
@Client.on_message(
    (filters.incoming & (filters.group | filters.private)),
    group=2
)
async def auto_chatbot_listener(client: Client, message: Message):
    """Conversational girl listener for cloned bots."""
    global _message_counts, _blocklist

    if not message.from_user:
        return

    # Ignore own messages (critical for userbot ID clones)
    if client.me and message.from_user.id == client.me.id:
        return

    # Ignore animated dice and game triggers so games module processes them
    if message.dice:
        return

    raw_text = message.text or message.caption or ""
    if raw_text.startswith(("/", "!", ".")) or raw_text.lower().strip() in ["dice", "roll", "dart", "basket", "football", "slot", "bowling"]:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    bot_id = client.me.id
    current_time = datetime.now()

    if message.chat.type == ChatType.PRIVATE:
        await add_served_cuser(bot_id, user_id, client=client, user=message.from_user)
    else:
        await add_served_cchat(bot_id, chat_id, client=client, chat=message.chat)

    _blocklist = {uid: t for uid, t in _blocklist.items() if t > current_time}
    if user_id in _blocklist:
        return

    if user_id not in _message_counts:
        _message_counts[user_id] = {"count": 1, "last_time": current_time}
    else:
        diff = (current_time - _message_counts[user_id]["last_time"]).total_seconds()
        if diff <= 10:
            _message_counts[user_id]["count"] += 1
        else:
            _message_counts[user_id] = {"count": 1, "last_time": current_time}

        if _message_counts[user_id]["count"] >= 5:
            _blocklist[user_id] = current_time + timedelta(seconds=15)
            _message_counts.pop(user_id, None)
            await message.reply_text(
                f"⚠️ Arey {message.from_user.mention}! Thoda sa aaram se na please! 🙈\n"
                "Anshika thak jayegi! 10-15 second ruk ke baat karo na! 🌸✨"
            )
            return

    if not await is_chatbot_enabled(chat_id):
        return

    saved_name = await get_user_nickname(user_id)
    user_name = saved_name or message.from_user.first_name or "Friend"
    bot_username = (client.me.username or "").lower()

    # 1. Stickers
    if message.sticker:
        # Learn sticker in RAM, MongoDB, and Telegram DB!
        await save_sticker(message.sticker.file_id, client=client)
        reply_stk = get_random_sticker(fallback=message.sticker.file_id)
        if reply_stk:
            try:
                await client.send_chat_action(chat_id, ChatAction.CHOOSE_STICKER)
                await asyncio.sleep(0.5)
                await message.reply_sticker(reply_stk)
                return
            except Exception:
                try:
                    await message.copy(chat_id)
                    return
                except Exception:
                    pass
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.5)
        except Exception:
            pass
        await message.reply_text("Hehe kitna cute sticker hai na ji! 🙈🥰")
        return

    # 2. Voice / Audio (Reply with Text Message)
    if message.voice or message.audio:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.5)
        except Exception:
            pass
        await message.reply_text(get_voice_reply())
        return

    # 3. Photos
    if message.photo:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.8)
        except Exception:
            pass
        if message.caption and len(message.caption.strip()) > 1:
            caption_reply = await generate_conversational_response(message.caption.strip(), user_name, is_question_mode=True, client=client)
            await message.reply_text(caption_reply)
        else:
            await message.reply_text(get_photo_reply())
        return

    # 4. Videos
    if message.video:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.8)
        except Exception:
            pass
        await message.reply_text(get_video_reply())
        return

    # 5. Animations / GIFs
    if message.animation:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.8)
        except Exception:
            pass
        await message.reply_text(get_animation_reply())
        return

    # 6. Text
    if not message.text:
        return

    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id != bot_id
        and message.reply_to_message.text
        and not message.reply_to_message.text.startswith(("/", "!", "."))
        and not is_abusive(message.text)
        and not is_abusive(message.reply_to_message.text)
    ):
        try:
            await save_chat_reply(
                word=message.reply_to_message.text,
                reply_type="text",
                content=message.text,
                client=client
            )
        except Exception:
            pass

    clean_text = message.text
    if bot_username:
        clean_text = clean_text.replace(f"@{bot_username}", "").strip()

    if not clean_text:
        clean_text = "hello"

    name_match = re.search(r"(?:mera naam|my name is|call me)\s+([a-zA-Z\u0900-\u097F]+)", clean_text, re.IGNORECASE)
    if name_match:
        extracted = name_match.group(1).strip()
        if 2 <= len(extracted) <= 20 and not is_abusive(extracted):
            await save_user_nickname(user_id, extracted)
            user_name = extracted.title()

    if is_abusive(clean_text):
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.6)
        except Exception:
            pass
        await message.reply_text(get_abuse_refusal())
        return

    try:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        pass

    # Generate girl-style AI conversational response with vivid user memory
    response_text = await generate_conversational_response(clean_text, user_name, client=client, user_id=user_id)

    # Pure text reply only (Zero voice notes)
    try:
        typing_delay = min(max(len(response_text) * 0.015, 0.6), 1.5)
        await asyncio.sleep(typing_delay)
        await message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Cloned bot failed to send chatbot reply: {e}")
