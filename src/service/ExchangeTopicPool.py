from nameko.rpc import rpc


class ExchangeTopicPool():
    name = 'exchange_topic_pool'
    pool = []

    def get_pool_size(self):
        return len(self.pool)

    @rpc
    def add_topic(self, topic):
        self.pool.append(topic)
        return 200, 'Topic was successfully added to pool'

    @rpc
    def retrieve_topic(self):
        try:
            response = self.pool.pop()
        except IndexError:
            if self.get_pool_size() == 0:
                return 404, 'Pool is empty'
        else:
            return 200, response

    @rpc
    def clear_topics(self):
        pool_size = self.get_pool_size()
        self.pool.clear()
        return 200, 'Successfully cleared %s topics' % pool_size

    @rpc
    def describe_topic_pool(self):
        message = '%s Topic(s) in pool' % self.get_pool_size()
        counter = 0
        for topic in self.pool:
            message = message + '\n[%s] %s' % (counter, topic)
            counter += 1
        return 200, message
