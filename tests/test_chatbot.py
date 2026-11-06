import os
import unittest
from nexichat.database.chatbot import (
    is_chatbot_enabled,
    set_chatbot_enabled,
    save_chat_reply,
    get_chat_reply,
    save_qa_pair,
    get_qa_answer,
    save_sticker,
    get_random_sticker
)
from nexichat.modules.helpers.ai import (
    calculate_love,
    get_random_shayari,
    get_random_joke,
    generate_conversational_response,
    is_abusive,
    get_abuse_refusal,
    get_voice_reply,
    get_photo_reply,
    get_video_reply,
    get_animation_reply
)

class TestChatbotFeatures(unittest.IsolatedAsyncioTestCase):

    async def test_chatbot_database_toggle(self):
        chat_id = -10099887766
        # Default should be enabled (True)
        enabled_default = await is_chatbot_enabled(chat_id)
        self.assertTrue(enabled_default)

        # Disable chatbot
        await set_chatbot_enabled(chat_id, False)
        enabled_after_off = await is_chatbot_enabled(chat_id)
        self.assertFalse(enabled_after_off)

        # Re-enable chatbot
        await set_chatbot_enabled(chat_id, True)
        enabled_after_on = await is_chatbot_enabled(chat_id)
        self.assertTrue(enabled_after_on)

    async def test_learned_replies(self):
        await save_chat_reply("koyeb deployment", "text", "Koyeb deployment is ready and working!")
        reply = await get_chat_reply("koyeb deployment")
        self.assertIsNotNone(reply)
        self.assertEqual(reply["content"], "Koyeb deployment is ready and working!")

    async def test_qa_memory_learning(self):
        # AI learns a Q&A pair so it never forgets
        await save_qa_pair("capital of france", "Paris is the capital of France ji! 🌸")
        ans = await get_qa_answer("capital of france")
        self.assertIsNotNone(ans)
        self.assertIn("Paris", ans)

    async def test_sticker_learning(self):
        stk_id = "CAACAgIAAxkBAAEK7nxlffK7g4Z243_TEST_ID"
        await save_sticker(stk_id)
        stk = get_random_sticker()
        self.assertIsNotNone(stk)

    async def test_anti_abuse_filter(self):
        self.assertTrue(is_abusive("bsdk"))
        self.assertTrue(is_abusive("tum chutiya ho"))
        self.assertFalse(is_abusive("hello pyari bot"))
        
        # Test refusal message
        refusal = get_abuse_refusal()
        self.assertTrue(any(k in refusal.lower() for k in ["gand", "bad words", "gaali", "naraz", "respect"]))

    async def test_media_replies(self):
        v = get_voice_reply()
        p = get_photo_reply()
        vid = get_video_reply()
        anim = get_animation_reply()
        self.assertTrue(len(v) > 5)
        self.assertTrue(len(p) > 5)
        self.assertTrue(len(vid) > 5)
        self.assertTrue(len(anim) > 5)

    async def test_love_calculator(self):
        res = calculate_love("Amrit", "Chatbot")
        self.assertIn("Love Compatibility Test", res)
        self.assertIn("Amrit", res)
        self.assertIn("%", res)

    async def test_shayari(self):
        sh = get_random_shayari()
        self.assertIsInstance(sh, str)
        self.assertTrue(len(sh) > 10)

    async def test_joke(self):
        jk = get_random_joke()
        self.assertIsInstance(jk, str)
        self.assertTrue(len(jk) > 10)

    async def test_conversational_ai_math(self):
        resp = await generate_conversational_response("5 * 8")
        self.assertIn("40", resp)

    async def test_conversational_ai_creator(self):
        resp = await generate_conversational_response("who is your creator")
        # Anshika character maintains independence without mentioning owner
        self.assertTrue(any(word in resp.lower() for word in ["owner", "malik", "independent", "marzi"]))

    async def test_conversational_ai_identity(self):
        resp = await generate_conversational_response("who are you")
        self.assertIn("Anshika", resp)
        self.assertTrue("Chamoli" in resp or "Uttarakhand" in resp)

    async def test_conversational_ai_telugu(self):
        from nexichat.modules.helpers.ai import detect_language
        lang1 = detect_language("బాగున్నారా?")
        self.assertEqual(lang1, "telugu")
        lang2 = detect_language("ela unnav?")
        self.assertEqual(lang2, "telugu")

    async def test_conversational_ai_group_links(self):
        resp = await generate_conversational_response("group link")
        # Anshika talks naturally as a friend without unsolicited link spam
        self.assertTrue("group" in resp.lower() or "channel" in resp.lower() or "chat" in resp.lower())

    async def test_telegram_db_functions(self):
        from nexichat.database.telegram_db import get_db_chats, log_qa_to_telegram, log_reply_to_telegram
        chats = get_db_chats()
        self.assertTrue(len(chats) >= 1)
        self.assertNotIn("privatethink", chats)
        self.assertNotIn("amrit_feel", chats)
        self.assertIn("Yaarwinprofits", chats)
        # Should execute safely even without client connection
        await log_qa_to_telegram(None, "sample q", "sample a")
        await log_reply_to_telegram(None, "sample word", "text", "sample reply")

    async def test_sticker_fallback_guarantee(self):
        # Fallback should be returned if no sticker learned yet
        fb = "TEST_FALLBACK_FILE_ID"
        res = get_random_sticker(fallback=fb)
        self.assertIsNotNone(res)

    async def test_voicemode_database_toggle(self):
        from nexichat.database.chatbot import is_voicemode_enabled, set_voicemode_enabled
        chat_id = -10099112233
        # Default should be False (text mode)
        self.assertFalse(await is_voicemode_enabled(chat_id))
        # Turn ON
        await set_voicemode_enabled(chat_id, True)
        self.assertTrue(await is_voicemode_enabled(chat_id))
        # Turn OFF
        await set_voicemode_enabled(chat_id, False)
        self.assertFalse(await is_voicemode_enabled(chat_id))

    def test_hinglish_to_hindi_transliteration(self):
        from nexichat.modules.helpers.media_gen import hinglish_to_hindi
        # Already Hindi
        self.assertEqual(hinglish_to_hindi("नमस्ते"), "नमस्ते")
        # Hinglish converts to Hindi
        res = hinglish_to_hindi("Hii kaise ho")
        self.assertTrue(len(res) > 0)
        # Should contain Devanagari characters
        has_devanagari = any("\u0900" <= c <= "\u097F" for c in res)
        self.assertTrue(has_devanagari)

    async def test_userbot_never_reveals_owner(self):
        class MockUser:
            is_bot = False
            first_name = "Lav"
        class MockClient:
            me = MockUser()

        mock_client = MockClient()
        resp_owner = await generate_conversational_response("owner kaun hai", client=mock_client)
        # Userbot must NOT reveal Amrit Raj or Villanns as owner
        self.assertNotIn("Amrit Raj", resp_owner)
        self.assertNotIn("@Villanns", resp_owner)
        # Should talk like an independent real girl
        self.assertTrue(any(k in resp_owner.lower() for k in ["owner", "malik", "ghulam", "boss", "real ladki"]))

    def test_polly_aditi_voice_generation(self):
        from nexichat.modules.helpers.media_gen import generate_voice_file
        path = generate_voice_file("Hii kaise ho!", voice="Aditi")
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 500)
        try:
            os.remove(path)
        except Exception:
            pass

if __name__ == "__main__":
    unittest.main()

