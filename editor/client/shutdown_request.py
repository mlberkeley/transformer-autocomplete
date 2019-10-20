#from base_request import BaseRequest
from test_request import TestRequest

TIMEOUT_SECONDS = 0.1

class ShutdownRequest(TestRequest):
    def __init__(self, loc):
        super(ShutdownRequest, self).__init__(None) #Change when B_R works
        self.loc = loc

    def Start(self):
        self.PostDataToHandler({},  
                               'shutdown',
                               TIMEOUT_SECONDS,
                               display_message=False,
                               loc=self.loc)

def SendShutdownRequest(loc=None):
    print("Sending shutdown request")
    request = ShutdownRequest(loc=loc)
    request.Start()
