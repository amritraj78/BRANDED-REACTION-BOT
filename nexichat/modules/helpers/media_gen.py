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
  Ye file Voice Note (.mp3) aur AI Images (.jpg) generate karti hai:
  1. generate_voice_file(text): Google TTS endpoint se sweet girl voice note banati hai.
  2. generate_ai_image(prompt): Pollinations free AI se high-quality artwork image banati hai.
  3. Dynamic CACHE_DIR: Temp files ko ./cache me rakhti hai jise sentinel auto-clean karta hai.
================================================================================
"""

import os
import re
import uuid
import urllib.parse
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def clean_tts_text(text: str) -> str:
    """Clean text for TTS by removing markdown symbols, emojis, and urls."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[*_`~#|]", "", text)
    # Remove emojis so TTS pronounces words cleanly
    text = re.sub(r"[^\w\s,\.\?\!\'\-]", "", text)
    return text.strip()[:200]


def generate_voice_file(text: str, lang: str = "hi") -> Optional[str]:
    """
    Generate an audio voice file using Google TTS (free, no extra pip dependencies).
    Returns the file path of the generated .mp3 audio file.
    """
    cleaned = clean_tts_text(text)
    if not cleaned:
        cleaned = "Haanji, boliye kya kehna chahte hain aap!"

    encoded_text = urllib.parse.quote(cleaned)
    url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={lang}&client=tw-ob"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200 and len(response.content) > 500:
            file_name = f"voice_{uuid.uuid4().hex[:8]}.mp3"
            file_path = os.path.join(CACHE_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        logger.error(f"TTS generation error: {e}")

    return None


def generate_ai_image(prompt: str) -> Optional[str]:
    """
    Generate an AI image using Pollinations.ai (free high-quality FLUX/SD, zero API key).
    Returns the file path of the generated .jpg image file.
    """
    if not prompt or len(prompt.strip()) < 2:
        prompt = "cute aesthetic girl holding flowers, masterpiece, 4k"

    encoded_prompt = urllib.parse.quote(prompt.strip())
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&nologo=true&seed={uuid.uuid4().int % 100000}"

    try:
        response = requests.get(url, timeout=25)
        if response.status_code == 200 and len(response.content) > 2000:
            file_name = f"image_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(CACHE_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        logger.error(f"AI image generation error: {e}")

    return None
