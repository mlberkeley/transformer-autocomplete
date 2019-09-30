from __future__ import print_function
import sys
import atexit
import os
import json
import argparse
import handlers 
from server import StoppableWSGIServer

def possibly_detach_from_terminal():
    try:
        os.setsid()
    except OSError:
        pass

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='server hostname')
    parser.add_argument('--port', type=int, default=0,
                        help='server port')
    parser.add_argument('--log', type=int, default=0)
    parser.add_argument('--idle_suicide_seconds', type=int, default=0)
    parser.add_argument('--options_file', type=str, required=True,
                        help='JSON file with user options')
    return parser.parse_args()

def main():
    args = parse_arguments()
    print("Starting server...")
    #possibly_detach_from_terminal()
    from watchdog_plugin import WatchdogPlugin
    # handlers.UpdateUserOptions(options)
    atexit.register(handlers.ServerCleanup)
    handlers.wsgi_server = StoppableWSGIServer(handlers.app,
                                               host=args.host,
                                               port=args.port,
                                               threads=30)
    handlers.wsgi_server.Run()

if __name__ == '__main__':
    main()

