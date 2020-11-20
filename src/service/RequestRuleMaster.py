from nameko.rpc import rpc
from nameko.events import EventHandler

from objects.RequestRules import RuleManager


class RuleMaster():
    name = 'rule_master'
    rule_manager = RuleManager()

    @rpc
    def authorize(self):
        return self.rule_manager.authorize()

    @rpc
    def parse_handler_response(self, payload):
        self.rule_manager.parse_handler_response(payload)

    @rpc
    def promise_request(self):
        self.rule_manager.promise_request()

    @rpc
    def has_pending_requests(self):
        return self.rule_manager.has_pending_requests()
