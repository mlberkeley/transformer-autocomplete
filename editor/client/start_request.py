from test_request import TestRequest

COMPLETER = 'transformer'
TIMEOUT_SECONDS = 0.1 if COMPLETER == 'mirror' else 0.5


class StartRequest(TestRequest):
    def __init__(self, loc, data):
        super(StartRequest, self).__init__(None)
        self.loc = loc
        self.data = data

    def Start(self):
        self.PostDataToHandler(self.data,
                                'start',
                                TIMEOUT_SECONDS,
                                loc=self.loc)

def SendStartRequest(loc=None):
    print("Sending Start request")
    request = StartRequest(loc=loc, data={'completer':COMPLETER})
    request.Start()

if __name__ == '__main__':
    loc = 'http://127.0.0.1:4200'
    SendStartRequest(loc=loc)
    if COMPLETER == 'transformer':
        from ready_request import ReadyRequest
        import time
        rr = ReadyRequest(loc=loc)
        rr.Start()
        for i in range(100):
            time.sleep(0.2)
            if rr.Done():
                print("DONE")
                resp = rr.Response()
                print(resp)
                if resp['result']:
                    break
        



