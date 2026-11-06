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
  Ye file Chatbot ka Local RAM Memory & MongoDB Database Manager hai!
  
Isme kya-kya save hota hai?
  1. _qa_cache: AI dwara sikhe gaye Questions & Answers (Instant recall).
  2. _replies_cache: Group me users ki aapsi baatein jo bot ne learn ki hain.
  3. _stickers_cache: Group me aane wale stickers jo bot save karke wapas bhejti hai.
  4. _nicknames_cache: Users ke custom nicknames jo wo /setname se batate hain.
  5. Har save function Telegram Database me bhi log karta hai taaki data kabhi loss na ho.
================================================================================
"""

import random
from typing import Optional, Dict, Any, List
from nexichat import db

from nexichat.database.telegram_db import (
    log_qa_to_telegram,
    log_reply_to_telegram,
    log_sticker_to_telegram
)

chatbot_status_db = db.chatbot_status
chatai_db = db.chatai
qa_cache_db = db.qa_cache
stickers_db = db.stickers
user_nicknames_db = db.user_nicknames
afk_db = db.afk

# In-memory caches for ultra-fast performance
_replies_cache: List[Dict[str, Any]] = []
_qa_cache: Dict[str, str] = {}
_stickers_cache: List[str] = []
_nicknames_cache: Dict[int, str] = {}
_afk_cache: Dict[int, Dict[str, Any]] = {}
_cache_loaded = False


async def is_chatbot_enabled(chat_id: int) -> bool:
    """Check if chatbot is enabled for a given chat (defaults to True)."""
    status_doc = await chatbot_status_db.find_one({"chat_id": chat_id})
    if not status_doc:
        return True
    return status_doc.get("enabled", True)


async def set_chatbot_enabled(chat_id: int, enabled: bool):
    """Enable or disable chatbot for a given chat."""
    await chatbot_status_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )


async def is_voicemode_enabled(chat_id: int) -> bool:
    """Check if voice note mode is enabled for a given chat (defaults to False)."""
    status_doc = await chatbot_status_db.find_one({"chat_id": chat_id})
    if not status_doc:
        return False
    return status_doc.get("voicemode", False)


async def set_voicemode_enabled(chat_id: int, enabled: bool):
    """Enable or disable voice note mode for a given chat."""
    await chatbot_status_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"voicemode": enabled}},
        upsert=True
    )


async def load_replies_cache():
    """Load all learned replies, Q&A memory, and stickers into cache."""
    global _replies_cache, _qa_cache, _stickers_cache, _cache_loaded
    try:
        cursor = chatai_db.find()
        _replies_cache = await cursor.to_list(length=None)

        # Load Q&A cache
        qa_cursor = qa_cache_db.find()
        qa_list = await qa_cursor.to_list(length=None)
        for doc in qa_list:
            if "q" in doc and "a" in doc:
                _qa_cache[doc["q"]] = doc["a"]

        # Load learned stickers
        stk_cursor = stickers_db.find()
        stk_list = await stk_cursor.to_list(length=None)
        for doc in stk_list:
            fid = doc.get("file_id")
            if fid and fid not in _stickers_cache:
                _stickers_cache.append(fid)

        _cache_loaded = True
    except Exception:
        pass


async def save_chat_reply(word: str, reply_type: str, content: str, client: Optional[Any] = None):
    """
    Save learned reply data into chatai collection AND Telegram Database.
    reply_type: 'text', 'sticker', 'photo', 'video', 'animation', 'voice'
    content: text message or Telegram file_id
    """
    global _replies_cache
    if not word or not content:
        return

    word_clean = word.strip().lower()
    doc = {
        "word": word_clean,
        "type": reply_type,
        "content": content
    }

    try:
        existing = await chatai_db.find_one({"word": word_clean, "content": content})
        if not existing:
            await chatai_db.insert_one(doc)
            _replies_cache.append(doc)
            # Koyeb Free Tier RAM Guard: Cap in-memory replies to 2500 items
            if len(_replies_cache) > 2500:
                _replies_cache.pop(0)
    except Exception:
        pass

    if client:
        try:
            await log_reply_to_telegram(client, word_clean, reply_type, content)
        except Exception:
            pass


async def get_chat_reply(word: str = "", clean_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Search for a learned reply matching the given word/phrase."""
    global _replies_cache, _cache_loaded
    if not _cache_loaded:
        await load_replies_cache()

    target_text = clean_text or word
    if not target_text:
        return None

    word_clean = target_text.strip().lower()

    exact_matches = [r for r in _replies_cache if r.get("word") == word_clean]
    if exact_matches:
        return random.choice(exact_matches)

    partial_matches = [r for r in _replies_cache if r.get("word") in word_clean or word_clean in r.get("word", "")]
    if partial_matches:
        return random.choice(partial_matches)

    return None


async def save_qa_pair(question: str, answer: str, client: Optional[Any] = None):
    """Save an answered question to memory, MongoDB, and Telegram Database."""
    global _qa_cache
    if not question or not answer:
        return

    q_key = question.strip().lower()
    _qa_cache[q_key] = answer

    # Koyeb Free Tier RAM Guard: Cap in-memory Q&A cache to 2500 items
    if len(_qa_cache) > 2500:
        try:
            oldest_k = next(iter(_qa_cache))
            _qa_cache.pop(oldest_k, None)
        except Exception:
            pass

    try:
        await qa_cache_db.update_one(
            {"q": q_key},
            {"$set": {"a": answer}},
            upsert=True
        )
    except Exception:
        pass

    if client:
        try:
            await log_qa_to_telegram(client, question, answer)
        except Exception:
            pass


def _jaccard_token_similarity(text1: str, text2: str) -> float:
    """Calculate token-level Jaccard similarity between two strings."""
    import re
    w1 = set(re.sub(r"[^\w\s]", "", text1.strip().lower()).split())
    w2 = set(re.sub(r"[^\w\s]", "", text2.strip().lower()).split())
    if not w1 or not w2:
        return 0.0
    common = w1 & w2
    union = w1 | w2
    return len(common) / len(union) if union else 0.0


async def get_qa_answer(question: str) -> Optional[str]:
    """Retrieve an answer from Q&A memory with exact and semantic fuzzy matching (0 API credits)."""
    global _qa_cache, _cache_loaded
    if not _cache_loaded:
        await load_replies_cache()

    if not question:
        return None

    import re
    q_norm = re.sub(r"[^\w\s]", "", question.strip().lower())
    if not q_norm:
        return None

    # 1. Exact match in memory
    if q_norm in _qa_cache:
        return _qa_cache[q_norm]
    if question.strip().lower() in _qa_cache:
        return _qa_cache[question.strip().lower()]

    # 2. Token overlap similarity match (Jaccard similarity >= 0.70)
    q_words = set(q_norm.split())
    if len(q_words) >= 2:
        for saved_q, saved_a in _qa_cache.items():
            sim = _jaccard_token_similarity(question, saved_q)
            if sim >= 0.70:
                return saved_a

    return None



async def save_sticker(file_id: str, client: Optional[Any] = None):
    """Learn and store a sticker file ID in RAM, MongoDB, and Telegram Database."""
    global _stickers_cache
    if not file_id:
        return
    if file_id not in _stickers_cache:
        _stickers_cache.append(file_id)
        if len(_stickers_cache) > 500:
            _stickers_cache.pop(0)
    try:
        await stickers_db.update_one(
            {"file_id": file_id},
            {"$set": {"file_id": file_id}},
            upsert=True
        )
    except Exception:
        pass

    if client:
        try:
            await log_sticker_to_telegram(client, file_id)
        except Exception:
            pass


def get_random_sticker(fallback: Optional[str] = None) -> Optional[str]:
    """Get a random sticker file_id from cache, or fallback."""
    global _stickers_cache
    if _stickers_cache:
        return random.choice(_stickers_cache)
    return fallback


async def save_user_nickname(user_id: int, nickname: str):
    """Save custom user nickname in RAM and DB."""
    global _nicknames_cache
    if not user_id or not nickname:
        return
    clean_name = nickname.strip().title()
    _nicknames_cache[user_id] = clean_name
    try:
        await user_nicknames_db.update_one(
            {"user_id": user_id},
            {"$set": {"nickname": clean_name}},
            upsert=True
        )
    except Exception:
        pass


async def get_user_nickname(user_id: int) -> Optional[str]:
    """Retrieve saved nickname for a user."""
    global _nicknames_cache
    if user_id in _nicknames_cache:
        return _nicknames_cache[user_id]
    try:
        doc = await user_nicknames_db.find_one({"user_id": user_id})
        if doc and "nickname" in doc:
            _nicknames_cache[user_id] = doc["nickname"]
            return doc["nickname"]
    except Exception:
        pass
    return None


async def set_user_afk(user_id: int, reason: str = ""):
    """Store AFK state with timestamp and reason."""
    import time
    global _afk_cache
    data = {
        "afk": True,
        "reason": reason.strip(),
        "time": time.time()
    }
    _afk_cache[user_id] = data
    try:
        await afk_db.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
    except Exception:
        pass


async def get_user_afk(user_id: int) -> Optional[Dict[str, Any]]:
    """Get AFK state if active."""
    global _afk_cache
    if user_id in _afk_cache:
        return _afk_cache[user_id]
    try:
        doc = await afk_db.find_one({"user_id": user_id})
        if doc and doc.get("afk"):
            _afk_cache[user_id] = doc
            return doc
    except Exception:
        pass
    return None


async def remove_user_afk(user_id: int) -> Optional[Dict[str, Any]]:
    """Remove AFK state and return previous data."""
    global _afk_cache
    old_data = await get_user_afk(user_id)
    _afk_cache.pop(user_id, None)
    try:
        await afk_db.delete_one({"user_id": user_id})
    except Exception:
        pass
    return old_data


# ==============================================================================
# MULTI-TURN CONVERSATION CONTEXT (5-Minute Sliding Ring Buffer)
# ==============================================================================
_conversation_context: Dict[int, List[Dict[str, Any]]] = {}


def append_user_context(user_id: int, role: str, text: str):
    """Store recent dialogue turn in sliding conversation buffer."""
    import time
    global _conversation_context
    if not user_id or not text:
        return
    now = time.time()
    if user_id not in _conversation_context:
        _conversation_context[user_id] = []

    # Prune expired turns older than 300s (5 minutes)
    _conversation_context[user_id] = [
        m for m in _conversation_context[user_id] if (now - m.get("time", 0)) < 300
    ]

    _conversation_context[user_id].append({"role": role, "text": text.strip(), "time": now})

    # Keep at most 6 recent turns (3 user + 3 Priya) to protect RAM
    if len(_conversation_context[user_id]) > 6:
        _conversation_context[user_id] = _conversation_context[user_id][-6:]


def get_user_context(user_id: int) -> List[Dict[str, Any]]:
    """Fetch active dialogue history for user within last 5 minutes."""
    import time
    global _conversation_context
    if not user_id:
        return []
    now = time.time()
    history = _conversation_context.get(user_id, [])
    active = [m for m in history if (now - m.get("time", 0)) < 300]
    _conversation_context[user_id] = active
    return active


def clear_user_context(user_id: int):
    """Reset dialogue history when user requests to forget or on reset."""
    global _conversation_context
    _conversation_context.pop(user_id, None)


