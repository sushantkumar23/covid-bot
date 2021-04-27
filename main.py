# main.py
import os
from pymongo import MongoClient
from fastapi import FastAPI, Request
from twilio.rest import Client

app = FastAPI()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
MONGO_URI = os.getenv('MONGO_URI')

client = Client(account_sid, auth_token)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()

leads = db['leads']
whatsapp_requests = db['whatsapp_requests']
whatsapp_responses = db['whatsapp_responses']

@app.get("/")
def hello_world():
    return "Hello World", 200


@app.post("/incoming_message")
async def incoming_message(request: Request):

    form_data = await request.form()
    incoming_message = dict(form_data)
    print("incoming_request: {}".format(incoming_message))

    whatsapp_requests.insert_one(incoming_message)

    message_body = """
    The following leads are available in Mumbai for Oxygen:

    1. Oxygen Services
    Contact: +91 9823656281

    2. HelpNow
    Contact: +91 8822288222

    3. Hemkunt Foundation
    Contact: +91 9899930828
    """

    # Reponse for Whatsapp
    wa_response = {
        "from": "whatsapp:+14155238886",
        "to": incoming_message["From"],
        "body": message_body
    }

    message = client.messages.create(
        from_=wa_response["from"],
        body=wa_response["body"],
        to=wa_response["to"]
    )

    whatsapp_responses.insert_one(wa_response)
    print(message.sid)


@app.post("/status")
def status(request):
    request_status = request.values.get("Body", '')
    print(request_status)
