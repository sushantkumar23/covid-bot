import random
import string


class Helper:
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

    onboard_msg = f"""
    Hi! I’m Covid-INDIA Bot🤖

    Here to assist with some relevant leads in this distressful times. Stay hopeful 🤞🏻
    {instructions}
    I’ll get back with the best information available. Take care! 🙏

    * IMPORTANT *
    In case you have any verified contacts you would like to share, please send a message in the following format:

    For a plasma donor in Mumbai, please reply SEND MUM 6 Name Contact

    Any leads you share can help save many lives 🙏. Please join us to help India fight back Coronavirus 🦠
    """

    @staticmethod
    def generate_transaction_id():
        return ''.join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
