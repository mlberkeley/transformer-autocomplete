import bottle
import json
import platform
import sys
import time
import traceback
import completer
from bottle import request
from utils import StartThread, LOGGER

bottle.Request.MEMFILE_MAX = 10 * 1024 * 1024

_server_state = None
app = bottle.Bottle()
wsgi_server = None

@app.post('/completions')
def GetCompletions():
    #request_data = RequestWrap(request.json)
    LOGGER.info(request.json)
    print(request.json)
    LOGGER.info('Received completion request')
    errors = None
    completions = completer.ComputeCandidates(request.json)
    LOGGER.debug('completions: {}'.format(completions))
    resp = {
        'completions': completions,
        'completion_start_column': request.json['column_num'], #request.json['column_num'],
    }
    return _JsonResponse(resp)

@app.get('/healthy')
def GetHealthy():
    LOGGER.info('Received health request')
    return _JsonResponse(True)

@app.get('/ready')
def GetReady():
    pass

@app.post('/shutdown')
def Shutdown():
    LOGGER.info( 'Received shutdown request' )
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
    LOGGER.info('Server shutdown')
    def Terminator():
        if wsgi_server:
            wsgi_server.Shutdown()
    StartThread(Terminator)

def ServerCleanup():
    if _server_state:
        _server_state.Shutdown()

def UpdateUserOptions( options ):
    pass
