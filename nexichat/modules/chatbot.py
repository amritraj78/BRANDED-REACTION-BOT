# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Student Friendly Guide)
================================================================================
Is file ka kya kaam hai?
  Ye file Chatbot ka Main Controller hai. Yahi se decide hota hai ki user ke
  message ka reply kaise dena hai.
  
Kaise kaam karta hai?
  1. /chatbot on|off command handle karta hai.
  2. Har message type ka reply karta hai:
     - Sticker ka reply sticker se.
     - Voice note ka reply voice note se (/voice se banta hai).
     - Photo / Video / GIF ka sweet reply.
  3. Continuous Self-Learning: Group me log aapas me baat karte hain, toh ye
     unke sawal-jawab passive tareeqe se learn karke Telegram Database me save
     karti rehti hai!
  4. /voice <text> se girl voice generate karta hai.
  5. /draw <prompt> se free AI images generate karta hai.
================================================================================
"""

import os
import re
import time
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

import config
from config import OWNER_ID
from nexichat import LOGGER, nexichat, SUDOERS
from nexichat.database.chatbot import (
    is_chatbot_enabled,
    set_chatbot_enabled,
    is_voicemode_enabled,
    set_voicemode_enabled,
    save_chat_reply,
    get_chat_reply,
    save_sticker,
    get_random_sticker,
    save_qa_pair,
    save_user_nickname,
    get_user_nickname
)
from nexichat.modules.helpers.media_gen import generate_voice_file, generate_ai_image
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.modules.helpers.ai import (
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

# Anti-spam flood protection
_message_counts = {}
_blocklist = {}
_chat_text_streak = {}


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


@nexichat.on_message(filters.command(["chatbot", "chat"]))
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


@nexichat.on_callback_query(filters.regex(r"^cb_(enable|disable)_chatbot$"))
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


@nexichat.on_message(filters.command(["voicemode", "vchat", "voicechat"]))
async def voicemode_toggle_cmd(client: Client, message: Message):
    """
    Toggle or check voice mode status:
    /voicemode on -> Chatbot talks in sweet girl voice notes
    /voicemode off -> Chatbot talks in text + voice on voice messages
    /voicemode -> Show interactive toggle menu
    """
    chat_id = message.chat.id

    if len(message.command) > 1:
        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            if not await is_admin_or_sudo(client, message):
                return await message.reply_text("❌ **Only administrators can change voice mode settings.**")

        action = message.command[1].lower()
        if action in ["on", "enable", "yes", "true"]:
            await set_voicemode_enabled(chat_id, True)
            return await message.reply_text("🎙️ **Voice Note Mode is now ENABLED!** 🌸\nMain ab yahan aapse pyari awaz me voice notes me baat karungi ji! 🥰✨")
        elif action in ["off", "disable", "no", "false"]:
            await set_voicemode_enabled(chat_id, False)
            return await message.reply_text("📝 **Voice Note Mode is now DISABLED!**\nMain text messages me baat karungi aur voice bhejne par voice note dungi! 🌸")
        else:
            return await message.reply_text("ℹ️ **Usage:** `/voicemode on` or `/voicemode off`")

    enabled = await is_voicemode_enabled(chat_id)
    status_icon = "🟢 **ENABLED**" if enabled else "🔴 **DISABLED**"

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Enable Voice Mode", callback_data="cb_enable_voicemode"),
            InlineKeyboardButton("🔴 Disable Voice Mode", callback_data="cb_disable_voicemode"),
        ],
        [
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])

    text = (
        f"╭━━━━━━━〔 🎙️ **VOICE NOTE MODE SETTINGS** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {message.chat.title or message.chat.first_name or 'This Chat'}\n"
        f"  ✦ **ᴠᴏɪᴄᴇ ᴍᴏᴅᴇ :** {status_icon}\n"
        f"  ✦ **ᴛᴏɴᴇ :** ɴᴀᴛᴜʀᴀʟ sᴡᴇᴇᴛ ɢɪʀʟ ᴠᴏɪᴄᴇ 🌸\n\n"
        f"When enabled, all chatbot replies will be sent as realistic girl voice notes!\n\n"
        f"**Quick Commands:**\n"
        f"• `/voicemode on` - Turn Voice Note Mode ON\n"
        f"• `/voicemode off` - Turn Voice Note Mode OFF\n"
        f"• `/voice <text>` - Speak any text as girl voice note"
    )
    await message.reply_text(text, reply_markup=btn)


@nexichat.on_callback_query(filters.regex(r"^cb_(enable|disable)_voicemode$"))
async def voicemode_callback_handler(client: Client, query: CallbackQuery):
    """Handles inline button clicks for enabling/disabling voice mode."""
    chat_id = query.message.chat.id

    if query.message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        user_id = query.from_user.id
        if user_id not in SUDOERS and user_id != int(OWNER_ID):
            try:
                member = await client.get_chat_member(chat_id, user_id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    return await query.answer("❌ Only administrators can change voice settings!", show_alert=True)
            except Exception:
                return await query.answer("❌ Could not verify permissions!", show_alert=True)

    action = query.data.split("_")[1]
    enable = (action == "enable")
    await set_voicemode_enabled(chat_id, enable)

    status_icon = "🟢 **ENABLED**" if enable else "🔴 **DISABLED**"
    feedback = "🎙️ Voice Mode enabled! Ab har reply pyari girl voice note me aayega! 🌸" if enable else "📝 Voice Mode disabled! Ab regular text me reply aayega! ✨"
    await query.answer(feedback, show_alert=True)

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Enable Voice Mode", callback_data="cb_enable_voicemode"),
            InlineKeyboardButton("🔴 Disable Voice Mode", callback_data="cb_disable_voicemode"),
        ],
        [
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
        ]
    ])

    text = (
        f"╭━━━━━━━〔 🎙️ **VOICE NOTE MODE SETTINGS** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {query.message.chat.title or query.message.chat.first_name or 'This Chat'}\n"
        f"  ✦ **ᴠᴏɪᴄᴇ ᴍᴏᴅᴇ :** {status_icon}\n"
        f"  ✦ **ᴛᴏɴᴇ :** ɴᴀᴛᴜʀᴀʟ sᴡᴇᴇᴛ ɢɪʀʟ ᴠᴏɪᴄᴇ 🌸\n\n"
        f"When enabled, all chatbot replies will be sent as realistic girl voice notes!"
    )
    try:
        await query.message.edit_text(text, reply_markup=btn)
    except Exception:
        pass


@nexichat.on_message(filters.command(["ask", "ai", "gemini", "gpt", "chatgpt"]))
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


@nexichat.on_message(filters.command(["love", "crush"]))
async def love_command(client: Client, message: Message):
    """Calculate love compatibility percentage with typing animation."""
    if len(message.command) < 3:
        return await message.reply_text(
            "❤️ **Usage:** `/love <Name1> <Name2>`\n\n"
            "**Example:** `/love Rahul Priya`"
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


@nexichat.on_message(filters.command(["shayri", "shayari"]))
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


@nexichat.on_message(filters.command(["joke", "jokes"]))
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


@nexichat.on_message(filters.command(["voice", "speak", "tts"]))
async def voice_command(client: Client, message: Message):
    """Generate girl voice note from text."""
    if len(message.command) < 2 and not (message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption)):
        return await message.reply_text(
            "🎙️ **Usage:** `/voice <text>` or reply to any message with `/voice`\n\n"
            "**Example:** `/voice Namaste ji, kaise ho aap sabhi?`"
        )

    text = " ".join(message.command[1:]) if len(message.command) > 1 else (message.reply_to_message.text or message.reply_to_message.caption)

    try:
        await client.send_chat_action(message.chat.id, ChatAction.RECORD_AUDIO)
    except Exception:
        pass

    voice_path = generate_voice_file(text, lang="hi")
    if not voice_path or not os.path.exists(voice_path):
        return await message.reply_text("❌ Voice note generate nahi ho paya, please thodi der baad try karein!")

    try:
        caption_txt = f"🌸 **Voice Note for you ji!** 🥰\n💬 *\"{text[:60]}...\"*" if len(text) > 60 else f"🌸 **Voice Note for you ji!** 🥰\n💬 *\"{text}\"*"
        await message.reply_voice(voice=voice_path, caption=caption_txt)
    except Exception as e:
        logger.error(f"Failed to send voice: {e}")
        await message.reply_text("❌ Voice note send karne me dikkat aayi!")
    finally:
        if voice_path and os.path.exists(voice_path):
            try:
                os.remove(voice_path)
            except Exception:
                pass


@nexichat.on_message(filters.command(["draw", "imagine", "art", "gen"]))
async def draw_command(client: Client, message: Message):
    """Generate high-quality AI image from prompt."""
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


@nexichat.on_message(filters.command(["setname", "nickname", "myname"]))
async def setname_command(client: Client, message: Message):
    """Set custom nickname so the bot addresses the user by this name."""
    if len(message.command) < 2:
        return await message.reply_text(
            "🏷️ **Usage:** `/setname <your nickname>`\n\n"
            "**Example:** `/setname Vicky`"
        )

    new_name = " ".join(message.command[1:]).strip()
    await save_user_nickname(message.from_user.id, new_name)
    await message.reply_text(f"🌸 **Maine yaad kar liya ji!** 🥰\nAb se main aapko **{new_name}** bulaungi! ✨")


# Automatic conversational listener for ALL media types
@nexichat.on_message(
    (filters.incoming & (filters.group | filters.private)),
    group=2
)
async def auto_chatbot_listener(client: Client, message: Message):
    """
    Conversational girl listener:
    - Replies in private chats automatically.
    - Replies in groups when chatbot is enabled!
    - Handles text, stickers (with sticker), voice notes, photos, videos, GIFs!
    - Strict anti-abuse refusal without using bad words.
    - Q&A Memory learning so it remembers answers.
    - Anti-flood spam protection.
    """
    global _message_counts, _blocklist

    if not message.from_user:
        return

    # Ignore animated dice and game triggers so games module processes them
    if message.dice:
        return

    # Ignore bot commands so commands are handled by their own handlers
    raw_text = message.text or message.caption or ""
    if raw_text.startswith(("/", "!", ".")) or raw_text.lower().strip() in ["dice", "roll", "dart", "basket", "football", "slot", "bowling"]:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = datetime.now()

    # Track served entities & log to Telegram DB
    if message.chat.type == ChatType.PRIVATE:
        await add_served_user(user_id, client=client, user=message.from_user)
    else:
        await add_served_chat(chat_id, client=client, chat=message.chat)

    # Clean expired blocks
    _blocklist = {uid: t for uid, t in _blocklist.items() if t > current_time}
    if user_id in _blocklist:
        return

    # Anti-spam flood check: Max 5 messages per 10 seconds per user
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
                "𝐀ɴɢʟᴇ‹✨ thak jayegi! 10-15 second ruk ke baat karo na! 🌸✨"
            )
            return

    # Check if chatbot is enabled for this chat
    if not await is_chatbot_enabled(chat_id):
        return

    saved_name = await get_user_nickname(user_id)
    user_name = saved_name or message.from_user.first_name or "Friend"
    bot_id = client.me.id
    bot_username = (client.me.username or "").lower()

    # In groups:
    # 1. If replied to bot or mentioned bot -> 100% reply
    # 2. If general group message and chatbot is ON -> reply!
    is_private = message.chat.type == ChatType.PRIVATE
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot_id
    )
    is_mentioned = bot_username and (f"@{bot_username}" in raw_text.lower())

    # ========================================================
    # 1. HANDLE STICKERS (Sticker ka reply sticker se)
    # ========================================================
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

    # ========================================================
    # 2. HANDLE VOICE NOTES & AUDIO (Reply with Sweet Girl Voice Note!)
    # ========================================================
    if message.voice or message.audio:
        try:
            await client.send_chat_action(chat_id, ChatAction.RECORD_AUDIO)
        except Exception:
            pass
        chosen_voice_txt = get_voice_reply()
        voice_path = generate_voice_file(chosen_voice_txt, lang="hi")
        if voice_path and os.path.exists(voice_path):
            try:
                # Pure Voice Note (No text caption!)
                await message.reply_voice(voice=voice_path)
                try:
                    os.remove(voice_path)
                except Exception:
                    pass
                return
            except Exception as e:
                logger.debug(f"Failed to reply voice: {e}")
        await message.reply_text(chosen_voice_txt)
        return

    # ========================================================
    # 3. HANDLE PHOTOS
    # ========================================================
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

    # ========================================================
    # 4. HANDLE VIDEOS
    # ========================================================
    if message.video:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.8)
        except Exception:
            pass
        await message.reply_text(get_video_reply())
        return

    # ========================================================
    # 5. HANDLE ANIMATIONS / GIFS
    # ========================================================
    if message.animation:
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.8)
        except Exception:
            pass
        await message.reply_text(get_animation_reply())
        return

    # ========================================================
    # 6. HANDLE TEXT MESSAGES
    # ========================================================
    if not message.text:
        return

    # Self-learning: If someone replies to another user in a group, save reply pair
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

    # Auto-learn user nickname if user introduces themselves
    name_match = re.search(r"(?:mera naam|my name is|call me)\s+([a-zA-Z\u0900-\u097F]+)", clean_text, re.IGNORECASE)
    if name_match:
        extracted = name_match.group(1).strip()
        if 2 <= len(extracted) <= 20 and not is_abusive(extracted):
            await save_user_nickname(user_id, extracted)
            user_name = extracted.title()

    # Anti-abuse check
    if is_abusive(clean_text):
        try:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(0.6)
        except Exception:
            pass
        await message.reply_text(get_abuse_refusal())
        return

    # Spontaneous sweet voice reply: if user asks Priya/Angle to speak or send voice
    voice_trigger_match = re.search(
        r"\b(voice\s*(?:bhejo|sunao|karo|me\s*bolo|note|audio)|kuch\s*bolo\s*na|awaz\s*sunao|sing\s*a?\s*song|gana\s*gao|bolke\s*batao|apni\s*awaz|audio\s*bhejo|voice\s*chat|bolke\s*bolo|voice\s*me\s*baat)\b",
        clean_text,
        re.IGNORECASE
    )
    if voice_trigger_match:
        voice_responses = [
            f"Namaste {user_name} ji! Kaise ho aap? Kahiye na, kya haal chaal hain? 🌸",
            f"Arey suniye na {user_name}! Main toh hamesha aapke sath hoon! Kabhi bhi udaas mat hona, theek hai na? ✨",
            f"Hehe {user_name}! Aapne itne pyaar se bola toh main kaise na bolti! Kahiye na, aur kya chal raha hai? 🙈",
            f"Hii {user_name}! Main sun rahi hoon aapko ji! Aur batao khana khaya sabne? Dher saara pyaar! 🌸💖"
        ]
        chosen_voice_txt = random.choice(voice_responses)
        try:
            await client.send_chat_action(chat_id, ChatAction.RECORD_AUDIO)
            voice_path = generate_voice_file(chosen_voice_txt, lang="hi")
            if voice_path and os.path.exists(voice_path):
                # PURE VOICE NOTE ONLY (NO CAPTION!)
                await message.reply_voice(voice=voice_path)
                try:
                    os.remove(voice_path)
                except Exception:
                    pass
                return
        except Exception as ve:
            logger.debug(f"Spontaneous voice notice: {ve}")

    try:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
    except Exception:
        pass

    # Generate girl-style AI conversational response with multi-turn context
    response_text = await generate_conversational_response(clean_text, user_name, client=client, user_id=user_id)

    # Automatic Natural Switcher: alternates between pure Voice Note and pure Text Message!
    streak = _chat_text_streak.get(chat_id, 0)
    voicemode_on = await is_voicemode_enabled(chat_id)
    is_greeting_phrase = bool(re.search(r"\b(hii?|hello|kaise\s+ho|kya\s+haal|aur\s+batao|kya\s+kar\s+rahi|suno|kaha\s+ho)\b", clean_text, re.IGNORECASE))

    # Send voice note if voicemode is on, or after 2-4 text messages naturally
    should_send_voice = (
        voicemode_on
        or streak >= 4
        or (streak >= 2 and random.random() < 0.45)
        or (streak >= 1 and is_greeting_phrase and random.random() < 0.50)
    )

    if should_send_voice:
        try:
            await client.send_chat_action(chat_id, ChatAction.RECORD_AUDIO)
            voice_path = generate_voice_file(response_text, lang="hi")
            if voice_path and os.path.exists(voice_path):
                _chat_text_streak[chat_id] = 0
                # PURE VOICE NOTE ONLY (NO TEXT CAPTION!)
                await message.reply_voice(voice=voice_path)
                try:
                    os.remove(voice_path)
                except Exception:
                    pass
                return
        except Exception as ve:
            logger.debug(f"Voice auto-switch dispatch notice: {ve}")

    # Otherwise send PURE TEXT MESSAGE ONLY (NO VOICE NOTE!)
    _chat_text_streak[chat_id] = streak + 1
    try:
        typing_delay = min(max(len(response_text) * 0.015, 0.6), 1.5)
        await asyncio.sleep(typing_delay)
        await message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Failed to send chatbot reply: {e}")
