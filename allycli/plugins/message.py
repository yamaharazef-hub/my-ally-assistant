from plugin import plugin
import smtplib
import requests
import os

# --- Telegram Plugin ---
@plugin("send telegram")
def send_telegram(ally, s):
    """
    Send a message through Telegram.
    Usage: send telegram <message>
    """
    # Get credentials from environment variables
    TELEGRAM_BOT_TOKEN = os.environ.get("ALLY_TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.environ.get("ALLY_TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        ally.say("Telegram credentials are missing! Please set ALLY_TELEGRAM_BOT_TOKEN and ALLY_TELEGRAM_CHAT_ID.")
        return

    if not s:
        ally.say("What message should I send?")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": s}

    try:
        response = requests.post(url, data=data)
        if response.ok:
            ally.say("Message sent via Telegram!")
        else:
            ally.say(f"Failed to send Telegram message. Status: {response.status_code}")
    except Exception as e:
        ally.say(f"Error sending Telegram message: {e}")


# --- Gmail Plugin ---
@plugin("send gmail")
def send_gmail(ally, s):
    """
    Send a message through Gmail.
    Usage: send gmail <message>
    """
    EMAIL = os.environ.get("ALLY_GMAIL_ADDRESS")
    PASSWORD = os.environ.get("ALLY_GMAIL_APP_PASSWORD")

    if not EMAIL or not PASSWORD:
        ally.say("Gmail credentials are missing! Please set ALLY_GMAIL_ADDRESS and ALLY_GMAIL_APP_PASSWORD.")
        return

    if not s:
        ally.say("What message should I send?")
        return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, EMAIL, s)
        ally.say("Email sent successfully!")
    except Exception as e:
        ally.say(f"Error sending email: {e}")


def send_join_message():
    """Send a startup message via Telegram."""
    TELEGRAM_BOT_TOKEN = os.environ.get("ALLY_TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.environ.get("ALLY_TELEGRAM_CHAT_ID")

    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        # Silently fail if credentials are not set
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "Ally is up and running!"}

    try:
        requests.post(url, data=data)
    except Exception:
        # Silently fail on error
        pass
