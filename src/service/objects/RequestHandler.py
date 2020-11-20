import json
import requests

from nameko.standalone.events import event_dispatcher


class RequestFactory():
    def __init__(self, service_url):
        self.service_url = service_url

    def before_main_action(self, *args):
        raise NotImplementedError

    def main_action(self, *args):
        raise NotImplementedError

    def after_main_action(self, *args):
        raise NotImplementedError

    def execute(self, *args):
        self.before_main_action(*args)
        self.main_action(*args)
        self.after_main_action(*args)

    def compose_payload(self, response):
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers._store),
            'text': json.loads(response.text)
        }


class PostHandler(RequestFactory):
    def __init__(self, service_url, service_config, payload):
        super().__init__(service_url)
        self.topic_response = None
        self.payload = payload
        self.service_config = service_config

    def before_main_action(self, *args):
        return None

    # Execute the Post action
    def main_action(self, *args):
        self.topic_response = requests.post(url=self.service_url,
                                            json=self.payload)

    # Publish response
    def after_main_action(self, *args):
        event_dispatcher(self.service_config)(
            'post_handler', 'response',
            super().compose_payload(self.topic_response))


class FetchHandler(RequestFactory):
    def __init__(self, service_url, service_config):
        super().__init__(service_url)
        self.fetch_response = None
        self.service_config = service_config

    def before_main_action(self, *args):
        return None

    # Fetch results
    def main_action(self, *args):
        self.fetch_response = requests.get(url=self.service_url)

    # Publish response
    def after_main_action(self, *args):
        event_dispatcher(self.service_config)(
            'fetch_handler', 'response',
            super().compose_payload(self.fetch_response))
