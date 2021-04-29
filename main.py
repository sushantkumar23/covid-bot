import os
import re
from pymongo import MongoClient
from fastapi import FastAPI, Request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse


app = FastAPI()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
MONGO_URI = os.getenv('MONGO_URI')
NUM_LEADS = 5
NUM_IND_LEADS = 5

client = Client(account_sid, auth_token)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()

leads = db['leads']
whatsapp_requests = db['whatsapp_requests']
whatsapp_responses = db['whatsapp_responses']

instructions = """
Resources available:

1. Oxygen - 💨
2. Beds - 🛏
3. Injections - 💉
4. Ambulance - 🚑
5. Helpline - ☎️
6. Plasma - 🩸

Locations covered:

· Mumbai (MUM) · Delhi (DEL) · Bangalore (BLR) · Chennai (CHE) · Kolkata (KOL) · Pune (PUN) · Lucknow (LUK) · Ahmedabad (AMD) · Gurgaon (GGN)

If you are looking for Oxygen in Mumbai then reply with the following message (NOT case sensitive): 

MUM Oxygen
"""

onboard_msg = """
Hi! I’m Covid-INDIA Bot🤖

Here to assist with some relevant leads in this distressful times. Stay hopeful 🤞🏻
{}
I’ll get back with the best information available. Take care! 🙏

* IMPORTANT *
In case you have any verified contacts you would like to share, please send a message in the following format:

For a plasma donor in Mumbai, please reply SEND MUM 6 Name Contact

Any leads you share can help save many lives 🙏. Please join us to help India fight back Coronavirus 🦠
""".format(instructions)


def build_msg(item, lead_idx):
    contact_line = ""
    url_line = ""
    if item["contact_number"] != "":
        contact_line = "\nContact: {}".format(item["contact_number"])
    url = item["url"]
    if url != "":
        url = url.replace('https://', '')
        url = url.replace('http://', '')
        url = url.replace('www.', '')
        url_line = "\n{}".format(url)
    retval = """
{}. {} {} {}
            """.format(lead_idx, item["name"], contact_line, url_line)
    return retval


@app.get("/")
def hello_world():
    return "Hello World", 200


@app.post("/incoming_message", status_code=201)
async def handle_request(request: Request):
    form_data = await request.form()
    incoming_message = dict(form_data)
    print("incoming_request: {}".format(incoming_message))

    prev_message_count = whatsapp_requests.count_documents({'From': incoming_message['From']})
    whatsapp_requests.insert_one(incoming_message)

    message = incoming_message["Body"]
    # example_message = "MUM - Oxygen", "MUM Oxygen"

    try:
        if "-" in message:
            msg_parts = message.split('-')
        else:
            msg_parts = message.split(' ')

        lead_idx = 0
        filters = []

        for msg_part in msg_parts:
            if msg_part != '':
                filters.append(msg_part)
        city = filters[0].strip().upper()
        resource = filters[1].strip().lower()
        db_filter = {
            'region': city,
            'resource': resource
        }

        # Check if there are any results for this search; if not then throw exception
        count = leads.count_documents(db_filter)

        # If results are non-zero then go ahead
        cursor = leads.find(db_filter).limit(NUM_LEADS).sort("_id", -1)
        lead_str = ""

        for index, item in enumerate(cursor):
            lead_idx += 1
            lead_str += build_msg(item, lead_idx)
        cursor.close()

        # Look for nearby cities if number of leads less than NUM_LEADS
        if count < NUM_LEADS:
            nearby_city_filter = {
                'nearby_regions': {'$in': [city]},
                'resource': resource
            }
            cursor = leads.find(nearby_city_filter).limit(NUM_LEADS - count).sort("_id", -1)
            for index, item in enumerate(cursor):
                lead_idx += 1
                lead_str += build_msg(item, lead_idx)
            cursor.close()

        # Look for all india leads
        india_leads = {
            'region': "IND",
            'resource': resource
        }
        cursor = leads.find(india_leads).limit(NUM_IND_LEADS).sort("_id", -1)
        for index, item in enumerate(cursor):
            lead_idx += 1
            lead_str += build_msg(item, lead_idx)
        cursor.close()

        message_body = """
        The following leads are available in {} for {}:
        {}
        """.format(city, resource, lead_str)

        if lead_idx == 0:
            message_body = """
*Sorry, no results.*
Please follow the instructions below
{}
                        """.format(instructions)

    except Exception as e:
        print(e)
        if prev_message_count == 0:
            message_body = onboard_msg
        else:
            message_body = """
*Invalid search format!*
Please follow the instructions below
{}
            """.format(instructions)

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
    print(message.sid)
    # resp = MessagingResponse()
    # msg = resp.message()
    # msg.body(message_body)

    # Insert into the database for logging
    whatsapp_responses.insert_one(wa_response)

    return "success"


@app.post("/status")
def status(request: Request):
    return "Hello World"
