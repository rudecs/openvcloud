from framework.api import utils

class EmailSender:
    def __init__(self, api_client):
        self._api = api_client

    def send(self, sender_email, receiver_email, **kwargs):
        data = {
            'sender_email': sender_email,
            'receiver_email': receiver_email,
            'sender_name': utils.random_string(),
            'subject': utils.random_string(),
            'body': utils.random_string(),
        }
        data.update(**kwargs)
        return data, self._api.system.emailsender.send(** data)