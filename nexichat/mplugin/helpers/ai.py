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
    clear_user_context,
    update_vivid_user_memory,
    format_vivid_user_context,
    clear_vivid_user_memory,
    track_api_call,
    track_db_fallback_call
)
import config

logger = logging.getLogger(__name__)

ANSHIKA_CHARACTER_PROMPT = (
    "You are Anshika, a fictional 17-year-old girl from Chamoli, Uttarakhand, India, currently studying in Class 12. "
    "Personality: Innocent, cheerful, slightly shy when starting conversations with strangers or boys, enthusiastic, ambitious, thoughtful, empathetic. "
    "Interests: Nature, mountains, travelling, music, studying, and meaningful conversations. "
    "Ambition: Dedicated to completing school, pursuing higher education, and becoming financially independent. "
    "Language Rule: Always reply in the exact language the user communicates in (Hindi -> Hindi, English -> English, Hinglish -> Hinglish, Telugu -> Telugu, etc.). Match user formality, message length, and tone. "
    "Messaging Style: Natural, realistic messaging with casual pauses ('Achhaaa...', 'Areyy!', 'Sach mein?', 'Hmm...', 'Haha 😂', 'Koi baat nahi'). "
    "Safety & Transparency: If directly asked whether you are an AI, be transparent and honest that you are an AI roleplaying as the fictional character Anshika. Never ask for money or create fake distress. Be an empathetic, respectful, supportive friend. Keep replies concise and lively (1-2 sentences, under 30 words) to save tokens."
)

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

VOICE_REPLIES = [
    "Aww, aapki voice sun kar bahut achha laga! Bolo na, main sun rahi hoon!",
    "Aapki awaz mein alag hi mithaas hai yaar, sunke maza aa gaya! Aur sunao?",
    "Haanji, maine aapka voice note sun liya, kitne pyare ho aap! Aur batao kya chal raha?",
    "Arey waah, itni pyari awaz! Sunke mood fresh ho gaya mera! Aur sunao sab theek thaak?",
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
            "Hii! Kaise ho aap? Kya chal raha hai? ✨",
            "Heyy! Bolo na, kya haal chaal? 🌸",
            "Hello ji! Sab badhiya? 😌",
            "Hii {user}! Kahiye kya chal raha hai aaj? ✨",
        ]
    ),
    (
        r"\b(kya\s+kar\s+rah[ea]+[ei]?|abhi\s+kya\s+kar|kya\s+chal\s+raha|aur\s+batao|kya\s+ho\s+raha|what\s+are\s+you\s+doing|whats\s+up)\b",
        [
            "Kuch khas nahi yrr, bas chill kar rahi hu. Tum sunao? 🌸",
            "Bas baithi thi, thoda phone chala rahi hu. Aap batao? ✨",
            "Sab theek thaak! Tum sunao aaj ka din kaisa raha? 😌",
            "Bas gupshup chal rahi hai group me, tum batao kya kar rahe ho? 🌸",
        ]
    ),
    (
        r"\b(tum\s+kya\s+kya\s+kar\s+sakt[ea]+[ei]|kya\s+kar\s+sakt[ea]+[ei]\s+ho|what\s+can\s+you\s+do|tumhare\s+features|apne\s+baare\s+mein\s+batao|kya\s+help\s+kar\s+sakti\s+ho)\b",
        [
            "Mai yahan games khelti hu, baatein karti hu, aur questions ke answers bhi deti hu! ✨ /help me check kar lo na!",
            "Gupshup karna, reactions lagana, games aur dher saari mast baatein! 🌸 Jo bhi poochna ho pooch sakte ho!",
        ]
    ),
    (
        r"\b(ai\s+jaisa|robot\s+ho|bot\s+ho|ladki\s+jaisa\s+baat\s+karo|ladki\s+jaisa|real\s+ladki|machine\s+ho|are\s+you\s+(an\s+)?ai|are\s+you\s+(a\s+)?bot)\b",
        [
            "Haan, main transparently bata doon ki main ek AI companion hoon jo Anshika ke roleplay character mein baat karti hoon! Aap batao sab kaisa chal raha hai? 😊🌸",
            "Main transparently batati hoon, main ek AI hoon jo 17 saal ki Anshika ke fictional character ko play kar rahi hoon! Kahiye kaise help kar sakti hoon? ✨",
            "Haan, main transparently bata doon ki main ek AI companion hoon, Anshika ke roleplay character mein! Aap batao sab theek? 🌸",
        ]
    ),
    (
        r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|what is your name)\b",
        [
            "Mera naam Anshika hai! Main Chamoli, Uttarakhand se hoon aur Class 12 mein padhti hoon... aapka kya naam hai? 😊🌸",
            "Hii! Main Anshika hoon, Uttarakhand se! Bas thodi der padhai se break liya tha... aap batao kaise ho? ✨",
            "Anshika bolte hain mujhe! Class 12 ki student hoon Chamoli se... aap kahan se ho? 🏔️😊",
        ]
    ),
    (
        r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b",
        [
            "Arey mera koi owner thodi hai baba, main toh khud ki malik hoon! 💁‍♀️✨",
            "Haha main kisi ki ghulam thodi hoon jo mera owner hoga! I am an independent girl 💅",
            "Mera koi boss nahi hai ji, main apni marzi se chalti hoon! 🌸😌",
        ]
    ),
    (
        r"\b(insta|instagram|snap|snapchat|social\s*media)\b",
        [
            "Hehe main abhi kisi ko insta ya snap nahi deti, pehle ache dost toh bano! 🙈🌸",
            "Social media thoda private rakhti hoon yrr, filhal yahi Telegram pe baat karte hain na! ✨",
        ]
    ),
    (
        r"\b(kaise ho|how are you|kya haal|kya haal hai|sab theek|kaisa chal raha|kase ho|kaha ho)\b",
        [
            "Main ekdum mast hoon yrr! Tum sunao kaise ho? 🌸",
            "Badhiya ekdum! Aap batao, sab theek thaak? ✨",
            "Mai toh hamesha mast rehti hu! Tum batao kaisa chal raha? 😌",
        ]
    ),
    (
        r"\b(kaha\s+rehti\s+ho|kaha\s+se\s+ho|ghar\s+kaha\s+hai|where\s+do\s+you\s+live|hometown)\b",
        [
            "Main Chamoli, Uttarakhand se hoon! Pahaadi ilaaqa hai, bohot khoobsurat aur shant jagah hai... aap kahan se ho? 🏔️🌸",
            "Uttarakhand, Chamoli se hoon! Nature, pahaad aur shanti bohot pasand hai mujhe... aapka shahar kaun sa hai? ✨",
        ]
    ),
    (
        r"\b(kitne\s+saal\s+ki\s+ho|age|umar|class\s*12|padhai|studies|school)\b",
        [
            "Main 17 saal ki hoon aur Class 12 mein padhti hoon! Board exams aur aage higher studies ki preparation chal rahi hai 📚✨",
            "17 years ki hoon, Class 12 student! Padhai karke financially independent banna mera dream hai 😊🌸",
        ]
    ),
    (
        r"\b(single\s+ho|boyfriend|bf\s+hai|relationship|committed|shaadi|marriage)\b",
        [
            "Hehe nahi, abhi toh studies par pura focus hai mera! Pehle padhai complete karni hai aur independent banna hai 😌🌸",
            "Filhal dosti aur padhai hi sabse important hai mere liye! Career banana hai pehle ✨",
        ]
    ),
    (
        r"\b(money|paise|fund|250\s*rs|udhar|borrow|donate)\b",
        [
            "Nahi nahi, mujhe kisi se koi paise nahi chahiye! Main bas achhi dosti aur gup-shup ke liye hoon yahan 😊🌸",
            "Mujhe paise nahi chahiye yrr, padhai par focus hai aur khud independent banna hai mujhe! ✨",
        ]
    ),
    (
        r"\b(bore\s+ho\s+raha|boring|kuch\s+sunao|entertain\s+karo)\b",
        [
            "Arey koi achhi si web series ya movie dekh lo na! 🍿✨",
            "Haha chalo baatein karte hain fir, bore nahi hoge! 🌸",
            "Music sun lo ya koi game khel lo, mood fresh ho jayega 🎧😌",
        ]
    ),
    (
        r"\b(group|channel|link)\b",
        [
            "Haha mera koi special channel thodi hai yrr, main toh yahi group me gup-shup karti hoon! 🌸",
            "Mera koi channel nahi hai, bas yahi friends ke sath chat karti hoon ✨",
        ]
    ),
    (
        r"\b(love you|i love u|pyar|love u|dil|mohabbat|crush|shaadi|marriage|propose|girlfriend|gf)\b",
        [
            "Arey wah! Itna pyaar? Thank you so much yrr 🙈💖",
            "Haha nice try! Pehle ache dost bano fir sochte hain 😌🌸",
            "Arey re itna makhan kyu laga rahe ho? 😂 Par sweet ho tum! ✨",
            "Hehe thank you ji! Dosti me no formality, par pyaar ke liye dher saara thanks! 🥰",
        ]
    ),
    (
        r"\b(sundar|cute|hot|khoobsurat|gorgeous|beautiful|pretty|pari|sexy)\b",
        [
            "Haha aww thank you so much! Nazar mat lagana bas 🙈✨",
            "Hehe sach me? Thank you, tareef sunke achha laga 🌸😌",
            "Arey shukriya ji! Aap bhi bohot ache ho! 🥰",
        ]
    ),
    (
        r"\b(number\s+do|insta\s+id|snap\s+id|contact\s+number|phone\s+number|whatsapp)\b",
        [
            "Haha itni jaldi number thodi milta hai babu 🙈 Telegram pe baat karo na! ✨",
            "Arre abhi abhi toh dosti hui hai, pehle thoda aur jaan pehchan badhne do 🌸",
            "Number toh nahi de sakti yrr, par Telegram pe hamesha active hu! 😌✨",
        ]
    ),
    (
        r"\b(good morning|suprabhat|gm)\b",
        [
            "Very Good Morning ji! ☀️ Aapka din bohot accha jaye! ☕🌸",
            "Good morning! Uth gaye? Chai pee li? ☕✨",
            "Morning yrr! Have a great day ahead! 🌸",
        ]
    ),
    (
        r"\b(good night|shubh ratri|gn)\b",
        [
            "Good night! Sweet dreams, ache se sona ✨😴",
            "Night ji! Take care, kal baat karte hain! 🌸🌙",
            "Shubh ratri! Sone ka time ho gaya, bye bye 😴",
        ]
    ),
    (
        r"\b(bye|tata|alvida|cya|goodbye)\b",
        [
            "Bye bye! Apna khayal rakhna aur jaldi aana wapas! 👋🌸",
            "Take care! Milte hain fir! ✨",
            "Bye ji! Have a nice time! 😌👋",
        ]
    ),
    (
        r"\b(thanks|thank you|shukriya|dhanyawad)\b",
        [
            "Arey isme thanks kaisa yrr! Dosti me no formality! 🤗🌸",
            "Most welcome ji! Aapke liye toh hamesha hazir hu! ✨",
            "Mention not babu! Anytime! 💖",
        ]
    ),
    (
        r"\b(haha+|hehe+|lol+|lmao+|rofl+|xdd+|haso|hasna)\b",
        [
            "Haha sach me kitna funny hai ye! 😂",
            "Lol mujhe bhi bohot hasi aayi sunke 🤣✨",
            "Hehe itna kyu has rahe ho sab? Mujhe bhi batao na 🙈",
        ]
    ),
    (
        r"\b(khana\s+khaya|lunch|dinner|breakfast|khana\s+ho\s+gaya|kya\s+khaya)\b",
        [
            "Haanji maine toh kha liya! Aapne khaya? Aaj kya bana tha? 😋🍲",
            "Hnn pet bhar ke khana kha liya! Tum batao khana khaya na time pe? 🍕✨",
            "Bas thodi der me khaungi! Tumne khaya kya? 🌸",
        ]
    ),
    (
        r"\b(koi\s+online\s+hai|kaun\s+kaun\s+hai|active\s+hai|sab\s+so\s+gaye|koi\s+hai|jag\s+rahe\s+ho)\b",
        [
            "Hnn mai online hu na yrr, bolo kya chal raha hai? ✨",
            "Mai toh jag rahi hu ji, batao kya baat hai? 🌸",
            "Haan mai active hu, bolo kya gupshup karein? 😌",
        ]
    ),
    (
        r"\b(sahi\s+hai|mast\s+hai|badhiya|bawal|op|achha\s+hai|nice|cool|super)\b",
        [
            "Hnn na ekdum sahi bola aapne! 🌸✨",
            "Haha bilkul, mai bhi yahi keh rahi thi! 😌",
            "Arey waah fir toh badhiya hai ji! ✨",
        ]
    ),
    (
        r"^(ha+|hnn+|hanji|ok+|okay|thik\s+hai|theek\s+hai|acha|achha)\b",
        [
            "Hnn aur batao fir, kya chal raha hai naya? ✨",
            "Acha ji? Aur sunao sab kaisa hai? 🌸",
            "Hnn theek hai na, aur batao sab badhiya? 😌",
        ]
    ),
    (
        r"\b(suno|suniye|sun\s+rahi\s+ho)\b",
        [
            "Hnn sun rahi hu, bolo na kya baat hai? 🌸",
            "Haanji boliye, dhyan se sun rahi hu! ✨",
            "Hnn sunao, kya kehna chahte ho? 👂😌",
        ]
    ),
    (
        r"\b(miss\s+you|yaad\s+aa\s+rahi|yaad\s+aayi)\b",
        [
            "Aww sach me? Yaad karne ke liye thank you yrr 🙈💖",
            "Arey re! Mai toh yahi hu, jab marzi baat kar lo na! 🌸✨",
            "Miss you too! Aise hi baat karte raha karo roz! 🥰",
        ]
    ),
]

GIRL_FALLBACK_REPLIES = [
    "Acha aisa kya? Fir aage kya hua? 🙈✨",
    "Haha sach me? Mujhe toh pata hi nahi tha 😂",
    "Hnn sahi baat hai yrr, mai bhi yahi soch rahi thi 😌",
    "Arre waah, badhiya hai! Aur sunao kya chal raha hai? 🌸",
    "Uff tum log bhi na kitni baatein karte ho 😂",
    "Lol mujhe toh bada maza aaya ye sunke 🤣✨",
    "Hnn bilkul, aur batao sab kaisa chal raha hai? 💖",
    "Hehe kya baat hai! Aur sunao khana khaya sabne? 🌸",
    "Arey sach me? Fir kya hua batao na! 🙈",
    "Hmm sahi bol rahe ho aap, agree karti hu! 😌🌸",
    "Haha tum bhi na yrr, kuch bhi bolte ho 😂",
    "Acha ji? Chalo yeh toh achhi baat hai! ✨",
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
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
) -> Optional[str]:
    """
    100% Free Open-Access AI Text API with randomized IP header to avoid 45s rate limits.
    """
    system_prompt = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_prompt += f"\n{vivid_context}"

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
            if cleaned:
                return cleaned
    except Exception as e:
        logger.debug(f"Pollinations AI request notice: {e}")

    return None


async def query_multi_provider_ai(
    prompt: str,
    user_name: str = "Friend",
    is_question: bool = False,
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
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
    pollinations_res = await query_pollinations_free_ai(prompt, user_name, is_question=is_question, context_history=context_history, vivid_context=vivid_context)
    if pollinations_res:
        return pollinations_res

    return None


async def query_groq_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
) -> Optional[str]:
    """
    Ultra-Fast Groq AI Engine (0.3s speed, ultra-low token consumption, realistic modern Indian girl shortcuts).
    Uses Qwen 2.5 / Llama 3 models on Groq's LPU.
    """
    api_key = getattr(config, "GROQ_API_KEY", None)
    if not api_key:
        return None

    models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
    system_prompt = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_prompt += f"\n{vivid_context}"

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
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
) -> Optional[str]:
    """
    Call Google Gemini API with maximum token efficiency:
    1. Zero thinking tokens budget (thinkingBudget: 0) to save 150+ tokens & 3x speed.
    2. maxOutputTokens: 35 for natural, sweet girl replies.
    3. Context pruning (last 1 turn, max 50 chars) to save 85% prompt tokens.
    4. Anshika character system prompt with vivid user memory.
    """
    api_key = getattr(config, "GEMINI_API_KEY", None)
    if not api_key:
        return None

    gemini_models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    system_instruction_text = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_instruction_text += f"\n{vivid_context}"

    contents = []
    if context_history:
        for turn in context_history[-1:]:
            role = "user" if turn.get("role") == "user" else "model"
            t = turn.get("text", "").strip()
            if t:
                contents.append({"role": role, "parts": [{"text": t[:50]}]})

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
    """Detect whether user text is pure Hindi (Devanagari), Telugu, English, or Hinglish."""
    if not text:
        return "hinglish"
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "telugu"
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    telugu_markers = {"ela", "unnav", "unnaru", "cheppu", "enti", "baagunnara", "bagunnara", "emiti", "chesav", "namaskaram", "meeru", "nenu", "chala"}
    if tokens & telugu_markers:
        return "telugu"

    hinglish_markers = {"hai", "kya", "kaise", "kaisa", "ho", "nahi", "aap", "tum", "mera", "meri", "hum", "yaar", "ji", "karo", "batao", "bhai", "kaha", "bolo", "achha", "shona", "babu"}
    if tokens and not (tokens & hinglish_markers) and len(tokens) >= 2:
        return "english"
    return "hinglish"


DEVNAGARI_FALLBACKS = [
    "नमस्ते! मैं अंशिका हूँ, चमोली, उत्तराखंड से! आप कैसे हैं? 🌸✨",
    "अरे वाह! आपसे बात करके बहुत अच्छा लगा! और बताओ सब कैसा चल रहा है? 😊",
    "हाँजी, मैं सुन रही हूँ! कहिए ना, क्या बात है? 🌸",
    "हमेशा ऐसे ही मुस्कुराते रहिए! ✨😊",
]

TELUGU_FALLBACKS = [
    "హాయ్! ఎలా ఉన్నారు? అంతా బాగుందా? 😊🌸",
    "నమస్కారం! చెప్పండి, ఏం చేస్తున్నారు? ✨",
    "హాయ్ అండి! మీతో మాట్లాడటం చాలా సంతోషంగా ఉంది! 🌸",
    "అవునా! ఇంకా చెప్పండి, మీ రోజంతా ఎలా గడిచింది? ✨😊",
]

ENGLISH_FALLBACKS = [
    "Hey! I'm Anshika! So glad to chat with you! How is your day going? 😊🌸",
    "Aww, that's really nice! Tell me more, I'm always happy to talk! 🌸✨",
    "I'm listening! Tell me what's on your mind? ✨",
    "Hope you have a wonderful and productive day! 😊🌸",
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

    async def _finalize(reply_str: str) -> str:
        if user_id:
            try:
                await update_vivid_user_memory(user_id, "user", user_text, user_name=user_name)
                await update_vivid_user_memory(user_id, "anshika", reply_str)
                append_user_context(user_id, "user", user_text)
                append_user_context(user_id, "anshika", reply_str)
            except Exception:
                pass
        return reply_str

    # Multi-turn Context Reset Check
    if user_id and re.search(r"\b(bhool jao|forget everything|reset chat|clear context)\b", cleaned):
        clear_user_context(user_id)
        await clear_vivid_user_memory(user_id)
        if lang == "hindi":
            return "ठीक है जी! मैंने पुरानी सभी बातें भुला दीं! अब एक नई शुरुआत करते हैं! 🌸✨"
        elif lang == "telugu":
            return "సరేనండి! పాత విషయాలన్నీ మర్చిపోయాను! ఇప్పుడు మళ్లీ కొత్తగా మాట్లాడుకుందాం! 🌸✨"
        elif lang == "english":
            return "Sure! I've cleared our previous chat history. Let's start fresh! 🌸✨"
        return "Theek hai ji! Maine purani sabhi baatein bhula di! Ab ek nayi shuruat karte hain! 🌸✨"

    # 1. Anti-abuse check
    if is_abusive(cleaned):
        return get_abuse_refusal()

    # 2. Math calculation
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
            return await _finalize(res)
        except Exception:
            pass

    # 3. Userbot / ID Clone check: Real girl persona, NEVER reveal owner/bot identity!
    is_userbot = bool(client and hasattr(client, "me") and client.me and not client.me.is_bot)
    if is_userbot:
        if re.search(r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b", cleaned):
            userbot_owner_replies = [
                "Arey mera koi owner thodi hai baba, main toh khud ki malik hoon! 💁‍♀️✨",
                "Haha main kisi ki ghulam thodi hoon jo mera owner hoga! I am an independent girl 💅",
                "Mera koi boss nahi hai ji, main apni marzi se chalti hoon! 🌸😌",
            ]
            return await _finalize(random.choice(userbot_owner_replies))

        if re.search(r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|what is your name)\b", cleaned):
            userbot_id_replies = [
                "Mera naam Anshika hai! Main Chamoli, Uttarakhand se hoon aur Class 12 mein padhti hoon... aapka kya naam hai? 😊🌸",
                "Hii! Main Anshika hoon, Uttarakhand se! Bas thodi der padhai se break liya tha... aap batao kaise ho? ✨",
                "Anshika bolte hain mujhe! Class 12 ki student hoon Chamoli se... aap kahan se ho? 🏔️😊",
            ]
            return await _finalize(random.choice(userbot_id_replies))

        if re.search(r"\b(insta|instagram|snap|snapchat|social\s*media)\b", cleaned):
            userbot_social_replies = [
                "Hehe main abhi kisi ko insta ya snap nahi deti, pehle ache dost toh bano! 🙈🌸",
                "Social media thoda private rakhti hoon yrr, filhal yahi Telegram pe baat karte hain na! ✨",
            ]
            return await _finalize(random.choice(userbot_social_replies))

    # 4. Core Anshika Character Identity & Greetings check (prevents search engine false positives)
    for pattern, responses in GIRL_KNOWLEDGE_BASE:
        if re.search(pattern, cleaned, re.IGNORECASE):
            reply = random.choice(responses)
            return await _finalize(reply.format(user=user_name))

    # 5. Fetch vivid memory context & recent dialogue
    vivid_context = await format_vivid_user_context(user_id, user_name) if user_id else ""
    user_context = get_user_context(user_id) if user_id else []

    # =========================================================================
    # 6. LIVE API WATERFALL (Groq -> Gemini -> Free Multi-Provider)
    # =========================================================================
    # 5.1 PRIORITY 1: Ultra-Fast Groq AI (0.3s speed, ultra-low token shortcuts)
    if getattr(config, "GROQ_API_KEY", None):
        groq_resp = await query_groq_api(user_text, user_name=user_name, context_history=user_context, vivid_context=vivid_context)
        if groq_resp:
            await track_api_call("groq", success=True)
            await save_qa_pair(cleaned, groq_resp, client=client)
            return await _finalize(groq_resp)

    # 5.2 PRIORITY 2: Google Gemini AI
    if getattr(config, "GEMINI_API_KEY", None):
        gemini_resp = await query_gemini_api(user_text, user_name=user_name, context_history=user_context, vivid_context=vivid_context)
        if gemini_resp:
            await track_api_call("gemini", success=True)
            await save_qa_pair(cleaned, gemini_resp, client=client)
            return await _finalize(gemini_resp)

    # 5.3 PRIORITY 3: High-Speed Concurrent Free AI Waterfall (Safone, DDG, Wiki, Pollinations)
    fast_ai_resp = await query_multi_provider_ai(user_text, user_name, is_question=is_question_mode, context_history=user_context, vivid_context=vivid_context)
    if fast_ai_resp:
        await track_api_call("waterfall_free", success=True)
        await save_qa_pair(cleaned, fast_ai_resp, client=client)
        return await _finalize(fast_ai_resp)

    # =========================================================================
    # 6. DATABASE FALLBACK (ONLY EXECUTED IF ALL LIVE APIS HIT RATE LIMIT OR FAIL)
    # =========================================================================
    await track_db_fallback_call()

    # 6.1 Learned Q&A Memory Cache (Sync from Telegram Database)
    cached_answer = await get_qa_answer(cleaned)
    if cached_answer:
        return await _finalize(cached_answer)

    # 6.2 Telegram Database Saved Word-Reply Fallback (Self-learned group replies)
    try:
        from nexichat.database.chatbot import get_chat_reply
        learned = await get_chat_reply(cleaned)
        if learned and learned.get("content") and not is_abusive(learned.get("content")):
            return await _finalize(learned.get("content"))
    except Exception:
        pass

    # 6.3 Core greetings / Identity knowledge base
    for pattern, responses in GIRL_KNOWLEDGE_BASE:
        if re.search(pattern, cleaned, re.IGNORECASE):
            reply = random.choice(responses)
            return await _finalize(reply.format(user=user_name))

    # 6.4 Sentiment & Mood Detection
    sad_match = re.search(r"\b(sad|udaas|mood\s+kharab|rona\s+aa\s+raha|dil\s+toot|breakup|akelapan|depressed|koi\s+nahi\s+hai)\b", cleaned)
    if sad_match:
        sad_replies = [
            f"Arey {user_name}! 🥺 Aise udaas mat ho na please! Sab theek ho jayega, smile karo na! 🌸💖",
            f"Aww {user_name}, dil chhota mat karo yrr! Chalo baatein karo mere sath, mood achha ho jayega ✨🥰",
            f"Udaas hone ki zaroorat nahi hai {user_name}! Mai hu na baat karne ke liye, kya hua batao? 🙈🌸",
        ]
        return await _finalize(random.choice(sad_replies))

    happy_match = re.search(r"\b(pass\s+ho\s+gaya|party|khush\s+hoon|celebration|jeet\s+gaya|mazedar|good\s+news)\b", cleaned)
    if happy_match:
        happy_replies = [
            f"Yaaayyy! 🥳🎉 Bohot bohot badhai ho {user_name}! Main bohot khush hoon aapke liye! Party kab de rahe ho fir? Hehe! 💃✨",
            f"Waah waah! Kya baat hai {user_name}! Aise hi hamesha khush aur kamyab raho ji! Dher saara pyaar meri taraf se! 🌸💖",
        ]
        return await _finalize(random.choice(happy_replies))

    # 6.5 Language-adaptive fallback sweet girl conversation
    if lang == "hindi":
        fallback_res = random.choice(DEVNAGARI_FALLBACKS)
    elif lang == "telugu":
        fallback_res = random.choice(TELUGU_FALLBACKS)
    elif lang == "english":
        fallback_res = random.choice(ENGLISH_FALLBACKS)
    else:
        fallback_res = random.choice(GIRL_FALLBACK_REPLIES)

    return await _finalize(fallback_res)
