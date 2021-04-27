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


@app.post("/incoming_message", status_code=201)
async def incoming_message(request: Request):

    form_data = await request.form()
    incoming_message = dict(form_data)
    print("incoming_request: {}".format(incoming_message))

    whatsapp_requests.insert_one(incoming_message)

    message = incoming_message["Body"]
    # example_message = "MUM - Oxygen"

    try:
        filters = message.split('-')
        city = filters[0].strip().upper()
        resource = filters[1].strip()
        db_filter = {
            'region': city,
            'resource': resource
        }

        # Check if there are any results for this search; if not then throw exception
        count = leads.count_documents(db_filter)
        if count == 0:
            raise Exception("No item found")

        # If results are non-zero then go ahead
        cursor = leads.find(db_filter).limit(5)
        lead_str = ""
        for index, item in enumerate(cursor):
            lead_str += """
            {}. {}
            Contact: +91 {}
            """.format(index+1, item["name"], item["contact_number"])

        message_body = """
        The following leads are available in {} for {}:
        {}
        """.format(city, resource, lead_str)

    except Exception as e:
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

    whatsapp_responses.insert_one(wa_response)
    print(message.sid)


@app.post("/status")
def status(request: Request):
    request_status = request.values.get("Body", '')
    print(request_status)
