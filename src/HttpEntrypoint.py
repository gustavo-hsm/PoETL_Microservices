import os

from flask import Flask, request

from nameko.standalone.rpc import ClusterRpcProxy


app = Flask(__name__)
usr = os.environ['USER']
pwd = os.environ['PASS']
host = os.environ['HOST']
service_config = {'AMQP_URI': 'amqp://%s:%s@%s' % (usr, pwd, host)}


@app.route('/', methods=['GET'])
def home():
    return 'Hello World'


@app.route('/attach', methods=['POST'])
def attach_topic():
    try:
        data = request.json
        if all(key in data for key in ('want', 'have')):
            with ClusterRpcProxy(service_config) as rpc:
                status_code, response = rpc.exchange_topic_pool.\
                                        add_topic(data)
                return response, status_code
        else:
            return 'Required arguments: %s\n Found: %s' %\
                ([x for x in ['want', 'have']],
                 [x for x in data]), 400
    except TypeError as e:
        return 'Malformed request\n%s' % e, 400


@app.route('/detach/<index>', methods=['GET'])
def detach_topic(index):
    try:
        index = int(index)
    except ValueError:
        return 'Index must be an integer', 400
    else:
        with ClusterRpcProxy(service_config) as rpc:
            status_code, response = rpc.exchange_topic_pool.\
                                    retrieve_topic(index)
            return response, status_code


@app.route('/clear', methods=['GET'])
def clear_topics():
    with ClusterRpcProxy(service_config) as rpc:
        status_code, response = rpc.exchange_topic_pool.\
                                clear_topics()
        return response, status_code


@app.route('/topics', methods=['GET'])
def describe_topics():
    with ClusterRpcProxy(service_config) as rpc:
        status_code, response = rpc.exchange_topic_pool.\
                                describe_topic_pool()
        return response, status_code


@app.route('/engine/start', methods=['GET'])
def start_engine():
    with ClusterRpcProxy(service_config) as rpc:
        status_code, response = rpc.request_engine.start()
        return response, status_code


@app.route('/engine/queue', methods=['GET'])
def describe_queue():
    with ClusterRpcProxy(service_config) as rpc:
        response = rpc.request_engine.describe_queue()
        return response, 200


if __name__ == "__main__":
    app.run('localhost', debug=True)
