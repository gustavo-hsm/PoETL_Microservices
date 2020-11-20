class ExchangeItem():
    def __init__(self, want, have):
        self.want = []
        self.have = []

        if type(want) == str:
            self.want.append(want)
        else:
            self.want = list(want)

        if type(have) == str:
            self.have.append(have)
        else:
            self.have = list(have)

        self.payload = self._compose_payload()

    def _compose_payload(self):
        return {
            'exchange': {
                'status': {
                    'option': 'any'
                },
                'want': [x for x in self.want],
                'have': [x for x in self.have],
            }
        }

    def get_payload(self):
        return self.payload
