class HeaderData:
    def __init__(self, bearerToken: str, baggage: str, sentry: str, requestID: str):
        self.bearerToken: str = bearerToken
        self.baggage: str = baggage
        self.sentry: str = sentry
        self.requestID: str = requestID