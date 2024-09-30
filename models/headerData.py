class HeaderData:
    def __init__(self, bearerToken: str, baggage: str, sentry: str, requestID: str):
        self.bearerToken: str = bearerToken
        self.baggage: str = baggage
        self.sentry: str = sentry
        self.requestID: str = requestID

    def __str__(self):
        return f"Bearer Token: {self.bearerToken}\nBaggage: {self.baggage}\nSentry: {self.sentry}\nRequest ID: {self.requestID}"