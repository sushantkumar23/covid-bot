from dto.lead import Lead
from typing import List


class LeadsManager:
    def __init__(self, cursor):
        self.leads: List[Lead] = []
        self.index = 1  # index counting to begin from 1
        self._parse_leads(cursor)

    def _parse_leads(self, cursor):
        for item in cursor:
            self.leads.append(Lead(item, self.index))
            self.index += 1

    def add_leads(self, cursor):
        self._parse_leads(cursor)

    def is_empty(self):
        return len(self.leads) == 0

    def leads_str(self):
        return '\n\n'.join(str(lead) for lead in self.leads)
