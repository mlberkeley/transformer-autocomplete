import bottle
import json
import platform
import sys
import time
import traceback
from bottle import request
from utils import StartThread

bottle.Request.MEMFILE_MAX = 10 * 1024 * 1024

_server_state = None
app = bottle.Bottle()
wsgi_server = None

@app.post('/event_notification')
def EventNotification():
    pass

@app.post('/run_completer_command')
def RunCompleterCommand():
    pass

@app.post('/completions')
def GetCompletions():
    #request_data = RequestWrap(request.json)
    errors = None
    completions = completer.ComputeCandidates(request.json)
    resp = {
        'completions': completions,
    }
    return _JsonResponse(resp)

@app.post('/filter_and_sort_candidates')
def FilterAndSortCandidates():
    pass

@app.get('/healthy')
def GetHealthy():
    pass

@app.get('/ready')
def GetReady():
    pass

@app.post('/shutdown')
def Shutdown():
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
    def Terminator():
        if wsgi_server:
            wsgi_server.Shutdown()
    StartThread(Terminator)

def ServerCleanup():
    if _server_state:
        _server_state.Shutdown()

def UpdateUserOptions( options ):
    pass
