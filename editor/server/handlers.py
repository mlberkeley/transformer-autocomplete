import bottle
import json
import platform
import sys
import time
import traceback
import completer
from bottle import request
from utils import StartThread, logfile
import logging

NO_COMPLETIONS = {
    'line': -1,
    'column': -1,
    'completion_start_column': -1,
    'completions': []
}

bottle.Request.MEMFILE_MAX = 10 * 1024 * 1024

_server_state = None
app = bottle.Bottle()
wsgi_server = None
print("Setting up transformer")
current_completer = completer.TransformerCompleter()
print("Set up transformer")
logging.basicConfig(filename=logfile, level=logging.DEBUG)
_logger = logging.getLogger('handler')

@app.post('/completions')
def GetCompletions():
    #request_data = RequestWrap(request.json)
    _logger.info(request.json)
    _logger.info('Received completion request')
    errors = None
    global _server_state
    if current_completer is not None:
        completions = current_completer.compute_candidates(request.json)
        _logger.debug('completions: {}'.format(completions))
        print(completions)
        resp = {
            'completions': completions,
            'completion_start_column': request.json['column_num'], #request.json['column_num'],
        }
        return _JsonResponse(resp)
    else:
        print("Current Completer Is None")
        _logger.info("Current Completer Is None")
        return _JsonResponse(NO_COMPLETIONS)

@app.get('/healthy')
def GetHealthy():
    _logger.info('Received health request')
    return _JsonResponse(True)

#@app.post('/params')
#def GetParams()
#    _logger.info('Received param reset request')
#    for k, v in response.json.items():
#        if hasattr(current_completer, k):
#            setattr(current_completer, k, v)

@app.post('/ready')
def GetReady():
    global current_completer 
    if current_completer is not None:
        return _JsonResponse({'result': 1})
    else:
        return _JsonResponse({'result': 0})


@app.post('/start')
def GetStart():
    global current_completer
    _logger.info('Received start request')
    _logger.info(request.json)
    print(request.json)
    comp_req = request.json['completer']
    if current_completer is not None:
        _logger.warning("Replacing completer")
    if comp_req == 'mirror':
        current_completer = completer.MirrorCompleter()
    elif comp_req == 'transformer':
        current_completer = completer.TransformerCompleter()
    else:
        print("Unrecognized completer option: {}".format(comp_req))
        raise ValueError

    return _JsonResponse(True)
    


@app.post('/shutdown')
def Shutdown():
    _logger.info( 'Received shutdown request' )
    ServerShutdown()
    return _JsonResponse(True)

def _JsonResponse(data):
    bottle.response.set_header('Content-Type', 'application/json')
    return json.dumps(data,
                      separators=(',',':'),
                      default=_UniversalSerialize)

def _UniversalSerialize(obj):
    try:
        serialized = obj.__dict__.copy()
        serialized['TYPE'] = type(obj).__name__
        return serialized
    except AttributeError:
        return str(obj)

def ServerShutdown():
    _logger.info('Server shutdown')
    def Terminator():
        if wsgi_server:
            wsgi_server.Shutdown()
    StartThread(Terminator)

def ServerCleanup():
    if _server_state:
        _server_state.Shutdown()

def UpdateUserOptions( options ):
    pass
#_current_completer = completer.TransformerCompleter()
