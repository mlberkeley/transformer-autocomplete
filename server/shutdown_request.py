from base_request import BaseRequest

TIMEOUT_SECONDS = 0.1

class ShutdownRequest(BaseRequest):
    def __init__(self):
        super(ShutdownRequest, self).__init__()

    def Start(self):
        self.PostDataToHandler({},  
                               'shutdown',
                               TIMEOUT_SECONDS,
                               display_messagte=False)


def SendShutdownRequest():
    request = ShutdownRequest()
    request.Start()
