from base_request import BaseRequest
from shutdown_request import SendShutdownRequest
from subprocess import PIPE, Popen
from completion_request import CompletionRequest
from tempfile import NamedTemporaryFile

import paths
import base
import json
import os
import logging
import utils
import vimsupport
from pprint import pprint
from keep_alive import Keepalive

SERVER_IDLE_SUICIDE_SECONDS=1800
SERVER_SHUTDOWN_MESSAGE = (
    "The ycmd server SHUT DOWN (restart with ':YcmRestartServer')." )
EXIT_CODE_UNEXPECTED_MESSAGE = (
    "Unexpected exit code {code}. "
    "Type ':YcmToggleLogs {logfile}' to check the logs." )
CORE_UNEXPECTED_MESSAGE = (
    "Unexpected error while loading the YCM core library. "
    "Type ':YcmToggleLogs {logfile}' to check the logs." )
CORE_MISSING_MESSAGE = (
    'YCM core library not detected; you need to compile YCM before using it. '
    'Follow the instructions in the documentation.' )
CORE_PYTHON2_MESSAGE = (
    "YCM core library compiled for Python 2 but loaded in Python 3. "
    "Set the 'g:ycm_server_python_interpreter' option to a Python 2 "
    "interpreter path." )
CORE_PYTHON3_MESSAGE = (
    "YCM core library compiled for Python 3 but loaded in Python 2. "
    "Set the 'g:ycm_server_python_interpreter' option to a Python 3 "
    "interpreter path." )
CORE_OUTDATED_MESSAGE = (
    'YCM core library too old; PLEASE RECOMPILE by running the install.py '
    'script. See the documentation for more details.' )

class Completer(object):
    def __init__(self):
        self._buffers = None
        self._latest_completion_request = None
        self._keepalive = Keepalive()
        self._keepalive.Start()

        self._SetUpServer()
        #self._logger = logging.getLogger('gpt')

    def _SetUpServer(self):
        self._user_options = base.GetUserOptions()
        self._user_options['log_level'] = 0
        options_dict = dict(self._user_options)
        pprint(options_dict)
        server_port = utils.GetUnusedLocalhostPort()
        BaseRequest.server_location = 'http://127.0.0.1' + str(server_port)
        with NamedTemporaryFile(delete=False, mode='w+') as options_file:
            json.dump(options_dict, options_file)
        try:
            python_interpreter = paths.PathToPythonInterpreter()
        except RuntimeError as error:
            error_message = (
            "Unable to start the ycmd server. {0}. "
            "Correct the error then restart the server "
            "with ':YcmRestartServer'.".format( str( error ).rstrip( '.' ) ) )
            #self._logger.exception( error_message )
            vimsupport.PostVimMessage( error_message )
            return

        print(server_port)
        print(os.path.join(os.getcwd(), 'main.py'))
        args = [python_interpreter,
            os.path.join(os.getcwd(), 'main.py'), # server script path
            '--port={0}'.format(server_port),
            '--options_file={0}'.format(options_file.name),
            '--log={0}'.format(self._user_options['log_level']),
            '--idle_suicide_seconds={0}'.format(SERVER_IDLE_SUICIDE_SECONDS)]
        #TODO: add logging    
        self._server_popen = Popen(args)#, stdout=PIPE, stderr=PIPE)

    def IsServerAlive(self):
        return bool(self._server_popen) and self._server_popen.poll() is None

    def NotifyUserIfServerCrashed( self ):
        if ( not self._server_popen or self._user_notified_about_crash or
            self.IsServerAlive() ):
            return
        self._user_notified_about_crash = True

        return_code = self._server_popen.poll()
        logfile = os.path.basename( self._server_stderr )
        # See https://github.com/Valloric/ycmd#exit-codes for the list of exit
        # codes.
        if return_code == 3:
            error_message = CORE_UNEXPECTED_MESSAGE.format( logfile = logfile )
        elif return_code == 4:
            error_message = CORE_MISSING_MESSAGE
        elif return_code == 5:
            error_message = CORE_PYTHON2_MESSAGE
        elif return_code == 6:
            error_message = CORE_PYTHON3_MESSAGE
        elif return_code == 7:
            error_message = CORE_OUTDATED_MESSAGE
        else:
            error_message = EXIT_CODE_UNEXPECTED_MESSAGE.format( code = return_code,
                                                               logfile = logfile )
        error_message = SERVER_SHUTDOWN_MESSAGE + ' ' + error_message
        vimsupport.PostVimMessage(error_message)

    def SendCompletionRequest(self):
        request_data = BuildRequestData()
        self._latest_completion_request = CompletionRequest(request_data)
        self._latest_completion_request.Start()
        
    def GetCompletionResponse(self):
        response = self._latest_completion_request.Response()
        return response

    def GetCurrentCompletionRequest(self):
        return self._latest_completion_request

    def OnVimLeave(self):
        self._ShutdownServer()

    def _ShutdownServer(self):
        SendShutdownRequest()
