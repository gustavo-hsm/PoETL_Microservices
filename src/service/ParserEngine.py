

from nameko.rpc import rpc
from nameko.events import event_handler, EventDispatcher

from objects.DataParser import ExchangeParser


class ExchangeParserEngine(ExchangeParser):
    name = 'exchange_parser'
    dispatch = EventDispatcher()
    publish_threshold = 50

    def __init__(self):
        super().__init__()

    @rpc
    @event_handler('fetch_handler', 'response')
    def parse(self, payload):
        super().parse(payload)
        if super().get_queue_size() >= self.publish_threshold:
            self.publish()

    @rpc
    def publish(self):
        # TODO: Read Exchange data. Publish them onto dedicated currency queues
        self.dispatch('publish', super().retrieve_all_from_queue())
