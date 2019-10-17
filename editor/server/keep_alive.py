import time
from threading import Thread
from base_request import BaseRequest

class Keepalive(object):
    def __init__(self, ping_interval_seconds = 60 * 10):
        self._keepalive_thread = Thread(target=self._ThreadMain)
        self._keepalive_thread.daemon = True
        self._ping_interval_seconds = ping_interval_seconds

    def Start(self):
        self._keepalive_thread.start()

    def _ThreadMain(self):
        while True: 
            time.sleep(self._ping_interval_seconds)
            BaseRequest().GetDataFromHandler('healthy', display_message=False)
