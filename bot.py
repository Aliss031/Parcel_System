from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
import openai
import random
from datetime import datetime, timedelta

# === Flask App ===
app = Flask(__name__)

# === Firebase Setup ===
cred = credentials.Certificate(r"C:\Users\soray\Downloads\parcel-pin-system-firebase-adminsdk-fbsvc-d3a1cd4a87.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# === Twilio Setup ===
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# === OpenAI Setup ===
openai.api_key = "YOUR_OPENAI_API_KEY"

# === OTP Generator ===
def generate_otp():
    return str(random.randint(100000, 999999))

# === AI Chat Function ===
def ask_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4 if available
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"⚠️ AI Error: {e}"

# === Webhook for Incoming WhatsApp Messages ===
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip().lower()
    from_number = request.values.get("From", "")
    resp = MessagingResponse()

    if incoming_msg == "otp":
        otp = generate_otp()
        expiry = datetime.utcnow() + timedelta(days=5)
        expiry_str = expiry.strftime("%Y-%m-%d %H:%M UTC")

        # Store OTP in Firestore
        db.collection("parcel_otps").add({
            "phone": from_number.replace("whatsapp:+60", "0"),
            "otp": otp,
            "expires_at": expiry
        })

        reply_text = f"📦 Your Kolej 14 Parcel OTP is: {otp}\n🔒 Valid until: {expiry_str}"
        resp.message(reply_text)

    else:
        # AI handles other messages
        ai_reply = ask_ai(incoming_msg)
        resp.message(ai_reply)

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
