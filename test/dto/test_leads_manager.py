import unittest
from dto.leads_manager import LeadsManager
from datetime import date


class LeadsManagerTestCase(unittest.TestCase):
    def test_leads_manager(self):
        resource_name = "Popular Store"
        contact_number = 1234567890
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": date(2021, 3, 1),
                  "url": "https://www.google.com"}
        leads_manager = LeadsManager([db_row])

        self.assertEqual(len(leads_manager.leads), 1)
        self.assertFalse(leads_manager.is_empty())
        self.assertEqual(leads_manager.leads_str(),
                         """1. Popular Store
Contact: 1234567890
google.com
_Last verified: March 1st_""")

    def test_adding_leads(self):
        db_row = {"name": "Popular Store", "contact_number": 1234567890, "last_verified": date(2021, 4, 22),
                  "url": "https://www.google.com"}
        leads_manager = LeadsManager([db_row])

        db_row2 = {"name": "Another Store", "contact_number": 1234567891, "last_verified": date(2021, 4, 21),
                   "url": "www.yahoo.com"}

        leads_manager.add_leads([db_row2])
        self.assertEqual(len(leads_manager.leads), 2)
        self.assertFalse(leads_manager.is_empty())
        self.assertEqual(leads_manager.leads_str(),
                         """1. Popular Store
Contact: 1234567890
google.com
_Last verified: April 22nd_

2. Another Store
Contact: 1234567891
yahoo.com
_Last verified: April 21st_""")


if __name__ == '__main__':
    unittest.main()
