import os
from pymongo import MongoClient
from fastapi import FastAPI, Request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse


app = FastAPI()

account_sid = os.getenv("ACCOUNT_SID")
auth_token = os.getenv("AUTH_TOKEN")
MONGO_URI = os.getenv('MONGO_URI')
NUM_LEADS = 5

client = Client(account_sid, auth_token)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()

leads = db['leads']
whatsapp_requests = db['whatsapp_requests']
whatsapp_responses = db['whatsapp_responses']


@app.get("/")
def hello_world():
    return "Hello World", 200


@app.post("/incoming_message", status_code=201)
async def handle_request(request: Request):
    form_data = await request.form()
    incoming_message = dict(form_data)
    print("incoming_request: {}".format(incoming_message))

    whatsapp_requests.insert_one(incoming_message)
    prev_message_count = whatsapp_requests.count_documents({'From': incoming_message['From']})

    # If this is the first message sent by the user then send him the introductory
    # message
    if prev_message_count == 0:
        message_body = """
Hi! I’m Covid-INDIA Bot🤖

Here to assist with some relevant leads in this distressful times. Stay hopeful 🤞🏻

Resources available:

1. Oxygen - 💨
2. Hospital Beds - 🛏
3. Injections - 💉
4. Ambulance - 🚑
5. Helpline - ☎️
6. Plasma - 🩸

Locations covered:

· Mumbai (MUM) · Delhi (DEL) · Bangalore (BLR) · Chennai (CHE) · Kolkata (KOL) · Pune (PUN) · Nagpur (NAG) · Lucknow (LUK) · Ahmedabad (AMD) · Gurgaon (GGN)

If you are looking for Oxygen in Mumbai then reply with the following message (NOT case sensitive):

MUM Oxygen Or MUM 1 Or *<city-code> <resource name or id>*

I’ll get back with the best information available. Take care! 🙏

------------------------- IMPORTANT ------------------------------
In case you have any verified contacts you would like to share, please send a message in the following format:

For a plasma donor in Mumbai, please reply SEND-MUM-6-Name-Contact

Any leads you share can help save many lives 🙏. Please join us to help India fight back Coronavirus 🦠
"""
    else:
        message = incoming_message["Body"]
        # example_message = "MUM - Oxygen", "MUM Oxygen"

        try:
            if "-" in message:
                filters = message.split('-')
            else:
                filters = message.split(' ')

            city = filters[0].strip().upper()
            resource = filters[1].strip().lower()
            db_filter = {
                'region': city,
                'resource': resource
            }

            # Check if there are any results for this search; if not then throw exception
            count = leads.count_documents(db_filter)
            if count == 0:
                raise Exception("No item found")

            # If results are non-zero then go ahead
            cursor = leads.find(db_filter).limit(NUM_LEADS).sort("_id", -1)
            lead_str = ""
            for index, item in enumerate(cursor):
                lead_str += """
                {}. {}
                Contact: +91 {}
                """.format(index + 1, item["name"], item["contact_number"])
            cursor.close()

            # Look for nearby cities if number of leads less than NUM_LEADS
            if count < NUM_LEADS:
                nearby_city_filter = {
                    'nearby_regions': {'$in': [city]},
                    'resource': resource
                }
                cursor = leads.find(nearby_city_filter).limit(NUM_LEADS - count).sort("_id", -1)
                for index, item in enumerate(cursor):
                    lead_str += """
                    {}. {}
                    Contact: +91 {}
                    """.format(index + 1 + count, item["name"], item["contact_number"])
                cursor.close()

            message_body = """
            The following leads are available in {} for {}:
            {}
            """.format(city, resource, lead_str)

        except Exception as e:
            print(e)
            message_body = "Either your search format was invalid or we could not find any results for your search."

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

    return str(resp)


@app.post("/status")
def status(request: Request):
    request_status = request.values.get("Body", '')
    print(request_status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
