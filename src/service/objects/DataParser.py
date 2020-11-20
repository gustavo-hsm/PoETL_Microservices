import logging

from objects.Queue import Queue


class DataParser():
    queue = Queue()

    def parse(self, payload):
        raise NotImplementedError

    def publish(self):
        raise NotImplementedError

    def add_to_queue(self, data):
        self.queue.add(data)

    def get_queue_size(self):
        return self.queue.get_queue_size()

    def retrieve_one_from_queue(self):
        return self.queue.retrieve_one()

    def retrieve_all_from_queue(self):
        return self.queue.retrieve_all()

    def retrieve_by_type_from_queue(self, typeof):
        return self.queue.retrieve_by_type(typeof)


class ExchangeParser(DataParser):
    def parse(self, payload):
        try:
            for item in payload['text']['result']:
                try:
                    trade_register = {
                        'offer_id': item['id'],
                        'trade_league': item['item']['league'],
                        'buying_currency': None,
                        'buying_price': None,
                        'offer_currency': item['item']['typeLine'],
                        'offer_amount': 1,
                        'offer_total_stock': item['item']['stackSize'],
                        'acc_user': item['listing']['account']['name'],
                        'acc_user_online': item['listing']
                        ['account']['online'] is not None,
                        'indexed_time': item['listing']['indexed']
                    }

                    if item['listing'] is not None:
                        if item['listing']['price'] is not None:
                            trade_register['buying_currency'] = item[
                                'listing']['price']['currency']
                            trade_register['buying_price'] = round(item[
                                'listing']['price']['amount'])
                except (TypeError, AttributeError):
                    logging.info('Unable to parse this register:\n%s' % item)
                    continue
                else:
                    super().add_to_queue(trade_register)
        except KeyError as e:
            # Unexpected data format
            status_code = payload['status_code']

            # Evaluate status code. If its 200, the payload has probably
            # changed and the parser needs to be updated
            logging.error('Status code: %s\n' +
                          'Unable to parse this payload: %s\n%s' %
                          (status_code, payload, e))
            pass
