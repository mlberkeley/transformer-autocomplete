## Adapted from YCM
try:
    import vim
    import vimsupport
except ImportError:
    print("No vim for baserequest.")
import json
import logging
from future.utils import native
try:
    from utils import GetCurrentDirectory, ToBytes, urljoin, get_data
except ImportError:
    import sys
    sys.path.insert(0, '../')
    from utils import GetCurrentDirectory, ToBytes, urljoin, get_data

_READ_TIMEOUT_SEC = 30 
_HEADERS = {'content-type': 'application/json'}
_CONNECT_TIMEOUT_SEC = 1.
_logger = logging.getLogger('gpt')

class BaseRequest(object):

    def __init__(self):
        self._should_resend = False

    def Start(self):
        pass

    def Done(self):
        return True

    def Response(self):
        return {}

    def ShouldResend(self):
        return self._should_resend

    def GetDataFromHandler(self,
                           handler,
                           timeout=_READ_TIMEOUT_SEC,
                           display_message=True,
                           truncate_message=False,):
        self.HandleFuture(
            BaseRequest._TalkToHandlerAsync('', handler, 'GET', timeout),
            display_message,
            truncate_message)
        
    def HandleFuture(self,
                     future,
                     display_message=True,
                     truncate_message=False,):
        try:
            return _JsonFromFuture(future)
        except BaseRequest.Requests().exceptions.ConnectionError as e:
            print("Yikes! ConnectionError {}".format(e))
            _logger.error(e)
        except Exception as e:
            print("other exception {}".format(e))    
            print(e.msg)
            print(e.doc)
            _logger.exception(e)
            _logger.exception(e.msg)
            _logger.exception(e.doc)
            #DisplayServerException(e, truncate_message)
        return None

    @staticmethod 
    def PostDataToHandlerAsync(data, handler, timeout=_READ_TIMEOUT_SEC):
        _logger.info('Posting data to handler')
        return BaseRequest._TalkToHandlerAsync(data, handler, 'POST', timeout)

    def PostDataToHandler( self,
                           data,
                           handler,
                           timeout = _READ_TIMEOUT_SEC,
                           display_message = True,
                           truncate_message = False ):
        return self.HandleFuture(
            BaseRequest.PostDataToHandlerAsync( data, handler, timeout ),
            display_message,
            truncate_message )
        
    @staticmethod
    def _TalkToHandlerAsync(data,
                            handler,
                            method,
                            timeout = _READ_TIMEOUT_SEC):
        request_uri = _BuildUri(handler)
        _logger.info('Talking to handler async')
        if method == 'POST':
            sent_data = _ToUtf8Json(data)
            return BaseRequest.Session().post(
                request_uri,
                data=sent_data,
                headers=BaseRequest._ExtraHeaders(method,
                                                  request_uri,
                                                  sent_data),
                timeout=(_CONNECT_TIMEOUT_SEC, timeout))
        return BaseRequest.Session().get(
            request_uri,
            headers = BaseRequest._ExtraHeaders(method,
                                                request_uri,),
            timeout=(_CONNECT_TIMEOUT_SEC, timeout))

    @staticmethod
    def _ExtraHeaders( method, request_uri, request_body = None ):
        if not request_body:
            request_body = bytes( b'' )
        headers = dict( _HEADERS )
#    headers[ _HMAC_HEADER ] = b64encode(
#        CreateRequestHmac( ToBytes( method ),
#                           ToBytes( urlparse( request_uri ).path ),
#                           request_body,
#                           BaseRequest.hmac_secret ) )
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

def BuildRequestDataTest(buffer_number=None):
    working_dir = GetCurrentDirectory() #TODO
    # We're going to assume that we only care about the current buffer.
    line = 4
    column = 4
    current_filepath = '/Users/phil/nvidia/editor/test/test.txt'
    return {
        'filepath': current_filepath,
        'line_num': line + 1,
        'column_num': column + 1,
        'working_dir': working_dir,
        'file_data': get_data(current_filepath)
    }
def BuildRequestData(buffer_number=None):
    working_dir = GetCurrentDirectory() #TODO
    current_buffer = vim.current.buffer #TODO: vim
    # We're going to assume that we only care about the current buffer.
    current_filepath = vimsupport.GetBufferFilepath(current_buffer)
    line, column = vimsupport.CurrentLineAndColumn()
    
    return {
	'filepath': current_filepath,
	'line_num': line + 1,
	'column_num': column + 1,
	'working_dir': working_dir,
	'file_data': vimsupport.GetUnsavedAndSpecifiedBufferData( current_buffer,
				      current_filepath )
    }

#def _LoadExtraConfFile( filepath ):
#    BaseRequest().PostDataToHandler( { 'filepath': filepath },
#                                       'load_extra_conf_file' )

#def _IgnoreExtraConfFile( filepath ):
#    BaseRequest().PostDataToHandler( { 'filepath': filepath },
#                                       'ignore_extra_conf_file' )

def _ToUtf8Json(data):
  return ToBytes(json.dumps(data) if data else None)

def DisplayServerException( exception, truncate_message = False ):
    serialized_exception = str( exception )

  # We ignore the exception about the file already being parsed since it comes
  # up often and isn't something that's actionable by the user.
    if 'already being parsed' in serialized_exception:
        return
    vimsupport.PostVimMessage( serialized_exception, truncate = truncate_message )

def _JsonFromFuture(future):
    response = future.result()
    #_validateResponseObject(response)
    if response.status_code == BaseRequest.Requests().codes.server_error:
        raise MakeServerException(response.json())
    response.raise_for_status()

    if response.text:
        return response.json()
    return None
def _LoadExtraConfFile( filepath ):
    BaseRequest().PostDataToHandler( { 'filepath': filepath },
                                       'load_extra_conf_file' )

def _IgnoreExtraConfFile( filepath ):
    BaseRequest().PostDataToHandler( { 'filepath': filepath },
                                       'ignore_extra_conf_file' )

def _BuildUri(handler):
    uri = native(ToBytes(urljoin(BaseRequest.server_location, handler)))
    print("URI from uri {} | params: {} {}".format(uri, BaseRequest.server_location, handler))
    _logger.info(uri)
    return uri

class ServerError(Exception):
    def __init__(self,message):
        super(ServerError, self).__init__(message)

def MakeServerException(data):
    return ServerError( '{0}: {1}'.format( data[ 'exception' ][ 'TYPE' ],
                                             data[ 'message' ] ) )
#def _ValidateResponseObject( response ):
#    our_hmac = CreateHmac( response.content, BaseRequest.hmac_secret )
#    their_hmac = ToBytes( b64decode( response.headers[ _HMAC_HEADER ] ) )
#    if not SecureBytesEqual( our_hmac, their_hmac ):
#        raise RuntimeError( 'Received invalid HMAC for response!' )
#    return True
