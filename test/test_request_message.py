import unittest
from request_message import RequestMessage


class RequestMessageTestCase(unittest.TestCase):
    def test_request_message(self):
        req_msg = RequestMessage("DEL Oxygen")
        self.assertEqual(req_msg.city, "DEL")
        self.assertEqual(req_msg.resource, "oxygen")  # the stored value is in lower case

    def test_request_messages_with_dash_as_sep(self):
        req_msg = RequestMessage("DEL-Beds")
        self.assertEqual(req_msg.city, "DEL")
        self.assertEqual(req_msg.resource, "beds")  # the stored value is in lower case

    def test_invalid_message(self):
        self.assertRaises(ValueError, RequestMessage, "Invalid")
        self.assertRaises(ValueError, RequestMessage, "Invalid Invalid")
        self.assertRaises(ValueError, RequestMessage, "Invalid Invalid Invalid")

    def test_mis_spelled_resources(self):
        req_msg = RequestMessage("DEL-Besd")
        self.assertEqual(req_msg.city, "DEL")

        self.assertEqual(req_msg.resource, "beds")
        self.assertEqual(RequestMessage("DEL-plamsa").resource, "plasma")
        self.assertEqual(RequestMessage("DEL-lpasma").resource, "plasma")
        self.assertEqual(RequestMessage("DEL-xygen").resource, "oxygen")
        self.assertEqual(RequestMessage("DEL-injection").resource, "injections")
        self.assertEqual(RequestMessage("DEL-ambulanec").resource, "ambulance")
        self.assertEqual(RequestMessage("DEL-helplin").resource, "helpline")
        self.assertEqual(RequestMessage("DEL-hepline").resource, "helpline")


if __name__ == '__main__':
    unittest.main()
