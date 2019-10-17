from __future__ import print_function

from future.utils import listvalues
from waitress.server import TcpWSGIServer
import select

class StoppableWSGIServer(TcpWSGIServer):
    
    def Run(self):
        print('serving on http://{0}:{1}'.format(
            self.effective_host,
            self.effective_port))
        try:
            self.run()
        except select.error:
            if not self.shutdown_requested:
                raise

    def Shutdown(self):
        self.shutdown_requested = True
        self.task_dispatcher.shutdown()
        for channel in listvalues(self._map):
            channel.close()
