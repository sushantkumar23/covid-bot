import os

from fastapi import FastAPI, Request, Response
from pymongo import MongoClient
from twilio.twiml.messaging_response import MessagingResponse

from dto.leads_manager import LeadsManager
from helper import Helper
from request_message import RequestMessage

app = FastAPI()

MONGO_URI = os.getenv('MONGO_URI')
DEV = bool(os.getenv("DEV"))  # any truthy value is True, falsy is False
NUM_LEADS = 5
NUM_IND_LEADS = 5

mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()

leads = db['leads']
whatsapp_requests = db['whatsapp_requests']
whatsapp_responses = db['whatsapp_responses']


def handle_message(message: str, user):
    prev_message_count = whatsapp_requests.count_documents({'From': user})
    try:
        req_msg = RequestMessage(message)
        if req_msg.is_help_message:
            return f'Please follow the instructions below\n{Helper.instructions}'

        db_filter = {
            'region': req_msg.city,
            'resource': req_msg.resource
        }

        # Check if there are any results for this search; if not then throw exception
        count = leads.count_documents(db_filter)

        # If results are non-zero then go ahead
        cursor = leads.find(db_filter).limit(NUM_LEADS).sort("_id", -1)
        leads_manager = LeadsManager(cursor)
        cursor.close()

        # Look for nearby cities if number of leads less than NUM_LEADS
        if count < NUM_LEADS:
            nearby_city_filter = {
                'nearby_regions': {'$in': [req_msg.city]},
                'resource': req_msg.resource
            }
            cursor = leads.find(nearby_city_filter).limit(NUM_LEADS - count).sort("_id", -1)
            leads_manager.add_leads(cursor)
            cursor.close()

        # Look for all india leads
        india_leads = {
            'region': "IND",
            'resource': req_msg.resource
        }
        cursor = leads.find(india_leads).limit(NUM_IND_LEADS).sort("_id", -1)
        leads_manager.add_leads(cursor)
        cursor.close()

        if leads_manager.is_empty():
            message_body = f"*Sorry, no results.*\nPlease follow the instructions below\n{Helper.instructions}"
        else:
            message_body = f"The following leads are available in {req_msg.city} for {req_msg.resource}:" \
                           f"{leads_manager.leads_str()}"

    except Exception as e:
        print(e)
        if prev_message_count == 0:
            message_body = Helper.onboard_msg
        else:
            message_body = f"*Invalid search format!*\nPlease follow the instructions below {Helper.instructions}"

    return message_body


@app.get("/")
def hello_world():
    return "Hello World", 200


@app.post("/incoming_message", status_code=201)
async def handle_request(request: Request):
    form_data = await request.form()
    incoming_message = dict(form_data)
    print("incoming_request: {}".format(incoming_message))
    transaction_id = Helper.generate_transaction_id()

    if not DEV:
        incoming_message["transaction_id"] = transaction_id
        whatsapp_requests.insert_one(incoming_message)

    message = incoming_message["Body"]
    user = incoming_message["From"]

    message_body = handle_message(message, user)

    if DEV:
        print(message_body)

    # Build Response
    wa_response = {
        "from": "whatsapp:+14155238886",
        "to": user,
        "body": message_body,
        "transaction_id": transaction_id
    }
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(message_body)

    if not DEV:
        # Insert into the database for logging
        whatsapp_responses.insert_one(wa_response)

    return Response(content=str(resp), media_type="application/xml")


@app.post("/status")
def status(request: Request):
    return "Hello World"
