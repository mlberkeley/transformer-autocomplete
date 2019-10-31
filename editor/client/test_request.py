import json
import logging
import time
import argparse
from pprint import pprint
from future.utils import native
from cutils import GetCurrentDirectory, ToBytes, urljoin, ToUnicode, get_data

_READ_TIMEOUT_SEC = 30 
_HEADERS = {'content-type': 'application/json'}
_CONNECT_TIMEOUT_SEC = 0.01
NO_COMPLETIONS = {
    'line': -1,
    'column': -1,
    'completion_start_column': -1,
    'completions': []
}
_logger = logging.getLogger('gpt')

class TestRequest(object):

    def __init__(self, request_data):
        self.request_data = request_data
        self._should_resend = False

    def Start(self):
        self._response_future = self.PostDataToHandlerAsync(self.request_data,
                                                            'completions')
    def Done(self):
        return bool(self._response_future) and self._response_future.done()

    def _RawResponse(self):
        if not self._response_future:
            return NO_COMPLETIONS
        response = self.HandleFuture(self._response_future,
                                     truncate_message=True)
        errors = response.pop('errors', [])

        response['line'] = self.request_data['line_num']
        response['column'] = self.request_data['column_num']
        return response

    def Response(self):
        response = self._RawResponse()
        print("response is:")
        pprint(response)
        response['completions'] = self._ConvertCompletionDataToVimData(
            response['completions'])
        return response

    def _ConvertCompletionDataToVimData(self, completion_data ):
      # See :h complete-items for a description of the dictionary fields.
        print(list(completion_data['completions'].keys()))
        completion_data = completion_data['completions'] if 'completions' in completion_data else completion_data
        return {
            'word'     : completion_data[ 'insertion_text' ],
            'abbr'     : completion_data.get( 'menu_text', '' ),
            'menu'     : completion_data.get( 'extra_menu_info', '' ),
            'kind'     : ToUnicode( completion_data.get( 'kind', '' ) )[ :1 ].lower(),
            'equal'    : 1,
            'dup'      : 1,
            'empty'    : 1,
        }

    def ShouldResend(self):
        return self._should_resend

    def GetDataFromHandler(self,
                           handler,
                           timeout=_READ_TIMEOUT_SEC,
                           display_message=True,
                           truncate_message=False,):
        self.HandleFuture(
            TestRequest._TalkToHandlerAsync('', handler, 'GET', timeout),
            display_message,
            truncate_message)
        
    def HandleFuture(self,
                     future,
                     display_message=True,
                     truncate_message=False,):
        try:
            return _JsonFromFuture(future)
        except TestRequest.Requests().exceptions.ConnectionError as e:
            print("Yikes! ConnectionError {}".format(e))
            _logger.error(e)
        except Exception as e:
            print("other exception {}".format(e))    
            print(e.msg)
            print(e.doc)
            _logger.exception(e)
        return None

    def PostDataToHandler( self,
                           data,
                           handler,
                           timeout = _READ_TIMEOUT_SEC,
                           display_message = True,
                           truncate_message = False,
                           loc = None):
        return self.HandleFuture(
            TestRequest.PostDataToHandlerAsync(data, handler, timeout, loc),
            display_message,
            truncate_message )

    @staticmethod 
    def PostDataToHandlerAsync(data, handler, timeout=_READ_TIMEOUT_SEC, loc=None):
        _logger.info('Posting data to handler')
        return TestRequest._TalkToHandlerAsync(data, handler, 'POST', timeout, loc=loc)
        
    @staticmethod
    def _TalkToHandlerAsync(data,
                            handler,
                            method,
                            timeout = _READ_TIMEOUT_SEC,
                            loc=None):
        request_uri = _BuildUri(handler, loc)
        _logger.info('Talking to handler async')
        if method == 'POST':
            sent_data = _ToUtf8Json(data)
            print("sd:")
            print(sent_data)
            return TestRequest.Session().post(
                request_uri,
                data=sent_data,
                headers=TestRequest._ExtraHeaders(method,
                                                  request_uri,
                                                  sent_data),
                timeout=(_CONNECT_TIMEOUT_SEC, timeout))
        return TestRequest.Session().get(
            request_uri,
            headers = TestRequest._ExtraHeaders(method,
                                                request_uri,),
            timeout=(_CONNECT_TIMEOUT_SEC, timeout))

    @staticmethod
    def _ExtraHeaders( method, request_uri, request_body = None ):
        if not request_body:
            request_body = bytes( b'' )
        headers = dict( _HEADERS )
        return headers


    @classmethod
    def Requests( cls ):
        try:
            return cls.requests
        except AttributeError:
            import requests
            cls.requests = requests
            return requests
    @classmethod
    def Session(cls):
        try:
            return cls.session
        except AttributeError:
            from unsafe_thread_pool_executor import UnsafeThreadPoolExecutor
            from requests_futures.sessions import FuturesSession
            executor = UnsafeThreadPoolExecutor(max_workers=30)
            cls.session = FuturesSession(executor=executor)
            return cls.session

    server_location = ''


def _ToUtf8Json(data):
  return ToBytes(json.dumps(data) if data else None)

def BuildRequestData(buffer_number=None):
    working_dir = GetCurrentDirectory() #TODO
    # We're going to assume that we only care about the current buffer.
    line = 5
    column = 28
    current_filepath = '/Users/phil/nvidia/editor/test/test.txt'
    return {
        'filepath': current_filepath,
        'line_num': line + 1,
        'column_num': column + 1,
        'working_dir': working_dir,
        'file_data': get_data(current_filepath)
    }

def _JsonFromFuture(future):
    response = future.result()
    if response.status_code == TestRequest.Requests().codes.server_error:
        raise MakeServerException(response.json())
    response.raise_for_status()

    if response.text:
        return response.json()
    return None

def _BuildUri(handler, loc=None):
    if loc is None:
        uri = native(ToBytes(urljoin(TestRequest.server_location, handler)))
    else:
        uri = native(ToBytes(urljoin(loc, handler)))
    print("URI {}".format(uri))
    return uri

if __name__ == '__main__':
    import shutdown_request as sdr
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=0,
                        help='server port')
    
    args = parser.parse_args()
    server_port = args.port
    TestRequest.server_location = 'http://127.0.0.1:' + str(server_port)
    request_data = BuildRequestData()
    print("Request data from trq:")
    pprint(request_data)
    lcr = TestRequest(request_data)
    lcr.Start()
    
    def request_ready():
        return lcr.Done()
    def get_completion_response():
        response = lcr.Response()
        return response
    for i in range(1):
        if request_ready():
            response = get_completion_response()
            print("Got a response!")
            print(response)
    time.sleep(1)
    import sys
    sys.exit(0)
    print("Sending Shutdown Request")
    sdr.ShutdownRequest.server_location = TestRequest.server_location
    print("TR {}".format(TestRequest.server_location))
    print(sdr.ShutdownRequest.server_location)
    sdr.SendShutdownRequest(TestRequest.server_location)
