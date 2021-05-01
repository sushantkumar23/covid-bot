import unittest
from datetime import date
from dto.lead import Lead


class LeadTestCase(unittest.TestCase):
    def test_lead(self):
        resource_name = "Popular Store"
        contact_number = 1234567890
        lead_index = 1
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": date(2021, 3, 1),
                  "url": "https://www.google.com"}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.contact_line, f'\nContact: {contact_number}')
        self.assertEqual(lead.url_line, "\ngoogle.com")
        self.assertEqual(lead.last_verified_line, "\n_Last verified: March 1st_")
        self.assertEqual(str(lead),
                         """1. Popular Store
Contact: 1234567890
google.com
_Last verified: March 1st_""")

    def test_lead_without_contact(self):
        resource_name = "Popular Store"
        lead_index = 1
        db_row = {"name": resource_name, "contact_number": None, "last_verified": date(2021, 3, 12),
                  "url": "www.google.com"}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.contact_line, '')
        self.assertEqual(lead.url_line, "\ngoogle.com")
        self.assertEqual(lead.last_verified_line, "\n_Last verified: March 12th_")
        self.assertEqual(str(lead),
                         """1. Popular Store
google.com
_Last verified: March 12th_""")

    def test_lead_without_url(self):
        resource_name = "Popular Store"
        contact_number = 1234567890
        lead_index = 1
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": date(2021, 3, 12),
                  "url": None}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.last_verified_line, "\n_Last verified: March 12th_")
        self.assertEqual(lead.url_line, "")
        self.assertEqual(str(lead),
                         """1. Popular Store
Contact: 1234567890
_Last verified: March 12th_""")

    def test_lead_without_last_verified_date(self):
        resource_name = "Popular Store"
        contact_number = 1234567890
        lead_index = 20
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": None,
                  "url": "http://www.google.com"}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.contact_line, f'\nContact: {contact_number}')
        self.assertEqual(lead.last_verified_line, "")

        self.assertEqual(str(lead),
                         """20. Popular Store
Contact: 1234567890
google.com""")

    def test_lead_with_only_contact_others_none(self):
        resource_name = "Popular Store"
        contact_number = 123
        lead_index = 2
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": None, "url": None}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.contact_line, f'\nContact: {contact_number}')
        self.assertEqual(lead.last_verified_line, "")
        self.assertEqual(lead.url_line, "")

        self.assertEqual(str(lead),
                         """2. Popular Store
Contact: 123""")

    def test_lead_with_only_contact_others_empty(self):
        resource_name = "Popular Store"
        contact_number = 1230
        lead_index = 20
        db_row = {"name": resource_name, "contact_number": contact_number, "last_verified": "", "url": ""}
        lead = Lead(db_row, lead_index)

        self.assertEqual(lead.name, resource_name)
        self.assertEqual(lead.lead_index, lead_index)
        self.assertEqual(lead.contact_line, f'\nContact: {contact_number}')
        self.assertEqual(lead.last_verified_line, "")
        self.assertEqual(lead.url_line, "")

        self.assertEqual(str(lead),
                         """20. Popular Store
Contact: 1230""")


if __name__ == '__main__':
    unittest.main()
