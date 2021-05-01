from leven import levenshtein
import numpy as np


class RequestMessage:
    ALL_RESOURCES = ["oxygen", "beds", "injections", "ambulance", "helpline", "plasma"]

    def __init__(self, message: str):
        self.message = message.strip()
        self.is_help_message = self.message.lower() == "help"

        if "-" in self.message:
            msg_parts = self.message.split('-')
        else:
            msg_parts = self.message.split(' ')

        if len(msg_parts) != 2:  # additional check
            raise ValueError("Invalid resource")

        filters = [msg_part for msg_part in msg_parts if msg_part]

        self.city = filters[0].strip().upper()
        input_resource = filters[1].strip().lower()
        lev_scores = [levenshtein(res, input_resource) for res in self.ALL_RESOURCES]
        min_pos = np.argmin(np.array(lev_scores))
        if lev_scores[min_pos] < 4:
            self.resource = self.ALL_RESOURCES[min_pos]
        else:
            raise ValueError("Invalid resource")
