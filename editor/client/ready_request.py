from test_request import TestRequest

TIMEOUT_SECONDS = 0.1
COMPLETER = 'transformer'

class ReadyRequest(TestRequest):
    def __init__(self, loc):
        super(ReadyRequest, self).__init__(None)
        self.loc = loc

    def Start(self):
        self._response_future = self.PostDataToHandlerAsync({},
                                                            'ready',
                                                            loc=self.loc)

    def Done(self):
        return bool(self._response_future) and self._response_future.done()

    def Response(self):
        if not self._response_future:
            return {"result", 0}
        response = self.HandleFuture(self._response_future,
                                     truncate_message=True)
        if response is None:
            print("uwu, I am sad")
        return response

def SendReadyRequest(loc=None):
    print("Sending ready request")
    request = ReadyRequest(loc=loc, data={'completer':COMPLETER})
    request.Start()
