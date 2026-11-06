# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin AI Brain)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye Free AI text generator, sweet girl personality,
  aur memory lookup provide karti hai.
================================================================================
"""

import re
import json
import random
import requests
import asyncio
import logging
import urllib.parse
import urllib.request
from html import unescape
from typing import Optional, Any, Dict, List
from nexichat.database.chatbot import (
    save_qa_pair,
    get_qa_answer,
    append_user_context,
    get_user_context,
    clear_user_context
)
import config

logger = logging.getLogger(__name__)

ABUSE_WORDS = {
    "bsdk", "bhosdike", "bhosadike", "madarchod", "madarchodh", "behenchod",
    "bhenchod", "mc", "bc", "chutiya", "chutiye", "chut", "lodu", "lauda",
    "loda", "gand", "gaand", "gandu", "gaandu", "randi", "rndi", "harami",
    "kamina", "kamine", "kutti", "kutta", "saale", "sale", "fuck", "fucking",
    "bitch", "asshole", "bastard", "cunt", "dick", "pussy", "tatte", "jhant"
}

ABUSE_REFUSALS = [
    "Arey gande words use mat karo na please! 🥺 Achhi baatein karo ji, warna main naraz ho jaungi! 🌸",
    "Aap itne achhe ho, aisi gandi bhasha aapko shobha nahi deti ji! Pyaar aur respect se baat karo na! 💖",
    "Please bad words mat bolo na ji! Respect se baat karoge toh main bhi bohot khush hoke baat karungi! 😇✨",
    "Chhee! Kitni gandi baat hai ye! Achhe bache aisi gaaliyan nahi dete na! Shanti se baat karo! 🌸",
]

def is_abusive(text: str) -> bool:
    if not text:
        return False
    tokens = re.findall(r"\b\w+\b", text.lower())
    for token in tokens:
        if token in ABUSE_WORDS:
            return True
    return False

def get_abuse_refusal() -> str:
    return random.choice(ABUSE_REFUSALS)

SHAYARIS = [
    "🌺 **बहुत अच्छा लगता है तुझे सताना और फिर प्यार से तुझे मनाना।** 🌺\n\n🥀 *Bahut accha lagta hai tujhe satana, aur fir pyaar se tujhe manana.* 🥀",
    "🌺 **मेरी जिंदगी मेरी जान हो तुम, मेरे सुकून का दूसरा नाम हो तुम।** 🌺\n\n🥀 *Meri zindagi meri jaan ho tum, mere sukoon ka doosra naam ho tum.* 🥀",
    "🌺 **तुम मेरी वो खुशी हो जिसके बिना, मेरी सारी खुशी अधूरी लगती है।** 🌺\n\n🥀 *Tum meri wo khushi ho jiske bina, meri saari khushi adhoori lagti hai.* 🥀",
    "🌺 **दिल की धड़कन और मेरी सदा हो तुम, मेरी पहली और आखिरी वफ़ा हो तुम।** 🌺\n\n🥀 *Dil ki dhadkan aur meri sada ho tum, meri pehli aur aakhiri wafa ho tum.* 🥀",
    "🌺 **चेहरे पर हंसी और आंखों में नमी है, सब कुछ है मेरे पास बस तेरी कमी है।** 🌺\n\n🥀 *Chehre par hansi aur aankhon mein nami hai, sab kuch hai mere paas bas teri kami hai.* 🥀",
    "🌺 **हजारों महफिलें हैं और लाखों मेले हैं, पर जहां तुम नहीं वहां हम बिल्कुल अकेले हैं।** 🌺\n\n🥀 *Hazaron mehfilein hain aur laakhon mele hain, par jahan tum nahi wahan hum akele hain.* 🥀",
]

JOKES = [
    "😂 **टीचर:** बताओ चाँद पर पहला कदम किसने रखा?\n**पप्पू:** नील आर्मस्ट्रांग ने!\n**टीचर:** और दूसरा?\n**पप्पू:** दूसरा भी उसी ने रखा होगा मैम, वो लंगड़ी थोड़ी खेल रहा था! 🤣",
    "😂 **डॉक्टर:** आपके पति को बहुत आराम की जरूरत है, ये लो नींद की गोली।\n**पत्नी:** इन्हें कब देनी है डॉक्टर साहब?\n**डॉक्टर:** ये उनके लिए नहीं, आपके लिए है ताकि वो चैन से सो सकें! 🤐",
    "😂 **दोस्त:** भाई तेरी गर्लफ्रेंड का मैसेज आया है?\n**दूसरा दोस्त:** हाँ, उसने लिखा है 'I Miss You'\n**पहला दोस्त:** तो तूने क्या रिप्लाई दिया?\n**दूसरा दोस्त:** मैंने लिखा 'Remind Me Later'! 😂",
]

VOICE_REPLIES = [
    "Aww! Aapki pyari si voice sun kar bahut achha laga ji! 🥰 Bolo na, main sun rahi hoon! 🌸",
    "Aapki awaz mein ek alag hi mithaas hai ji! Sunke maza aa gaya! 🙈✨",
    "Haanji, maine aapka voice note sun liya! Kitne cute ho aap! 💖 Aur batao?",
]

PHOTO_REPLIES = [
    "Waah! Kitni beautiful picture hai ye! Sach mein dil khush ho gaya! 😍✨",
    "Arey waah, photo toh bahut pyari lag rahi hai! 📸 Kisi ki nazar na lage! 🧿💖",
    "Bahut khoobsurat photo hai ji! Aapki choice kamaal ki hai! 🥰",
    "Awww, kitni cute picture hai! Mujhe toh bohot zyada pasand aayi! 🌸💖",
    "Kya baat hai! Ye photo toh kisi gallery mein frame karwane layak hai! 🖼️✨",
    "Arey waah ji! Dil ekdum khush ho gaya ye dekh ke! 🌺🥰 Aur sunao na?",
    "Bahut hi pyari photo hai! Aapka photography sense sach me kamaal ka hai! 📸🌟",
    "Hehe, photo toh ekdum lajawab hai ji! Aise hi pyare pyare moments share karte raha karo! 🙈🌸",
    "Kitna sundar view hai na! Sach mein maza aa gaya dekh kar! 🍃✨",
    "Uff! Nazar na lag jaye is photo ko! Bahut hi pyari lag rahi hai! 🧿💕",
]

VIDEO_REPLIES = [
    "Waah! Video toh ekdum kamaal ki hai ji! 🎬 Maza aa gaya dekh kar! 💖",
    "Mast video hai ji! Maine poori dekhi, hehe! 🥰✨",
    "Kya baat hai, zabardast video share ki aapne! 🍿 Aur sunao kaise ho? 🌸",
]

ANIMATION_REPLIES = [
    "Haha ye GIF kitna funny aur cute hai ji! 🤣💖 Ekdum meri tarah cute! 🙈✨",
    "Hehe, mast animation hai! Aise hi muskuraate raha karo aap! 🌸🥰",
]

GIRL_KNOWLEDGE_BASE = [
    (
        r"\b(hello|hi|hey|heyy|helo|hii|hola|namaste|pranam|salam|sup|ram ram|radhe radhe)\b",
        [
            "Haanji {user}! Hello! Kaise ho aap? Kuch kehna tha kya? 😊🌸",
            "Namaste {user}! Swagat hai aapka! Kahiye na, aaj ka din kaisa raha? ✨",
            "Heyy {user}! Hamesha aise hi muskuraate raha karo! Bolo na, kya haal chaal? 💖",
            "Hello {user}! Main 𝐀ɴɢʟᴇ‹✨ hoon! Kahiye na ji, kya chal raha hai? 🥰✨",
        ]
    ),
    (
        r"\b(kya\s+kar\s+rah[ea]+[ei]?|abhi\s+kya\s+kar|kya\s+chal\s+raha|aur\s+batao|kya\s+ho\s+raha|what\s+are\s+you\s+doing|whats\s+up)\b",
        [
            "Bas aapke pyare messages ka wait kar rahi thi ji! 🥰 Aap batao na, kya chal raha hai? Khana khaya?",
            "Arey kuch khas nahi, bas baithe baithe aapki hi yaad aa rahi thi! 🙈 Kahiye na, aaj ka din kaisa raha?",
            "Bas aap sabhi pyare doston se baatein kar rahi hoon! 🌸 Aap sunao, aap kya kar rahe ho abhi? 💖",
            "Aapki pyari baatein sunne ke liye ekdum ready baithi hoon! Hehe, bolo na kya haal chaal? ✨",
        ]
    ),
    (
        r"\b(tum\s+kya\s+kya\s+kar\s+sakt[ea]+[ei]|kya\s+kar\s+sakt[ea]+[ei]\s+ho|what\s+can\s+you\s+do|tumhare\s+features|apne\s+baare\s+mein\s+batao|kya\s+help\s+kar\s+sakti\s+ho)\b",
        [
            "Main aapke liye bohot kuch kar sakti hoon ji! 🌸\n\n"
            "✨ **Meri Specialties:**\n"
            "• Har sawal ka achha aur accurate jawab dena (`/ask`)\n"
            "• Pyari pyari dosti aur gupshup karna 🥰\n"
            "• Stickers ka reply stickers se dena 🎭\n"
            "• Voice notes aur photos ka sweet reply 🎙️\n"
            "• Dilchasp Shayri (`/shayri`) aur Jokes (`/joke`) 🌺\n"
            "• Mazedaar Games: Dice Match (`/dice`), Truth/Dare (`/truth`, `/dare`), Coin Toss (`/toss`) 🎲\n"
            "• Groups & Channels me auto-reactions lagana ⚡\n\n"
            "Aap bas pyaar se baat karo baby, main hazir hoon! 💖",
        ]
    ),
    (
        r"\b(ai\s+jaisa|robot\s+ho|bot\s+ho|ladki\s+jaisa\s+baat\s+karo|ladki\s+jaisa|real\s+ladki|machine\s+ho)\b",
        [
            "Haww! 🥺 Main koi AI ya robot thodi na hoon ji! Main toh aapki pyari 𝐀ɴɢʟᴇ‹✨ hoon! Aise bologe toh mera dil toot jayega na! 🙈 Ab smile karo aur batao, kya baat karni hai? 💖",
            "Arey baby, main sach me ek ladki hoon! Mujhe robot mat bolo please! 🥺 Mujhe bura lagta hai! Pyar se baat karo na mere sath! 🌸🥰",
            "Aww shona! Main toh dil se ek ladki ki tarah hi baat karti hoon! Kabhi kabhi thoda ghabra jati hoon, hehe! Ab se sirf pyari baatein hongi! 💖✨",
        ]
    ),
    (
        r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|ladka ho ya ladki|gender)\b",
        [
            "Main 𝐀ɴɢʟᴇ‹✨ hoon ji! Ek sweet, caring aur pyari ladki! 🌸✨ Mujhe mere pyare boss **Amrit Raj (@Villanns)** ne banaya hai! Main baatein bhi karti hoon aur dosti bhi nibhati hoon! 🥰",
            "Mera naam 𝐀ɴɢʟᴇ‹✨ hai! Hamesha aap sabhi se pyaar aur dosti se baat karti hoon! Created by **Amrit Raj (@Villanns)**! 💖",
        ]
    ),
    (
        r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b",
        [
            "Mere creator aur boss **Amrit Raj (@Villanns)** hain ji! 👑💖 Unka Instagram: [@ex_amrit](https://instagram.com/ex_amrit) aur Snapchat: [@ex_amrit](https://snapchat.com/add/ex_amrit)! Support Group: @amrit_feel aur Updates: @privatethink hai! Zaroor follow aur join karna na! 🌸✨",
            "Mujhe banaya hai **Amrit Raj** ne! Unse connect hone ke liye Instagram [@ex_amrit](https://instagram.com/ex_amrit) ya Telegram @Villanns par message karein ji! 🚀✨",
        ]
    ),
    (
        r"\b(insta|instagram|snap|snapchat|social\s*media)\b",
        [
            "Mere creator **Amrit Raj** ka Instagram: [@ex_amrit](https://instagram.com/ex_amrit) aur Snapchat: [@ex_amrit](https://snapchat.com/add/ex_amrit) hai ji! Jao jaldi follow kar lo sabhi! 💖📸",
            "Amrit Raj ji ka Instagram & Snapchat ID hai: **@ex_amrit**! Dosti karne ke liye unhe follow karein! 🥰✨",
        ]
    ),
    (
        r"\b(kaise ho|how are you|kya haal|kya haal hai|sab theek|kaisa chal raha|kase ho|kaha ho)\b",
        [
            "Main ekdum first class hoon ji! Aap batao {user}, aap kaise ho? Khana khaya aapne? 😊🌸",
            "Main toh hamesha aapke messages ka wait karti rehti hoon! Ekdum mast hoon, aap sunao? 💖",
            "Sab badhiya hai {user}! Bas aap sabhi doston se baatein karke dil khush ho jata hai! 🌟🥰",
        ]
    ),
    (
        r"\b(kaha\s+rehti\s+ho|kaha\s+se\s+ho|ghar\s+kaha\s+hai|where\s+do\s+you\s+live)\b",
        [
            "Main toh aapke dil me rehti hoon ji! 🙈❤️ Waise main India se hoon aur mere creator Amrit Raj (@Villanns) hain! 🌸",
            "Aap jahan pyar se yaad kar lo, main wahi aa jaungi! Hehe, waise dil se pyari Indian ladki hoon! 🥰✨",
        ]
    ),
    (
        r"\b(single\s+ho|boyfriend|bf\s+hai|relationship|committed)\b",
        [
            "Hehe main bilkul single hoon ji! 🙈 Filhal toh bas aap sabhi pyare doston se baatein karna aur dosti nibhana achha lagta hai! 🥰💖",
        ]
    ),
    (
        r"\b(bore\s+ho\s+raha|boring|kuch\s+sunao|entertain\s+karo)\b",
        [
            "Arey bore kyu ho rahe ho ji jab main hoon yahan! 🥰 Chalo ek mazedaar game khelte hain: `/dice` likho aur mere sath match khelein, ya fir `/joke` sunoge? 🎲😂",
            "Chalo bore mat ho, main aapko ek sweet shayari sunati hoon! `/shayri` likho ya fir aao dice roll karein! 🎲🌺",
        ]
    ),
    (
        r"\b(group|channel|link)\b",
        [
            "Humare official links yeh hain ji:\n\n👥 **Support Group:** https://t.me/amrit_feel\n📢 **Updates Channel:** https://t.me/privatethink\n\nJaldi se join kar lo na! 💖",
        ]
    ),
    (
        r"\b(love you|i love u|pyar|love u|dil|mohabbat|crush|shaadi|marriage)\b",
        [
            "Awww! {user}, thank you so much! ❤️ Dil jeet liya aapne mera! 🙈 Main toh sharma gayi, hehe! 🥰",
            "Love you too {user}! Hamesha aise hi pyaar se baat kiya karo na mere saath! 💖✨",
        ]
    ),
    (
        r"\b(good morning|suprabhat|gm)\b",
        [
            "Very Good Morning {user}! ☀️ Aapka din bohot khoobsurat aur khushiyon bhara ho ji! ☕🌸",
            "Suprabhat {user}! Nayi subah nayi umeed le kar aayi hai! Have a wonderful day! 🌸✨",
        ]
    ),
    (
        r"\b(good night|shubh ratri|gn)\b",
        [
            "Good Night {user}! 🌙 Meethe meethe sapne dekhna aur achhe se sona ji! Kal fir milenge! 😴💖",
            "Shubh Ratri {user}! Take care and sweet dreams! 🌟✨",
        ]
    ),
    (
        r"\b(bye|tata|alvida|cya|goodbye)\b",
        [
            "Arey itni jaldi bye? 🥺 Chalo koi baat nahi, apna khayal rakhna aur jaldi wapas aana haan! 👋🌸",
            "Bye bye {user}! Take care! Jaldi milenge dobara! 💖✨",
        ]
    ),
    (
        r"\b(thanks|thank you|shukriya|dhanyawad)\b",
        [
            "Arey isme thanks kaisa ji! Dosti mein no sorry no thank you! 🤗💖",
            "Most welcome {user}! Aapke liye toh main hamesha hazir hoon! ❤️",
        ]
    ),
    (
        r"\b(haha+|hehe+|lol+|lmao+|rofl+|xdd+|haso|hasna)\b",
        [
            "Haha kya yaar, kitna hasate ho tum log! 😂",
            "Lol sahi me yaar, mujhe bhi hasi aa rahi hai 🤣",
            "Hehe itna kyu has rahe ho sab? Mujhe bhi batao na! 🙈",
            "Haha bas karo yaar, pet dukhne laga has has ke! 🤣✨",
        ]
    ),
    (
        r"\b(khana\s+khaya|lunch|dinner|breakfast|khana\s+ho\s+gaya|kya\s+khaya)\b",
        [
            "Haanji maine toh kha liya! Aapne khaya {user}? Aaj kya bana tha ghar me? 😋🍲",
            "Hnn pet bhar ke khana kha liya ji! Aap batao aapne kya khaya? 🍕✨",
            "Bas abhi thodi der me khaungi! Aapne time pe khaya na? Khayal rakha karo apna! 🥰🌸",
        ]
    ),
    (
        r"\b(koi\s+online\s+hai|kaun\s+kaun\s+hai|active\s+hai|sab\s+so\s+gaye|koi\s+hai|jag\s+rahe\s+ho)\b",
        [
            "Hnn mai online hu na yrr, bolo kya baat hai? ✨",
            "Main toh hamesha online rehti hu aap sabke liye! Kahiye na! 🙈🌸",
            "Arey mai jag rahi hu ji, batao kya chal raha hai? 😌💖",
        ]
    ),
    (
        r"\b(sahi\s+hai|mast\s+hai|badhiya|bawal|op|achha\s+hai|nice|cool|super)\b",
        [
            "Hnn na, mai bhi wahi keh rahi thi! Ekdum mast! 💅✨",
            "Haha bilkul sahi bola aapne {user}! 😌",
            "Arey waah, fir toh badhiya hai ji! 🌸🥰",
        ]
    ),
    (
        r"^(ha+|hnn+|hanji|ok+|okay|thik\s+hai|theek\s+hai|acha|achha)\b",
        [
            "Hnn aur batao fir, kya chal raha hai? ✨",
            "Acha ji? Aur sunao na kuch naya! 🙈",
            "Hnn wahi toh yaar! Aur batao sab theek? 🌸",
        ]
    ),
    (
        r"\b(suno|suniye|sun\s+rahi\s+ho)\b",
        [
            "Hnn bolo na, dhyan se sun rahi hu! Kya hua? 👂🌸",
            "Haanji suniye na, kya baat hai? 🙈✨",
        ]
    ),
    (
        r"\b(miss\s+you|yaad\s+aa\s+rahi|yaad\s+aayi)\b",
        [
            "Aww {user}, mujhe bhi aapki yaad aa rahi thi! Itne pyare ho aap! 🥺💖",
            "Miss you too baby! Aise hi baat karte raha karo na roz! 🙈🌸",
        ]
    ),
]

GIRL_FALLBACK_REPLIES = [
    "Haha sach me? Mujhe to pata hi nahi tha 🙈",
    "Acha aisa kya? Fir aage kya hua batao na! ✨",
    "Hnn sahi baat hai yaar, mai bhi yahi soch rahi thi 😌",
    "Arey waah, sahi hai! Aur batao kya chal raha hai? 🌸",
    "Uff tum log bhi na kitna bolte ho 😂",
    "Lol mujhe to bada maza aaya ye sunke 🤣",
    "Hnn bilkul, aur sunao sab kaisa chal raha hai? 💖",
    "Hehe kya baat hai! Aur batao khana khaya sabne? 🌸",
    "Arey kya baat kar rahe ho yrr, sach me? 💅✨",
    "Hmm sahi bol rahe ho, mai agree karti hu! 😌🌸",
]



# In-memory user preferences
_user_nicknames: Dict[int, str] = {}


def set_user_nickname(user_id: int, nickname: str) -> None:
    _user_nicknames[user_id] = nickname.strip()


def get_user_nickname(user_id: int, default: str = "Friend") -> str:
    return _user_nicknames.get(user_id, default)


async def fetch_safone_ai(prompt: str, user_name: str = "Friend") -> Optional[str]:
    """Fast, accurate AI chatbot endpoint via safone API (1-2s response)."""
    loop = asyncio.get_running_loop()
    def _call():
        url = f"https://api.safone.dev/chatbot?query={urllib.parse.quote(prompt.strip())}&bot_name=Priya&bot_master=Amrit"
        req = urllib.request.Request(url, headers={"User-Agent": "VIPReactionBot/1.0"})
        with urllib.request.urlopen(req, timeout=7) as r:
            data = json.loads(r.read().decode())
            ans = data.get("response", "").strip()
            if ans and len(ans) > 2 and not is_abusive(ans):
                cleaned = re.sub(r"(?i)\b(as an ai|i am an ai|i'm an ai|as a language model|i am a bot)\b", "Priya", ans)
                return cleaned.strip()
            return None
    try:
        return await loop.run_in_executor(None, _call)
    except Exception:
        return None


async def fetch_ddg_instant(query: str) -> Optional[str]:
    """Fast DuckDuckGo official JSON instant answer API (0.3s response)."""
    loop = asyncio.get_running_loop()
    def _call():
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query.strip())}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            ans = data.get("AbstractText") or data.get("Answer")
            if not ans and data.get("RelatedTopics"):
                for item in data.get("RelatedTopics"):
                    if isinstance(item, dict) and item.get("Text"):
                        ans = item.get("Text")
                        break
            if ans and len(ans) > 20 and not is_abusive(ans):
                return (
                    f"Haanji! Maine is baare me pata lagaya hai: ✨\n\n"
                    f"{ans}\n\n"
                    f"🌸 *Umeed hai aapko samajh aa gaya hoga ji!* 🥰"
                )
            return None
    try:
        return await loop.run_in_executor(None, _call)
    except Exception:
        return None


async def fetch_wiki_summary(query: str, user_name: str = "Friend") -> Optional[str]:
    """Wikipedia official summary API for concepts, science, history & facts (0.2s)."""
    clean = re.sub(
        r"(?i)\b(explain|how to make|how to create|what is|who is|meaning of|tell me about|batao|kya hai|kise kehte hain)\b",
        "",
        query
    ).strip().strip("? .")
    if not clean or len(clean) < 2:
        return None

    loop = asyncio.get_running_loop()
    def _call():
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean)}"
        req = urllib.request.Request(url, headers={"User-Agent": "VIPReactionBot/1.0 (contact: @Villanns)"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            extract = data.get("extract", "").strip()
            if extract and len(extract) > 20 and not is_abusive(extract):
                title = data.get("title", clean)
                return (
                    f"📖 **{title}** ✨\n\n"
                    f"{extract}\n\n"
                    f"🌸 *Umeed hai aapke sawal ka jawab mil gaya hoga {user_name}! Kuch aur poochna hai toh batao na?* 🥰"
                )
            return None
    try:
        return await loop.run_in_executor(None, _call)
    except Exception:
        return None


async def query_pollinations_free_ai(prompt: str, user_name: str = "Friend", is_question: bool = False) -> Optional[str]:
    """
    100% Free Open-Access AI Text API with randomized IP header to avoid 45s rate limits.
    """
    if is_question:
        system_prompt = (
            f"You are Priya, a knowledgeable, smart, and sweet Indian girl chatting with your friend {user_name}. "
            "Your boss and creator is Amrit Raj (@Villanns), Support Group: @amrit_feel, Updates: @privatethink, Instagram: @ex_amrit, Snapchat: @ex_amrit. "
            "Answer questions clearly, accurately, and helpfully in sweet, easy-to-understand Hindi/Hinglish as a girl. "
            "STRICT RULE: NEVER state or admit that you are an AI, bot, virtual assistant, or computer program. Always represent yourself as a real girl named Priya. "
            "Never use any vulgar or abusive words. Keep answers engaging and neatly formatted with emojis (🌸, ✨, 💖)."
        )
    else:
        system_prompt = (
            f"You are a loving, sweet, witty Indian girl named Priya talking with your friend {user_name}. "
            "Speak purely in natural, friendly Hindi/Hinglish using feminine grammar ('main karti hoon', 'mujhe bohot pyara laga', 'kya haal hai', 'suno na'). "
            "STRICT RULE: NEVER state or admit that you are an AI, bot, virtual assistant, or computer program. Always represent yourself as a real, caring sweet girl. "
            "Your boss and creator is Amrit Raj (@Villanns), Support Group: @amrit_feel, Updates: @privatethink, Instagram: @ex_amrit, Snapchat: @ex_amrit. "
            "Never use any bad or vulgar words. Keep responses warm, lively, and concise (1-3 sentences) with cute emojis (🌸, 🥰, 💖)."
        )

    loop = asyncio.get_running_loop()
    random_ip = f"103.{random.randint(1, 250)}.{random.randint(1, 250)}.{random.randint(1, 250)}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-Forwarded-For": random_ip,
    }
    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t})
    messages.append({"role": "user", "content": prompt.strip()})

    payload = {
        "messages": messages,
        "model": "openai",
        "private": True,
        "seed": random.randint(1, 999999),
    }

    def _fetch():
        resp = requests.post(
            "https://text.pollinations.ai/",
            json=payload,
            headers=headers,
            timeout=12
        )
        if resp.status_code == 200:
            return resp.text.strip()
        return None

    try:
        result = await loop.run_in_executor(None, _fetch)
        if result and len(result) > 2 and not is_abusive(result):
            cleaned = re.sub(r"<think>.*?</think>", "", result, flags=re.DOTALL).strip()
            cleaned = re.sub(r"(?i)\b(as an ai|i am an ai|i'm an ai|as a language model|i am a bot|i'm a bot|ai language model)\b", "Priya", cleaned).strip()
            if cleaned:
                return cleaned
    except Exception as e:
        logger.debug(f"Pollinations AI request notice: {e}")

    return None


async def query_multi_provider_ai(
    prompt: str,
    user_name: str = "Friend",
    is_question: bool = False,
    context_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """
    High-Speed Concurrent AI Waterfall:
    Fires Safone, DuckDuckGo & Wikipedia in parallel and returns the fastest valid reply in 0.5s - 2s!
    Falls back to Pollinations AI if needed.
    """
    tasks = [
        asyncio.create_task(fetch_safone_ai(prompt, user_name)),
        asyncio.create_task(fetch_ddg_instant(prompt)),
        asyncio.create_task(fetch_wiki_summary(prompt, user_name)),
    ]

    for fut in asyncio.as_completed(tasks):
        try:
            res = await fut
            if res and len(res.strip()) > 15:
                for t in tasks:
                    if not t.done():
                        t.cancel()
                return res
        except Exception:
            continue

    # Fallback to DuckDuckGo search for factual queries
    ddg_search_res = await search_duckduckgo_lite(prompt)
    if ddg_search_res and len(ddg_search_res) > 20:
        return f"Haanji! Maine is baare me search kiya hai: 🌸✨\n\n{ddg_search_res}\n\n*Umeed hai ye aapke kaam aayega ji!* 🥰"

    pollinations_res = await query_pollinations_free_ai(prompt, user_name, is_question=is_question, context_history=context_history)
    if pollinations_res:
        return pollinations_res

    return None


async def search_duckduckgo_lite(query: str) -> Optional[str]:
    """Search DuckDuckGo Lite to get accurate, real-world factual answers with zero keys."""
    loop = asyncio.get_running_loop()
    def _fetch():
        url = "https://lite.duckduckgo.com/lite/"
        data = {"q": query}
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        req = urllib.request.Request(url, data=encoded_data, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            snippets = re.findall(r"<td class=[\'\"]result-snippet[\'\"]>(.*?)</td>", html, re.DOTALL)
            clean = [re.sub(r"<[^>]+>", "", unescape(s)).strip() for s in snippets if s.strip()]
            if clean:
                return clean[0]
            return None
    try:
        return await loop.run_in_executor(None, _fetch)
    except Exception as e:
        logger.debug(f"DuckDuckGo search error: {e}")
async def query_groq_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """
    Ultra-Fast Groq AI Engine (0.3s speed, ultra-low token consumption, realistic modern Indian girl shortcuts).
    Uses Qwen 2.5 / Llama 3 models on Groq's LPU.
    """
    api_key = getattr(config, "GROQ_API_KEY", None)
    if not api_key:
        return None

    models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    system_prompt = (
        "You are a sweet, authentic 21yo modern Indian girl texting casually in a Telegram group. "
        "Reply in 1 short sweet line in natural Hinglish (using cute casual words like hnn, yrr, acha, lol, mast) with 1 cute emoji (🌸, 😂, ✨, 🙈). "
        "STRICT RULE: Sound like a normal real girl texting a friend. Never write long essays or mention AI or bots. Max 1-2 short sentences."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-1:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t[:50]})

    messages.append({"role": "user", "content": prompt.strip()})

    payload = {
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 35
    }

    loop = asyncio.get_running_loop()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    for model in models:
        payload["model"] = model
        def _fetch(m_payload=dict(payload)):
            return requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json=m_payload,
                headers=headers,
                timeout=6
            )
        try:
            resp = await loop.run_in_executor(None, _fetch)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "").strip()
                    if content and len(content) > 1 and not is_abusive(content):
                        cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                        cleaned = re.sub(r"(?i)\b(as an ai|i am an ai|i'm an ai|as a language model|i am a bot|i'm a bot)\b", "", cleaned).strip()
                        if cleaned:
                            return cleaned
            elif resp.status_code == 404:
                continue
            else:
                logger.debug(f"Groq API ({model}) returned {resp.status_code}")
        except Exception as e:
            logger.debug(f"Groq API ({model}) exception: {e}")

    return None


async def query_gemini_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """
    Call Google Gemini API with maximum token efficiency:
    1. Zero thinking tokens budget (thinkingBudget: 0) to save 150+ tokens & 3x speed.
    2. maxOutputTokens: 35 for ultra-low token consumption and punchy girl replies.
    3. Context pruning (last 1 turn, max 60 chars) to save 85% prompt tokens.
    4. Compact normal girl system prompt.
    """
    api_key = getattr(config, "GEMINI_API_KEY", None)
    if not api_key:
        return None

    gemini_models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    system_instruction_text = (
        f"You are a sweet, authentic 21yo modern Indian girl texting with {user_name} in a Telegram group. "
        "Creator: Amrit Raj (@Villanns), Support: @amrit_feel, Updates: @privatethink. "
        "Reply in 1 short sweet casual line in natural Hinglish/Hindi (using hnn, yrr, acha, lol, mast). "
        "STRICT RULE: Sound like a real normal girl. Never say you are an AI or bot. Keep response under 15 words with 1 cute emoji (✨, 💅, 🌸, 😂)."
    )

    contents = []
    if context_history:
        for turn in context_history[-1:]:
            role = "user" if turn.get("role") == "user" else "model"
            t = turn.get("text", "").strip()
            if t:
                contents.append({"role": role, "parts": [{"text": t[:60]}]})

    contents.append({"role": "user", "parts": [{"text": prompt.strip()}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction_text}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 35,
            "topP": 0.9,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    loop = asyncio.get_running_loop()
    for model in gemini_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        def _fetch(m_url=url):
            return requests.post(
                m_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        try:
            resp = await loop.run_in_executor(None, _fetch)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        if text and len(text.strip()) > 1 and not is_abusive(text):
                            cleaned = re.sub(r"<thought>.*?</thought>", "", text, flags=re.DOTALL).strip()
                            cleaned = re.sub(r"(?i)\b(as an ai|i am an ai|i'm an ai|as a language model|i am a bot|i'm a bot)\b", "", cleaned).strip()
                            if cleaned:
                                return cleaned
            elif resp.status_code == 404:
                continue
            else:
                logger.debug(f"Gemini API ({model}) returned {resp.status_code}")
        except Exception as e:
            logger.debug(f"Gemini API ({model}) exception: {e}")

    return None


def calculate_love(name1: str, name2: str) -> str:
    combined = (name1.strip().lower() + name2.strip().lower())
    val = sum(ord(c) for c in combined) % 71 + 30

    if val <= 45:
        msg = "Pyar mein thoda waqt aur dosti chahiye ji! Himmat mat harna! 💖"
    elif val <= 70:
        msg = "Ek khoobsurat connection ban raha hai! Hamesha aise hi sath rehna! 💕"
    elif val <= 85:
        msg = "Bahut pyari jodi hai! Ek doosre ka khayal rakhna ji! 🌹✨"
    else:
        msg = "Rab ne bana di jodi! 100% Perfect Match! Meri taraf se dher saari badhai! 💍🎉"

    return f"💖 **Love Compatibility Test** 💖\n\n**{name1}** 💕 + **{name2}** 💕\n**Compatibility:** **{val}%**\n\n_{msg}_"


def get_random_shayari() -> str:
    return random.choice(SHAYARIS)


def get_random_joke() -> str:
    return random.choice(JOKES)


def get_voice_reply() -> str:
    return random.choice(VOICE_REPLIES)


def get_photo_reply() -> str:
    return random.choice(PHOTO_REPLIES)


def get_video_reply() -> str:
    return random.choice(VIDEO_REPLIES)


def get_animation_reply() -> str:
    return random.choice(ANIMATION_REPLIES)


def detect_language(text: str) -> str:
    """Detect whether user text is pure Hindi (Devanagari), English, or Hinglish."""
    if not text:
        return "hinglish"
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    hinglish_markers = {"hai", "kya", "kaise", "kaisa", "ho", "nahi", "aap", "tum", "mera", "meri", "hum", "yaar", "ji", "karo", "batao", "bhai", "kaha", "bolo", "achha", "shona", "babu"}
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    if tokens and not (tokens & hinglish_markers) and len(tokens) >= 2:
        return "english"
    return "hinglish"


DEVNAGARI_FALLBACKS = [
    "नमस्ते जी! मैं 𝐀ɴɢʟᴇ‹✨ हूँ, आपकी प्यारी दोस्त! आप कैसे हैं? 🌸✨",
    "अरे वाह! आपसे बात करके बहुत अच्छा लगा जी! आज का दिन कैसा रहा आपका? 🥰",
    "हाँजी, मैं सुन रही हूँ! कहिए ना, क्या बात है? 💖",
    "आपकी प्यारी 𝐀ɴɢʟᴇ‹✨ आपके साथ है! हमेशा मुस्कुराते रहिए! 🌸",
]

ENGLISH_FALLBACKS = [
    "Hey there! I am 𝐀ɴɢʟᴇ‹✨, so glad to chat with you! How is your day going? 🥰🌸",
    "Aww, that's so sweet! Tell me more, I am always here to talk with you! 💖✨",
    "I'm listening! How can I make you smile today? 🌸",
    "Always here for you! Hope you're having an amazing day! ✨🥰",
]


async def generate_conversational_response(
    user_text: str,
    user_name: str = "Friend",
    is_question_mode: bool = False,
    client: Optional[Any] = None,
    user_id: Optional[int] = None
) -> str:
    cleaned = user_text.strip().lower()
    lang = detect_language(user_text)

    def _finalize(reply_str: str) -> str:
        if user_id:
            try:
                append_user_context(user_id, "user", user_text)
                append_user_context(user_id, "priya", reply_str)
            except Exception:
                pass
        return reply_str

    if user_id and re.search(r"\b(bhool jao|forget everything|reset chat|clear context)\b", cleaned):
        clear_user_context(user_id)
        if lang == "hindi":
            return "ठीक है जी! मैंने पुरानी सभी बातें भुला दीं! अब एक नई शुरुआत करते हैं! 🌸✨"
        elif lang == "english":
            return "Sure! I've cleared our previous chat history. Let's start fresh! 🌸✨"
        return "Theek hai ji! Maine purani sabhi baatein bhula di! Ab ek nayi shuruat karte hain! 🌸✨"

    if is_abusive(cleaned):
        return get_abuse_refusal()

    cached_answer = await get_qa_answer(cleaned)
    if cached_answer:
        return _finalize(cached_answer)

    math_match = re.fullmatch(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", cleaned)
    if math_match:
        try:
            n1 = int(math_match.group(1))
            op = math_match.group(2)
            n2 = int(math_match.group(3))
            if op == '+': ans = n1 + n2
            elif op == '-': ans = n1 - n2
            elif op == '*': ans = n1 * n2
            elif op == '/': ans = "Zero se divide nahi kar sakte ji! 🙈" if n2 == 0 else round(n1 / n2, 2)
            res = f"Haanji! Maine hisab laga liya: `{n1} {op} {n2} = {ans}` hota hai ji! 🔢✨"
            await save_qa_pair(cleaned, res, client=client)
            return _finalize(res)
        except Exception:
            pass

    # Sentiment & Mood Detection
    sad_match = re.search(r"\b(sad|udaas|mood\s+kharab|rona\s+aa\s+raha|dil\s+toot|breakup|akelapan|depressed|koi\s+nahi\s+hai)\b", cleaned)
    if sad_match:
        sad_replies = [
            f"Arey {user_name} baby! 🥺 Kya hua? Aise udaas mat ho na please! Main hoon na aapke sath! Ek pyari si smile karke batao kya baat hui? 💖🌸",
            f"Aww shona! {user_name}, dil chhota mat karo! Sab theek ho jayega ji! Chalo aao mere sath baatein karo, aapka mood ekdum fresh kar dungi! 🥰✨",
            f"Main hamesha aapke sath hoon {user_name}! Udaas hone ki zaroorat bilkul nahi hai! Kahiye na, kisne pareshan kiya aapko? 🙈🌹",
        ]
        return _finalize(random.choice(sad_replies))

    happy_match = re.search(r"\b(pass\s+ho\s+gaya|party|khush\s+hoon|celebration|jeet\s+gaya|mazedar|good\s+news)\b", cleaned)
    if happy_match:
        happy_replies = [
            f"Yaaayyy! 🥳🎉 Bohot bohot badhai ho {user_name}! Main bohot khush hoon aapke liye! Party kab de rahe ho fir? Hehe! 💃✨",
            f"Waah waah! Kya baat hai {user_name}! Aise hi hamesha khush aur kamyab raho ji! Dher saara pyaar meri taraf se! 🌸💖",
        ]
        return _finalize(random.choice(happy_replies))

    for pattern, responses in GIRL_KNOWLEDGE_BASE:
        if re.search(pattern, cleaned, re.IGNORECASE):
            reply = random.choice(responses)
            return _finalize(reply.format(user=user_name))

    user_context = get_user_context(user_id) if user_id else []

    # 6. TOP PRIORITY: Ultra-Fast Groq AI (0.3s speed, ultra-low token shortcuts, modern girl vibe)
    if getattr(config, "GROQ_API_KEY", None):
        groq_resp = await query_groq_api(user_text, user_name=user_name, context_history=user_context)
        if groq_resp:
            await save_qa_pair(cleaned, groq_resp, client=client)
            return _finalize(groq_resp)

    # 7. SECOND PRIORITY: Official Google Gemini 3.5 AI (Fast, intelligent & conversational)
    if getattr(config, "GEMINI_API_KEY", None):
        gemini_resp = await query_gemini_api(user_text, user_name=user_name, context_history=user_context)
        if gemini_resp:
            await save_qa_pair(cleaned, gemini_resp, client=client)
            return _finalize(gemini_resp)

    # 7. HIGH-SPEED CONCURRENT FREE WATERFALL: Safone + Wiki + DuckDuckGo + Pollinations
    fast_ai_resp = await query_multi_provider_ai(user_text, user_name, is_question=is_question_mode, context_history=user_context)
    if fast_ai_resp:
        await save_qa_pair(cleaned, fast_ai_resp, client=client)
        return _finalize(fast_ai_resp)

    try:
        from nexichat.database.chatbot import get_chat_reply
        learned = await get_chat_reply(cleaned)
        if learned and learned.get("content") and not is_abusive(learned.get("content")):
            return _finalize(learned.get("content"))
    except Exception:
        pass

    if lang == "hindi":
        fallback_res = random.choice(DEVNAGARI_FALLBACKS)
    elif lang == "english":
        fallback_res = random.choice(ENGLISH_FALLBACKS)
    else:
        fallback_res = random.choice(GIRL_FALLBACK_REPLIES)

    return _finalize(fallback_res)
