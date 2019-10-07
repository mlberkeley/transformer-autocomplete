from base_request import BaseRequest, BuildRequestData
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
import time
import vimsupport
from pprint import pprint
from keep_alive import Keepalive

SERVER_IDLE_SUICIDE_SECONDS=1800
SERVER_SHUTDOWN_MESSAGE = (
    "The server SHUT DOWN." )
EXIT_CODE_UNEXPECTED_MESSAGE = (
    "Unexpected exit code {code}. "
    "Type ':YcmToggleLogs {logfile}' to check the logs." )
CORE_PYTHON2_MESSAGE = (
    "Server library compiled for Python 2 but loaded in Python 3. "
    "Set the 'g:gpt_server_python_interpreter' option to a Python 2 "
    "interpreter path." )
CORE_PYTHON3_MESSAGE = (
    "Server library compiled for Python 3 but loaded in Python 2. "
    "Set the 'g:gpt_server_python_interpreter' option to a Python 3 "
    "interpreter path." )
CLIENT_LOGFILE_FORMAT = 'gpt_'
SERVER_LOGFILE_FORMAT = 'gpt_{port}_{std}_'

class Completer(object):
    def __init__(self, vim=True):
        self._buffers = None
        self.vim = vim
        self._latest_completion_request = None
        self._keepalive = Keepalive()
        self._keepalive.Start()
        self._server_stdout = None
        self._server_stderr = None
        self._server_popen = None
        self._logger = logging.getLogger('gpt')
        self._logger.setLevel(10)
        self._SetUpServer()
        self._SetUpLogging()

    def _SetUpServer(self):
        if self.vim:
            self._user_options = base.GetUserOptions()
        else:
            self._user_options = {}
        self._user_options['log_level'] = 0
        options_dict = dict(self._user_options)
        pprint(options_dict)
        server_port = utils.GetUnusedLocalhostPort()
        BaseRequest.server_location = 'http://127.0.0.1:' + str(server_port)
        print(BaseRequest.server_location)
        with NamedTemporaryFile(delete=False, mode='w+') as options_file:
            json.dump(options_dict, options_file)
        try:
            python_interpreter = paths.PathToPythonInterpreter()
        except RuntimeError as error:
            error_message = (
            "Unable to start the ycmd server. {0}. "
            "Correct the error then restart the server "
            "with ':YcmRestartServer'.".format( str( error ).rstrip( '.' ) ) )
            self._logger.exception(error_message)
            #vimsupport.PostVimMessage( error_message )
            return

        print(server_port)
        print(os.path.join(os.getcwd(), 'main.py'))
        args = [python_interpreter,
            os.path.join(os.getcwd(), 'main.py'), # server script path
            '--port={0}'.format(server_port),
            '--options_file={0}'.format(options_file.name),
            '--log={0}'.format(self._user_options['log_level']),
            '--idle_suicide_seconds={0}'.format(SERVER_IDLE_SUICIDE_SECONDS)]
        self._server_stdout = utils.logfile
        self._server_stderr = utils.logfile
        args.append('--stdout={0}'.format(self._server_stdout))
        args.append('--stderr={0}'.format(self._server_stderr))
        #TODO: add logging    
        #log = open("./erroroutput", "w")
        self._server_popen = Popen(args, stdout=PIPE, stderr=PIPE)#, stdout=PIPE, stderr=PIPE)

    def _SetUpLogging(self):
        self._client_logfile = utils.logfile
        with open("./logs.txt", "a") as f:
            f.write("{}\n".format(self._client_logfile))
        handler = logging.FileHandler(self._client_logfile)
        formatter = logging.Formatter( '%(asctime)s - %(levelname)s - %(message)s' )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.info('Logger setup\n')

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
        self._logger.error(error_message)
        error_message = SERVER_SHUTDOWN_MESSAGE + ' ' + error_message
        #vimsupport.PostVimMessage(error_message)

    def SendCompletionRequest(self):
        request_data = BuildRequestData()
        self._latest_completion_request = CompletionRequest(request_data)
        self._latest_completion_request.Start()
        
    def GetCompletionResponse(self):
        response = self._latest_completion_request.Response()
        self._logger.info(response)
        return response

    def GetCurrentCompletionRequest(self):
        return self._latest_completion_request

    def CompletionRequestReady(self):
        return bool( self._latest_completion_request and
                         self._latest_completion_request.Done() )

    def OnVimLeave(self):
        self._logger.info('Vim Leave')
        self._ShutdownServer()

    def _ShutdownServer(self):
        #self._server_popen.communicate()
        self._logger.info('sending shutdown request')
        SendShutdownRequest(BaseRequest.server_location)

if __name__ == '__main__':
    #boutta test this shit
    state = Completer(vim=False)
    state.SendCompletionRequest()
    for i in range(10):
        time.sleep(0.3)
        if state.CompletionRequestReady():
            resp = state.GetCompletionResponse()
            print(resp)
    
    time.sleep(3)
    print("Leaving!")
    state.OnVimLeave()

