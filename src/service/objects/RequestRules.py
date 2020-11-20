import logging
from time import time


class RuleManager():
    def __init__(self):
        self.rules = set()
        self.pending_requests = 0

    def add_rule(self, rule):
        self.rules.add(rule)

    def expire_rules(self):
        rules = self.rules.copy()
        for rule in rules:
            if rule.expire_rule():
                self.rules.remove(rule)

    def authorize(self):
        # Remove expired rules before evaluating authorization
        self.expire_rules()

        # Evaluate all rules
        can_request = [rule.allow_request(self.pending_requests)
                       for rule in self.rules]
        logging.info('Rules: %s\nPending: %s' %
                     (can_request, self.pending_requests))

        # Deny request if:
        # * Any of these rules return False
        # * There are no rules and at least 1 pending request
        allowed = (False not in can_request and len(can_request) > 0) or (
            len(can_request) == 0 and self.pending_requests == 0)
        return allowed

    def increment_request_counter(self):
        [rule.add_current_requests() for rule in self.rules]

    def promise_request(self):
        self.pending_requests += 1

    def fulfill_request(self):
        self.pending_requests -= 1

    def has_pending_requests(self):
        return self.pending_requests > 0

    def parse_handler_response(self, payload):
        # A pending request has been completed
        self.fulfill_request()
        logging.info('Status code: %s' % payload['status_code'])
        headers = payload['headers']
        try:
            base_rules = headers['x-rate-limit-ip'][-1].split(',')
            current_state = headers['x-rate-limit-ip-state'][-1].split(',')
            for rule, state in zip(base_rules, current_state):
                # 12:6:60 -  Maximum of 12 requests within 6 seconds.
                # 60 seconds of timeout if threshold is exceeded.
                rule_info = rule.split(':')

                # 1:6:0 - Where we are at. 1 request has been made within
                # 6 seconds. Therefore, it takes 0 seconds of timeout
                state_info = state.split(':')

                # Ensure both objects refers to the same rule
                assert rule_info[1] == state_info[1]

                current_state = int(state_info[0])
                maximum_requests = int(rule_info[0])
                duration = int(rule_info[1])
                self.add_rule(RequestRule(duration, maximum_requests,
                                          current_state=current_state))

        except (IndexError, KeyError, AssertionError) as e:
            logging.error('Unable to parse rule.\n%s' % e)
            raise


class RequestRule():
    def __init__(self, duration, maximum_requests, current_state=0):
        self.rule_duration = time() + duration
        self.current_state = current_state
        self.maximum_requests = maximum_requests
        logging.info('A new rule has been added: %s requests in %s seconds' %
                     (maximum_requests, duration))

    def allow_request(self, pending_requests=0):
        # Requests can only be authorized if below maximum threshold
        return (self.current_state + pending_requests) < self.maximum_requests

    def add_current_requests(self):
        self.current_state = self.current_state + 1

    def expire_rule(self):
        # Rules can only be expired once their set timer runs out
        return time() > self.rule_duration
