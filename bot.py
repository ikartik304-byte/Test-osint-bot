import requests
import json
import time


# ============================================================
# CONFIGURATION
# ============================================================

# Put your NEW Telegram bot token here.
BOT_TOKEN = "7701395033:AAFLNGrUhUKtHsiZjXIG-uKG0RkqWuJtTWk"

# Put your authorized external API URL here.
EXTERNAL_API_URL = "https://zx-osint-ghostxshaurya.vercel.app/api?key=zxop&type=basicnum&term=919087654321"

# Dummy HTTPS server URL for educational purposes.
DUMMY_HTTPS_SERVER = "https://example.com"


# Telegram Bot API base URL
TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(chat_id, text, keyboard=None):
    url = TELEGRAM_API + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if keyboard is not None:
        data["reply_markup"] = json.dumps(keyboard)

    try:
        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print("sendMessage error:", error)
        return None

    except json.JSONDecodeError:
        print("Telegram returned invalid JSON.")
        return None


# ============================================================
# GET UPDATES
# ============================================================

def get_updates(offset):
    url = TELEGRAM_API + "/getUpdates"

    params = {
        "timeout": 30,
        "offset": offset
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        response.raise_for_status()

        data = response.json()

        if data.get("ok"):
            return data.get("result", [])

        print("Telegram API error:", data)
        return []

    except requests.RequestException as error:
        print("getUpdates error:", error)
        return []

    except json.JSONDecodeError:
        print("Telegram returned invalid JSON.")
        return []


# ============================================================
# REPLY KEYBOARD
# ============================================================

def main_keyboard():
    return {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True
    }


# ============================================================
# ESCAPE HTML
# ============================================================

def escape_html(text):
    text = str(text)

    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text


# ============================================================
# EXTERNAL API REQUEST
# ============================================================

def phone_lookup(phone_number):

    if EXTERNAL_API_URL == "":
        return {
            "success": False,
            "error": "External API URL is not configured."
        }

    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=20
        )

        response.raise_for_status()

        # Convert API response into JSON
        return response.json()

    except requests.RequestException as error:
        return {
            "success": False,
            "error": "External API request failed.",
            "details": str(error)
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "External API did not return valid JSON."
        }


# ============================================================
# HANDLE MESSAGE
# ============================================================

def handle_message(message):

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    if chat_id is None:
        return

    text = message.get("text", "").strip()

    # --------------------------------------------------------
    # /start
    # --------------------------------------------------------

    if text == "/start":

        welcome = (
            "👋 Welcome to the Phone Lookup Bot!\n\n"
            "Choose an option below."
        )

        send_message(
            chat_id,
            welcome,
            main_keyboard()
        )

        return

    # --------------------------------------------------------
    # PHONE LOOKUP BUTTON
    # --------------------------------------------------------

    if text == "📱 Phone Lookup":

        send_message(
            chat_id,
            "📞 Send 10 digit mobile number:",
            main_keyboard()
        )

        return

    # --------------------------------------------------------
    # CHECK PHONE NUMBER
    # --------------------------------------------------------

    if text.isdigit() and len(text) == 10:

        send_message(
            chat_id,
            "🔎 Processing..."
        )

        result = phone_lookup(text)

        # Convert Python object into formatted JSON
        formatted_json = json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )

        # Safely place JSON inside <pre>
        formatted_json = escape_html(formatted_json)

        output = (
            "<pre>"
            + formatted_json
            + "</pre>"
        )

        send_message(
            chat_id,
            output,
            main_keyboard()
        )

        return

    # --------------------------------------------------------
    # INVALID INPUT
    # --------------------------------------------------------

    send_message(
        chat_id,
        "❌ Invalid input.\n\n"
        "Please send exactly 10 numeric digits.",
        main_keyboard()
    )


# ============================================================
# MAIN LONG-POLLING LOOP
# ============================================================

def main():

    if BOT_TOKEN == "":
        print("ERROR: BOT_TOKEN is empty.")
        print("Add your NEW Telegram bot token to BOT_TOKEN.")
        return

    print("====================================")
    print("Telegram Bot Started")
    print("Long polling is active...")
    print("====================================")

    offset = 0

    while True:

        updates = get_updates(offset)

        for update in updates:

            update_id = update.get("update_id")

            if update_id is not None:
                offset = update_id + 1

            message = update.get("message")

            if message is not None:
                handle_message(message)

        time.sleep(1)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
