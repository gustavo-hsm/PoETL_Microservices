import os
import json
import logging
import threading as th
from time import sleep

from nameko.events import event_handler
from nameko.rpc import rpc, RpcProxy

from objects.ExchangeItem import ExchangeItem
from objects.RequestHandler import PostHandler, FetchHandler
from objects.Queue import Queue


class RequestEngine():
    name = 'request_engine'
    pool_service = RpcProxy('exchange_topic_pool')
    rule_master = RpcProxy('rule_master')
    request_queue = Queue()

    usr = os.environ['USER']
    pwd = os.environ['PASS']
    host = os.environ['HOST']
    service_config = {'AMQP_URI': 'amqp://%s:%s@%s' % (usr, pwd, host)}

    league = os.environ['LEAGUE']
    FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/'
    EXCHANGE_URL = 'https://www.pathofexile.com/api/trade/exchange/' + league
    batch_size = 10

    @rpc
    def retrieve_topic(self):
        # Retrieve one topic from pool
        status_code, response = self.pool_service.retrieve_topic()

        # Initialize a PostHandler
        if status_code == 200:
            exchange_item = ExchangeItem(want=response.get('want'),
                                         have=response.get('have'))
            self.request_queue.add(PostHandler(self.EXCHANGE_URL,
                                               self.service_config,
                                               exchange_item.get_payload()))

    @rpc
    def describe_queue(self):
        return self.request_queue.describe()

    @rpc
    def start(self):
        self.retrieve_topic()
        if self.request_queue.get_queue_size() > 0:
            # Prioritizing PostHandlers first
            requests = self.request_queue.retrieve_by_type(PostHandler)
            self._execute_handler(requests)

            # Waiting for pending requests to complete
            while self.rule_master.has_pending_requests():
                logging.info('Incomplete requests. Waiting...')
                sleep(5)

            # Running remaining requests next
            remaining = self.request_queue.retrieve_all()
            self._execute_handler(remaining)
            return 200, 'Start cycle completed'
        else:
            return 404, 'Queue is empty'

    @rpc
    @event_handler('post_handler', 'response')
    def post_handler_response(self, payload):
        # Send this payload to RuleManager
        self.rule_master.parse_handler_response.call_async(payload)

        # Prepare all queries to fetch
        query_id = payload['text']['id']
        result = payload['text']['result']
        items = []

        while len(result) > self.batch_size:
            items.append([result.pop(0) for x in range(0, self.batch_size)])

        if len(result) > 0:
            items.append(result)

        # Generate FetchHandlers
        for item in items:
            query = self.FETCH_URL + ','.join(item) + '?query=' + query_id
            self.request_queue.add(FetchHandler(query, self.service_config))

    @rpc
    @event_handler('fetch_handler', 'response')
    def fetch_handler_response(self, payload):
        # Send this payload to RuleManager
        self.rule_master.parse_handler_response.call_async(payload)

    def _execute_handler(self, requests):
        while len(requests) > 0:
            if self.rule_master.authorize():
                self.rule_master.promise_request.call_async()
                next_up = requests.pop()
                th.Thread(target=next_up.execute).start()
            else:
                logging.info('Unauthorized. Waiting...')
                sleep(1)
