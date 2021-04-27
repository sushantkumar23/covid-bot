# main.py
import os
from fastapi import FastAPI, Request
from twilio.rest import Client

app = FastAPI()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
client = Client(account_sid, auth_token)


@app.get("/")
    return "Hello World", 200

@app.post("/incoming_message")
def incoming_message(request: Request):
    incoming_msg = request.values.get('Body', '').lower()

    print("Incoming message: {}".format(incoming_msg))
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='The following leads are available in Mumbai for Oxygen cylinders:',
        to='whatsapp:+919619446401'
    )
    print(message.sid)

@app.post("/status")
def status(request):
    request_status = request.values.get("Body", '')
    print(request_status)
