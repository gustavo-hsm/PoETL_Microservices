import os

from nameko.events import event_handler
from nameko.rpc import rpc

import objects.DataSink as ds


class SinkEngine():
    name = 'sink_engine'
    file_dir = 'output/'
    file_prefix = 'RpcSink'

    # TODO: Allow new DataSink objects to be attached via the API
    sink_services = [ds.SinkToLocalJSON(file_dir, file_prefix)]

    @rpc
    @event_handler('exchange_parser', 'publish')
    def sink_exchange_data(self, payload):
        for service in self.sink_services:
            service.sink(payload)
