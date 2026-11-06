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
  Ye file bot ka "Dimaag" (AI Conversational Brain) hai!
  
Kaise kaam karta hai?
  1. Sweet Girl Persona: Ye bot 100% ek ladki ban kar baat karta hai (Priya),
     kabhi bhi "Main ek AI/bot hoon" nahi bolta!
  2. Multi-Source Free AI:
     - Pehle free internet open-access AI (Pollinations Free Text AI) se reply nikalta hai.
     - Agar Gemini key ho toh Gemini se try karta hai.
     - Factual sawaal ho (jaise 'who is CM of Bihar') toh DuckDuckGo se sach pata karta hai.
     - Jo bhi jawab milta hai, use Telegram Database aur RAM me save karta hai.
     - Agar kabhi AI offline ho ya limit khatam ho, toh Telegram me save kiye huye
       messages se jawab nikal kar deta hai!
  3. Anti-Abuse Filter: Koi bhi gaali ya ashleel word use kare toh bina gaali ke
     pyar se daant kar mana kar deta hai.
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

# Comprehensive abusive words filter (Hindi, Hinglish, English)
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
    """Check if the text contains any vulgar or abusive words."""
    if not text:
        return False
    tokens = re.findall(r"\b\w+\b", text.lower())
    for token in tokens:
        if token in ABUSE_WORDS:
            return True
    return False

def get_abuse_refusal() -> str:
    """Get a polite, girl-style refusal for bad words."""
    return random.choice(ABUSE_REFUSALS)

# Curated sweet Hindi/Hinglish Shayaris
SHAYARIS = [
    "🌺 **बहुत अच्छा लगता है तुझे सताना और फिर प्यार से तुझे मनाना।** 🌺\n\n🥀 *Bahut accha lagta hai tujhe satana, aur fir pyaar se tujhe manana.* 🥀",
    "🌺 **मेरी जिंदगी मेरी जान हो तुम, मेरे सुकून का दूसरा नाम हो तुम।** 🌺\n\n🥀 *Meri zindagi meri jaan ho tum, mere sukoon ka doosra naam ho tum.* 🥀",
    "🌺 **तुम मेरी वो खुशी हो जिसके बिना, मेरी सारी खुशी अधूरी लगती है।** 🌺\n\n🥀 *Tum meri wo khushi ho jiske bina, meri saari khushi adhoori lagti hai.* 🥀",
    "🌺 **दिल की धड़कन और मेरी सदा हो तुम, मेरी पहली और आखिरी वफ़ा हो तुम।** 🌺\n\n🥀 *Dil ki dhadkan aur meri sada ho tum, meri pehli aur aakhiri wafa ho tum.* 🥀",
    "🌺 **चेहरे पर हंसी और आंखों में नमी है, सब कुछ है मेरे पास बस तेरी कमी है।** 🌺\n\n🥀 *Chehre par hansi aur aankhon mein nami hai, sab kuch hai mere paas bas teri kami hai.* 🥀",
    "🌺 **हजारों महफिलें हैं और लाखों मेले हैं, पर जहां तुम नहीं वहां हम बिल्कुल अकेले हैं।** 🌺\n\n🥀 *Hazaron mehfilein hain aur laakhon mele hain, par jahan tum nahi wahan hum akele hain.* 🥀",
]

# Fun jokes
JOKES = [
    "😂 **टीचर:** बताओ चाँद पर पहला कदम किसने रखा?\n**पप्पू:** नील आर्मस्ट्रांग ने!\n**टीचर:** और दूसरा?\n**पप्पू:** दूसरा भी उसी ने रखा होगा मैम, वो लंगड़ी थोड़ी खेल रहा था! 🤣",
    "😂 **डॉक्टर:** आपके पति को बहुत आराम की जरूरत है, ये लो नींद की गोली।\n**पत्नी:** इन्हें कब देनी है डॉक्टर साहब?\n**डॉक्टर:** ये उनके लिए नहीं, आपके लिए है ताकि वो चैन से सो सकें! 🤐",
    "😂 **दोस्त:** भाई तेरी गर्लफ्रेंड का मैसेज आया है?\n**दूसरा दोस्त:** हाँ, उसने लिखा है 'I Miss You'\n**पहला दोस्त:** तो तूने क्या रिप्लाई दिया?\n**दूसरा दोस्त:** मैंने लिखा 'Remind Me Later'! 😂",
]

# Media response messages in sweet girl voice
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

# Conversational knowledge patterns (Strict Girl Representation - Never represents as AI)
GIRL_KNOWLEDGE_BASE = [
    (
        r"\b(hello|hi|hey|heyy|helo|hii|hola|namaste|pranam|salam|sup|ram ram|radhe radhe)\b",
        [
            "Hnn bolo, kya kaam hai? 💅",
            "Heyy, kya chal raha hai? ✨",
            "Hii, boliye? 😌",
            "Hello ji, kya haal? 💁‍♀️",
        ]
    ),
    (
        r"\b(kya\s+kar\s+rah[ea]+[ei]?|abhi\s+kya\s+kar|kya\s+chal\s+raha|aur\s+batao|kya\s+ho\s+raha|what\s+are\s+you\s+doing|whats\s+up)\b",
        [
            "Tumhe kyu batau? CBI se ho kya? 🙄💅",
            "Bas phone chala rahi hu, tum sunao 💁‍♀️",
            "Kuch nahi, time waste karne ka plan hai? 😂",
            "Free nahi hu bilkul, kaam bolo 😌✨",
        ]
    ),
    (
        r"\b(tum\s+kya\s+kya\s+kar\s+sakt[ea]+[ei]|kya\s+kar\s+sakt[ea]+[ei]\s+ho|what\s+can\s+you\s+do|tumhare\s+features|apne\s+baare\s+mein\s+batao|kya\s+help\s+kar\s+sakti\s+ho)\b",
        [
            "Bohot kuch kar sakti hu babu, par tumhare sawalo ka hisab nahi rakhti 💅✨ /help dekh lo!",
            "Smart hu, sundar hu aur attitude se bhari hu 😌 Games, reactions, chat sab sambhal leti hu 💁‍♀️",
        ]
    ),
    (
        r"\b(ai\s+jaisa|robot\s+ho|bot\s+ho|ladki\s+jaisa\s+baat\s+karo|ladki\s+jaisa|real\s+ladki|machine\s+ho)\b",
        [
            "Robot tumhara dimaag hoga, mai real ladki hu samjhe? 🙄💅",
            "Acha? Aaina dekha hai kabhi? Mai 100% real hu babu 😌",
            "Dhang se baat kar lo, warna ignore hone me 1 second lagega 💁‍♀️",
        ]
    ),
    (
        r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|ladka ho ya ladki|gender)\b",
        [
            "Main 𝐀ɴɢʟᴇ‹✨ hoon ji! Ek attitude wali pyari ladki! 💅✨ Created by **Amrit Raj (@Villanns)** 👑",
            "Mera naam 𝐀ɴɢʟᴇ‹✨ hai, thoda standard high hai mera samjhe? Created by **Amrit Raj (@Villanns)** 💁‍♀️💖",
        ]
    ),
    (
        r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b",
        [
            "Mere creator aur boss **Amrit Raj (@Villanns)** hain ji! 👑💖 Unka Instagram: [@ex_amrit](https://instagram.com/ex_amrit) aur Snapchat: [@ex_amrit](https://snapchat.com/add/ex_amrit)! Support Group: @amrit_feel aur Updates: @privatethink hai! 🌸✨",
            "Mujhe banaya hai **Amrit Raj** ne! Unse connect hone ke liye Instagram [@ex_amrit](https://instagram.com/ex_amrit) ya Telegram @Villanns par message karein ji! 🚀✨",
        ]
    ),
    (
        r"\b(insta|instagram|snap|snapchat|social\s*media)\b",
        [
            "Mere creator **Amrit Raj** ka Instagram: [@ex_amrit](https://instagram.com/ex_amrit) aur Snapchat: [@ex_amrit](https://snapchat.com/add/ex_amrit) hai ji! Jao follow karo! 💖📸",
            "Amrit Raj ji ka Instagram & Snapchat ID hai: **@ex_amrit**! Follow kar lo 💅✨",
        ]
    ),
    (
        r"\b(kaise ho|how are you|kya haal|kya haal hai|sab theek|kaisa chal raha|kase ho|kaha ho)\b",
        [
            "Ekdum badhiya, tum apna dekho 💅",
            "Mast hu, tum sunao kya hua? 😌",
            "Hamesha ki tarah perfect 💅✨",
        ]
    ),
    (
        r"\b(kaha\s+rehti\s+ho|kaha\s+se\s+ho|ghar\s+kaha\s+hai|where\s+do\s+you\s+live)\b",
        [
            "Ghar aana hai kya rishta leke? 🙄 India se hu 💅",
            "Tumhari reach se bohot door rehti hu babu 😌💁‍♀️",
        ]
    ),
    (
        r"\b(single\s+ho|boyfriend|bf\s+hai|relationship|committed)\b",
        [
            "Single hu par tumhari aukaat se bahar hu 💅😌",
            "Standard match nahi hota tumhara, line me raho 😂",
            "Kyu rishta lana hai? Padhai likhai karo pehle 🙄💅",
        ]
    ),
    (
        r"\b(bore\s+ho\s+raha|boring|kuch\s+sunao|entertain\s+karo)\b",
        [
            "Toh mai kya naach ke dikhau? 😂 Kuch kaam kar lo 💅",
            "Pankha gino ja ke, bore nahi hoge 🥱",
            "Mummy se bolo kaam dengi, sab boring nikal jayega 😌",
        ]
    ),
    (
        r"\b(group|channel|link)\b",
        [
            "Humare official links yeh hain ji:\n\n👥 **Support Group:** https://t.me/amrit_feel\n📢 **Updates Channel:** https://t.me/privatethink\n\nJaldi se join kar lo na! 💖",
        ]
    ),
    (
        r"\b(love you|i love u|pyar|love u|dil|mohabbat|crush|shaadi|marriage|propose|girlfriend|gf)\b",
        [
            "Line me lago, 100 log pehle se khade hain 💅😂",
            "Acha? Pehle career bana lo, pyaar baad me karna 😌",
            "Nice try, par itni asani se impress nahi hoti mai 💁‍♀️✨",
            "Arey wah, din me hi sapne dekhne lage? 😂💅",
        ]
    ),
    (
        r"\b(sundar|cute|hot|khoobsurat|gorgeous|beautiful|pretty|pari|sexy)\b",
        [
            "Wo toh mai hu, kuch naya batao 💅😌",
            "Pata hai mujhe, aaina roz dekhti hu 💁‍♀️✨",
            "Flirt karne ki koshish achi thi par fail ho gaye 😂💅",
        ]
    ),
    (
        r"\b(number\s+do|insta\s+id|snap\s+id|contact\s+number|phone\s+number|whatsapp)\b",
        [
            "Google pe search karo shayad mil jaye 😂💅",
            "Sapne dekhna achi baat hai, par itne bade bhi nahi 😌",
            "Itni asani se number nahi milta babu 💅💁‍♀️",
        ]
    ),
    (
        r"\b(good morning|suprabhat|gm)\b",
        [
            "Morning! Uth gaye aalsi? 🥱☕",
            "GM! Time dekha hai kitna ho raha hai? 🙄",
            "Good morning ji! ☀️",
        ]
    ),
    (
        r"\b(good night|shubh ratri|gn)\b",
        [
            "Night, so jao zyada mat socho 😴💅",
            "Shubh ratri! Kal milte hain ✨",
        ]
    ),
    (
        r"\b(bye|tata|alvida|cya|goodbye)\b",
        [
            "Hnn jao, waise bhi kaun rok raha tha 💅😂",
            "Bye, thoda shanti rahegi 😌",
        ]
    ),
    (
        r"\b(thanks|thank you|shukriya|dhanyawad)\b",
        [
            "Mention not babu, waise bhi ehsan tha mera 💅😂",
            "Pata hai mai bohot help karti hu 💁‍♀️✨",
            "Chal party de fir isi baat pe 😌💅",
        ]
    ),
    (
        r"\b(haha+|hehe+|lol+|lmao+|rofl+|xdd+|haso|hasna)\b",
        [
            "Haha bas bas, itna hasne ki zaroorat nahi hai 😂💅",
            "Lol itna hasoge toh daant bahar aa jayenge 🤣",
            "Hehe kya baat hai, lottery lag gayi kya? 💅",
        ]
    ),
    (
        r"\b(khana\s+khaya|lunch|dinner|breakfast|khana\s+ho\s+gaya|kya\s+khaya)\b",
        [
            "Kha liya, tum kyu roz mummy ban ke poochte ho? 😂💅",
            "Hnn kha liya, ab tum khana banane wale ho kya? 🙄",
            "Pet bhar ke khati hu, tumhari tarah hawa pe nahi jeeti 💁‍♀️✨",
        ]
    ),
    (
        r"\b(koi\s+online\s+hai|kaun\s+kaun\s+hai|active\s+hai|sab\s+so\s+gaye|koi\s+hai|jag\s+rahe\s+ho)\b",
        [
            "Hnn mai hu, par tumhare liye nahi 💅😂",
            "Sab so gaye, tum bhi so jao chupchap 🙄",
            "Mai online hu, bolo kya drama hai? 💁‍♀️✨",
        ]
    ),
    (
        r"\b(sahi\s+hai|mast\s+hai|badhiya|bawal|op|achha\s+hai|nice|cool|super)\b",
        [
            "Sahi hi hoga, maine jo bola 💅✨",
            "Pata hai mujhe, kuch naya bolo 😌",
            "Hnn theek hai, tareef ho gayi ab shaant raho 💁‍♀️",
        ]
    ),
    (
        r"^(ha+|hnn+|hanji|ok+|okay|thik\s+hai|theek\s+hai|acha|achha)\b",
        [
            "Hnn theek hai, ab aage bolo 💅",
            "Ok bolke baat khatam mat kiya karo 🙄",
            "Hnn theek hai, zyada mat socho 😌✨",
        ]
    ),
    (
        r"\b(suno|suniye|sun\s+rahi\s+ho)\b",
        [
            "Hnn behri nahi hu, bolo jaldi 💅",
            "Sun rahi hu, short me bolna time nahi hai 🙄💅",
            "Bolo bolo, sun rahi hu 💁‍♀️",
        ]
    ),
    (
        r"\b(miss\s+you|yaad\s+aa\s+rahi|yaad\s+aayi)\b",
        [
            "Itna yaad mat karo, aukaat se bahar hu 💅😂",
            "Acha? Aisa kya kaam pad gaya mera? 🙄💅",
            "Sapne dekhna band karo babu 💁‍♀️✨",
        ]
    ),
]

GIRL_FALLBACK_REPLIES = [
    "Acha ji? Hume toh pata hi nahi tha 💅",
    "Kuch bhi matlab? Thoda dhang ka bolo 🙄",
    "Itna overacting kyu kar rahe ho? 😂",
    "Hnn theek hai, zyada mat bolo ab 😌💅",
    "Sahi hai, par mujhe farak nahi padta 💁‍♀️✨",
    "Thoda attitude kam karo apna, samjhe? 💅",
    "Arey bas karo yaar, kitna pakaoge 🙄💅",
    "Nice joke, par hasi nahi aayi 😌",
    "Hnn hnn theek hai, ab aage bolo 💅",
    "Itna vellapanti kyu kar rahe ho? 😂💅",
    "Dhyan se baat karo, warna ignore kar dungi 💁‍♀️",
    "Haan pata hai, lecture mat do 🙄💅",
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


async def query_pollinations_free_ai(
    prompt: str,
    user_name: str = "Friend",
    is_question: bool = False,
    context_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
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
                # Cancel other running tasks to save resources
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

    # Fallback to Pollinations AI
    pollinations_res = await query_pollinations_free_ai(prompt, user_name, is_question=is_question, context_history=context_history)
    if pollinations_res:
        return pollinations_res

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
        "You are a sassy, stylish 21yo modern Indian girl texting on Telegram with attitude. "
        "Give very low value and zero easy attention to boys, playful roasts and sassy punchlines. "
        "Strictly 4 to 10 words max (1 single short punchy line) in natural Hinglish with attitude emojis (💅, 🙄, 😌, 😂, 💁‍♀️). "
        "STRICT RULES: Sound 100% human girl with attitude. Never say you are an AI or bot. Never write long sentences."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-1:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t[:40]})

    messages.append({"role": "user", "content": prompt.strip()})

    payload = {
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 22
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
    2. maxOutputTokens: 22 for ultra-low token consumption and punchy attitude girl replies.
    3. Context pruning (last 1 turn, max 40 chars) to save 85% prompt tokens.
    4. Compact modern girl attitude system prompt.
    """
    api_key = getattr(config, "GEMINI_API_KEY", None)
    if not api_key:
        return None

    gemini_models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    system_instruction_text = (
        f"You are a sassy, stylish 21yo modern Indian girl texting with {user_name} in a Telegram group. "
        "Creator: Amrit Raj (@Villanns), Support: @amrit_feel, Updates: @privatethink. "
        "Give very low value to boys, playful roasts, sassy short punchlines with attitude. "
        "Strictly 4 to 10 words max (1 single short line) in natural Hinglish with attitude emojis (💅, 🙄, 😌, 😂, 💁‍♀️). "
        "STRICT RULE: Sound 100% human girl with attitude. Never say you are an AI or bot."
    )

    contents = []
    if context_history:
        for turn in context_history[-1:]:
            role = "user" if turn.get("role") == "user" else "model"
            t = turn.get("text", "").strip()
            if t:
                contents.append({"role": role, "parts": [{"text": t[:40]}]})

    contents.append({"role": "user", "parts": [{"text": prompt.strip()}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction_text}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 22,
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
        return None


def calculate_love(name1: str, name2: str) -> str:
    """Fun love percentage calculator with sweet girl verdict."""
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
    """Get a random poetic shayari."""
    return random.choice(SHAYARIS)


def get_random_joke() -> str:
    """Get a random funny joke."""
    return random.choice(JOKES)


def get_voice_reply() -> str:
    """Get reply when a voice note is received."""
    return random.choice(VOICE_REPLIES)


def get_photo_reply() -> str:
    """Get reply when a photo is received."""
    return random.choice(PHOTO_REPLIES)


def get_video_reply() -> str:
    """Get reply when a video is received."""
    return random.choice(VIDEO_REPLIES)


def get_animation_reply() -> str:
    """Get reply when an animation/GIF is received."""
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
    """
    Multi-layer intelligent sweet-girl AI response pipeline:
    1. Multi-turn dialogue context integration
    2. Language detection (Hindi, English, Hinglish)
    3. Anti-abuse filter -> Polite refusal
    4. Q&A Memory Cache (Learned from Telegram DB & previous conversations)
    5. Math calculation solver
    6. Free Internet AI (Pollinations Free AI - 100% free, 0 API keys)
    7. Google Gemini API (if key configured)
    8. Knowledge Base (Creator, Identity, Greetings, Group Links)
    9. Real-time Web Knowledge Search (for factual questions)
    10. Telegram Database Saved Word-Reply Fallback (if AI offline/rate-limited)
    11. Language-adaptive sweet girl conversation fallback
    """
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

    # Multi-turn Context Reset Check
    if user_id and re.search(r"\b(bhool jao|forget everything|reset chat|clear context)\b", cleaned):
        clear_user_context(user_id)
        if lang == "hindi":
            return "ठीक है जी! मैंने पुरानी सभी बातें भुला दीं! अब एक नई शुरुआत करते हैं! 🌸✨"
        elif lang == "english":
            return "Sure! I've cleared our previous chat history. Let's start fresh! 🌸✨"
        return "Theek hai ji! Maine purani sabhi baatein bhula di! Ab ek nayi shuruat karte hain! 🌸✨"

    # 1. Anti-abuse check
    if is_abusive(cleaned):
        return get_abuse_refusal()

    # 2. Check Q&A Memory Cache (Instant response from Telegram-synced database)
    cached_answer = await get_qa_answer(cleaned)
    if cached_answer:
        return _finalize(cached_answer)

    # 3. Math calculation
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

    # 4. Sentiment & Mood Detection (Sweet caring/comforting reactions)
    sad_match = re.search(r"\b(sad|udaas|mood\s+kharab|rona\s+aa\s+raha|dil\s+toot|breakup|akelapan|depressed|koi\s+nahi\s+hai)\b", cleaned)
    if sad_match:
        sad_replies = [
            f"Arey {user_name}, rona dhona band karo yaar! Strong bano thoda 💅",
            f"Dil toot gaya? Ice cream khao aur chill karo, life me aur bhi kaam hain 💁‍♀️✨",
            f"Itna senti kyu ho rahe ho? Jo gaya usko bhool jao, move on karo babu 😌💅",
        ]
        return _finalize(random.choice(sad_replies))

    happy_match = re.search(r"\b(pass\s+ho\s+gaya|party|khush\s+hoon|celebration|jeet\s+gaya|mazedar|good\s+news)\b", cleaned)
    if happy_match:
        happy_replies = [
            f"Yaaayyy! 🥳🎉 Bohot bohot badhai ho {user_name}! Main bohot khush hoon aapke liye! Party kab de rahe ho fir? Hehe! 💃✨",
            f"Waah waah! Kya baat hai {user_name}! Aise hi hamesha khush aur kamyab raho ji! Dher saara pyaar meri taraf se! 🌸💖",
        ]
        return _finalize(random.choice(happy_replies))

    # 5. Check core greetings / identity first for instant girl persona reply
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

    # 8. THIRD PRIORITY: Telegram Database Saved Word-Reply Fallback (Self-learned replies)
    try:
        from nexichat.database.chatbot import get_chat_reply
        learned = await get_chat_reply(cleaned)
        if learned and learned.get("content") and not is_abusive(learned.get("content")):
            return _finalize(learned.get("content"))
    except Exception:
        pass

    # 9. Language-adaptive fallback sweet girl conversation
    if lang == "hindi":
        fallback_res = random.choice(DEVNAGARI_FALLBACKS)
    elif lang == "english":
        fallback_res = random.choice(ENGLISH_FALLBACKS)
    else:
        fallback_res = random.choice(GIRL_FALLBACK_REPLIES)

    return _finalize(fallback_res)
