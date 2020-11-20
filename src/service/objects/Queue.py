class Queue():
    def __init__(self):
        self.queue = []
        self.processed = []

    def add(self, item):
        self.queue.append(item)
        return len(self.queue)

    def retrieve_one(self):
        item = self.queue.pop()
        self.processed.append(item)
        return item

    def retrieve_all(self):
        items = self.queue.copy()
        self.processed.extend(items)
        self.queue.clear()
        return items

    def retrieve_by_type(self, typeof):
        try:
            items = [item for item in self.queue if isinstance(item, typeof)]
            assert len(items) > 0
            self.processed.extend(items)
            [self.queue.remove(x) for x in items]
        except ValueError as e:
            print('Error attempting to remove items from Queue\n%s' % e)
        except AssertionError:
            print('No items of type "%s" found in Queue' % typeof)
        finally:
            return items

    def get_queue_size(self):
        return len(self.queue)

    def get_processed_size(self):
        return len(self.processed)

    def describe(self):
        queue_size = self.get_queue_size()
        processed_size = self.get_processed_size()
        message = 'Objects pooled: %s\nObjects processed: %s'\
            % (queue_size, processed_size)
        if queue_size > 0:
            message += '\n-----------------------'
            message += '\nList of pooled objects'
            message += '\n-----------------------\n'
            message += '\n'.join(map(str, self.queue))
        if processed_size > 0:
            message += '\n-----------------------'
            message += '\nList of processed objects'
            message += '\n-----------------------\n'
            message += '\n'.join(map(str, self.processed))
        return message
