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
  Ye file Bot Cloning System (/clone, /cloned, /delclone) handle karti hai.
  Koi bhi user @BotFather se token bana kar /clone <token> bhejta hai, toh bot
  unke liye unka apna Reaction + AI Chatbot clone create kar deta hai jo 
  nexichat/mplugin se automatically chalne lagta hai!
================================================================================
"""

import logging
import os
import sys
import shutil
import asyncio
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
import config
from pyrogram.types import BotCommand
from config import API_HASH, API_ID, OWNER_ID
from nexichat import CLONE_OWNERS
from nexichat import nexichat as app, save_clonebot_owner
from nexichat import db as mongodb

CLONES = set()
cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb

    
@app.on_message(filters.command(["clone", "host", "deploy"]))
async def clone_txt(client, message):
    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text("Please wait while I check the bot token.")
        try:
            ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token, plugins=dict(root="nexichat/mplugin"), workers=4)
            await ai.start()
            bot = await ai.get_me()
            bot_id = bot.id
            user_id = message.from_user.id
            await save_clonebot_owner(bot_id, user_id)
            await ai.set_bot_commands([
                    BotCommand("start", "Start the bot"),
                    BotCommand("help", "Get the help menu"),
                    BotCommand("reactions", "Toggle reactions (/reactions on|off)"),
                    BotCommand("chatbot", "Toggle AI chatbot (/chatbot on|off)"),
                    BotCommand("ask", "Ask AI any question"),
                    BotCommand("couples", "Couple of the day game 💍"),
                    BotCommand("propose", "Group propose game 💕"),
                    BotCommand("afk", "Set AFK status 😴"),
                    BotCommand("tagall", "Mention all members in batches 📢"),
                    BotCommand("cancel", "Cancel tag-all process 🛑"),
                    BotCommand("voice", "Girl voice note generator"),
                    BotCommand("draw", "Free AI image generator"),
                    BotCommand("welcome", "Toggle group welcome card"),
                    BotCommand("profile", "View your VIP profile card"),
                    BotCommand("security", "Group shield & antilink protection 🛡️"),
                    BotCommand("antilink", "Toggle group anti-link security"),
                    BotCommand("antispam", "Toggle group flood protector"),
                    BotCommand("truth", "Fun spicy truth game"),
                    BotCommand("dare", "Exciting dare game"),
                    BotCommand("flirt", "Sweet romantic flirt"),
                    BotCommand("love", "Love compatibility calculator"),
                    BotCommand("roast", "Playful roast card 🔥"),
                    BotCommand("quote", "Generate quote card 📜"),
                    BotCommand("shayri", "Poetic shayari generator"),
                    BotCommand("joke", "Funny joke generator"),
                    BotCommand("clone", "Make your own reaction bot"),
                    BotCommand("ping", "Check bot latency"),
                    BotCommand("id", "Get user/chat ID"),
                    BotCommand("stats", "Check bot stats"),
                    BotCommand("exportdb", "Download DB backup"),
                    BotCommand("gcast", "Broadcast message to groups/users"),
                ])
        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text("**Invalid bot token. Please provide a valid one.**")
            return
        except Exception as e:
            cloned_bot = await clonebotdb.find_one({"token": bot_token})
            if cloned_bot:
                await mi.edit_text("**🤖 Your bot is already cloned ✅**")
                return

        await mi.edit_text("**Cloning process started. Please wait for the bot to start.**")
        try:
            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": user_id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
            }
            cloned_bots = clonebotdb.find()
            cloned_bots_list = await cloned_bots.to_list(length=None)
            total_clones = len(cloned_bots_list)
            await clonebotdb.insert_one(details)
            CLONES.add(bot.id)
            
            await app.send_message(
                int(OWNER_ID), f"**#New_Clone**\n\n**Bot:- @{bot.username}**\n\n**Details:-**\n{details}\n\n**Total Cloned:-** {total_clones}"
            )
            try:
                from datetime import datetime
                from nexichat.database.telegram_db import send_to_telegram_db
                await send_to_telegram_db(
                    app,
                    f"✦ **#DATABASE #NEW_CLONE** ✦\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 **Bot:** @{bot.username}\n"
                    f"🆔 **Bot ID:** `{bot.id}`\n"
                    f"👤 **Cloned By User:** `{user_id}`\n"
                    f"📊 **Total Clones:** {total_clones}\n"
                    f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━"
                )
            except Exception:
                pass

            await mi.edit_text(
                f"**Bot @{bot.username} has been successfully cloned and started ✅.**\n**Remove clone by :- /delclone**\n**Check all cloned bot list by:- /cloned**"
            )
        
        except PeerIdInvalid as e:
            await mi.edit_text(f"**Your Bot Siccessfully Cloned👍**\n**You can check by /cloned**\n\n**But please start me (@{app.username}) From owner id**")
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>Error:</b>\n\n<code>{e}</code>\n\n**Forward this message to @Villanns for assistance**"
            )
    else:
        await message.reply_text("**Provide Bot Token after /clone Command from @Botfather.**\n\n**Example:** `/clone bot token paste here`")


@app.on_message(filters.command("cloned"))
async def list_cloned_bots(client, message):
    try:
        cloned_bots = clonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            await message.reply_text("No bots have been cloned yet.")
            return
        total_clones = len(cloned_bots_list)
        text = f"**Total Cloned Bots:** {total_clones}\n\n"
        for bot in cloned_bots_list:
            text += f"**Bot ID:** `{bot['bot_id']}`\n"
            text += f"**Bot Name:** {bot['name']}\n"
            text += f"**Bot Username:** @{bot['username']}\n\n"
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("**An error occurred while listing cloned bots.**")


@app.on_message(filters.command(["clonestats", "cstats"]) & (filters.user(int(OWNER_ID))))
async def clone_fleet_stats_cmd(client, message):
    """Owner command: View detailed metrics of all cloned bots in the fleet."""
    from nexichat.database.clonestats import get_served_cusers, get_served_cchats
    try:
        cloned_bots = clonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            return await message.reply_text("ℹ️ **No bots are currently cloned.**")

        total_clones = len(cloned_bots_list)
        active_in_ram = len(CLONES)

        total_users = 0
        total_chats = 0
        lines = []

        for bot in cloned_bots_list:
            bid = bot.get("bot_id")
            b_users = len(await get_served_cusers(bid))
            b_chats = len(await get_served_cchats(bid))
            total_users += b_users
            total_chats += b_chats
            is_live = "🟢 Live" if bid in CLONES else "🔴 Idle"
            lines.append(
                f"• @{bot.get('username', 'Bot')}\n"
                f"  🆔 `{bid}` | {is_live}\n"
                f"  👥 Users: `{b_users}` | 💬 Chats: `{b_chats}`"
            )

        fleet_text = (
            f"╭━━━━━━━〔 🤖 **CLONED FLEET STATS** 〕━━━━━━━╮\n\n"
            f"  ✦ **ᴛᴏᴛᴀʟ ᴄʟᴏɴᴇs :** `{total_clones}`\n"
            f"  ✦ **ᴀᴄᴛɪᴠᴇ ɪɴ ʀᴀᴍ :** `{active_in_ram}`\n"
            f"  ✦ **ᴄʟᴏɴᴇ ᴜsᴇʀs :** `{total_users}`\n"
            f"  ✦ **ᴄʟᴏɴᴇ ᴄʜᴀᴛs :** `{total_chats}`\n"
            f"  ✦ **ᴄʀᴇᴀᴛᴏʀ :** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns) 👑\n\n"
            f"╭─────────────────────────────────╮\n"
            + "\n".join(lines[:15]) +
            f"\n╰─────────────────────────────────╯\n"
            f"💡 *All learned data auto-uploaded to Telegram DB!*"
        )
        await message.reply_text(fleet_text)
    except Exception as e:
        logger.error(f"Error in clonestats: {e}")
        await message.reply_text(f"❌ Failed to fetch fleet stats: {e}")

@app.on_message(
    filters.command(["deletecloned", "delcloned", "delclone", "deleteclone", "removeclone", "cancelclone"])
)
async def delete_cloned_bot(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**⚠️ Please provide the bot token after the command.**")
            return

        bot_token = " ".join(message.command[1:])
        ok = await message.reply_text("**Checking the bot token...**")

        cloned_bot = await clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            await clonebotdb.delete_one({"token": bot_token})
            CLONES.discard(cloned_bot["bot_id"])

            await ok.edit_text(
                f"**🤖 your cloned bot has been removed from my database ✅**\n**🔄 Kindly revoke your bot token from @botfather otherwise your bot will stop when @{app.username} will restart ☠️**"
            )
        else:
            await message.reply_text("**Provide Bot Token after /delclone Command from @Botfather.**\n\n**Example:** `/delclone bot token paste here`")
    except Exception as e:
        await message.reply_text(f"**An error occurred while deleting the cloned bot:** {e}")
        logging.exception(e)

async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots...")
        bots = [bot async for bot in clonebotdb.find()]
        
        async def restart_bot(bot):
            bot_token = bot["token"]
            ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token, plugins=dict(root="nexichat/mplugin"), workers=4)
            try:
                await ai.start()
                bot_info = await ai.get_me()
                await ai.set_bot_commands([
                    BotCommand("start", "Start the bot"),
                    BotCommand("help", "Get the help menu"),
                    BotCommand("reactions", "Toggle reactions (/reactions on|off)"),
                    BotCommand("chatbot", "Toggle AI chatbot (/chatbot on|off)"),
                    BotCommand("ask", "Ask AI any question"),
                    BotCommand("couples", "Couple of the day game 💍"),
                    BotCommand("propose", "Group propose game 💕"),
                    BotCommand("afk", "Set AFK status 😴"),
                    BotCommand("tagall", "Mention all members in batches 📢"),
                    BotCommand("cancel", "Cancel tag-all process 🛑"),
                    BotCommand("voice", "Girl voice note generator"),
                    BotCommand("draw", "Free AI image generator"),
                    BotCommand("welcome", "Toggle group welcome card"),
                    BotCommand("profile", "View your VIP profile card"),
                    BotCommand("security", "Group shield & antilink protection 🛡️"),
                    BotCommand("antilink", "Toggle group anti-link security"),
                    BotCommand("antispam", "Toggle group flood protector"),
                    BotCommand("truth", "Fun spicy truth game"),
                    BotCommand("dare", "Exciting dare game"),
                    BotCommand("flirt", "Sweet romantic flirt"),
                    BotCommand("love", "Love compatibility calculator"),
                    BotCommand("roast", "Playful roast card 🔥"),
                    BotCommand("quote", "Generate quote card 📜"),
                    BotCommand("shayri", "Poetic shayari generator"),
                    BotCommand("joke", "Funny joke generator"),
                    BotCommand("clone", "Make your own reaction bot"),
                    BotCommand("ping", "Check bot latency"),
                    BotCommand("id", "Get user/chat ID"),
                    BotCommand("stats", "Check bot stats"),
                    BotCommand("exportdb", "Download DB backup"),
                    BotCommand("gcast", "Broadcast message to groups/users"),
                ])

                if bot_info.id not in CLONES:
                    CLONES.add(bot_info.id)
                    
            except (AccessTokenExpired, AccessTokenInvalid):
                await clonebotdb.delete_one({"token": bot_token})
                logging.info(f"Removed expired or invalid token for bot ID: {bot['bot_id']}")
            except Exception as e:
                logging.exception(f"Error while restarting bot with token {bot_token}: {e}")
            
        await asyncio.gather(*(restart_bot(bot) for bot in bots))
        
    except Exception as e:
        logging.exception("Error while restarting bots.")


@app.on_message(filters.command("delallclone") & filters.user(int(OWNER_ID)))
async def delete_all_cloned_bots(client, message):
    try:
        a = await message.reply_text("**Deleting all cloned bots...**")
        await clonebotdb.delete_many({})
        CLONES.clear()
        await a.edit_text("**All cloned bots have been deleted successfully ✅**")
        os.system(f"kill -9 {os.getpid()} && bash start")
    except Exception as e:
        await a.edit_text(f"**An error occurred while deleting all cloned bots.** {e}")
        logging.exception(e)
