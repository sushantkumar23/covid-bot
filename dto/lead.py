class Lead:
    """ Represents formatted message to be sent to users """
    def __init__(self, item, lead_index):
        self.lead_index = lead_index
        self.name = item["name"]
        self.contact_line = ""
        self.url_line = ""
        self.last_verified_line = ""

        contact_number = item["contact_number"]
        if contact_number:
            self.contact_line = f"\nContact: {contact_number}"

        url: str = item["url"]
        if url:
            self.url_line = f"\n{url.replace('https://', '').replace('http://', '').replace('www.', '')}"

        if "last_verified" in item:
            last_verified = item["last_verified"]
            if last_verified:
                self.last_verified_line = f"\n_Last verified: {Lead.custom_strftime('%B {S}', last_verified)}_"

    def __str__(self) -> str:
        return f'{self.lead_index}. {self.name}{self.contact_line}{self.url_line}{self.last_verified_line}'

    @staticmethod
    def custom_strftime(time_format, t):
        return t.strftime(time_format).replace('{S}', str(t.day) + Lead.suffix(t.day))

    @staticmethod
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
