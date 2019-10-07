from __future__ import print_function
import sys
import atexit
import os
import json
import argparse
import handlers 
import utils
from server import StoppableWSGIServer

def possibly_detach_from_terminal():
    try:
        os.setsid()
    except OSError:
        pass

def CloseStdin():
    sys.stdin.close()
    os.close( 0 )

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='server hostname')
    parser.add_argument('--port', type=int, default=0,
                        help='server port')
    parser.add_argument('--log', type=int, default=0)
    parser.add_argument('--idle_suicide_seconds', type=int, default=0)
    parser.add_argument('--check_interval_seconds', type=int, default=600)
    parser.add_argument('--options_file', type=str,# required=True,
                        help='JSON file with user options')
    parser.add_argument('--stdout', type=str)
    parser.add_argument('--stderr', type=str)
    return parser.parse_args()

def main():
    args = parse_arguments()
    print("Starting server...")
    if args.stdout is not None:
        sys.stdout = utils.OpenForStdHandle( args.stdout )
    if args.stderr is not None:
        sys.stderr = utils.OpenForStdHandle( args.stderr )

    #possibly_detach_from_terminal()
    from watchdog_plugin import WatchdogPlugin
    # handlers.UpdateUserOptions(options)
    atexit.register(handlers.ServerCleanup)
    handlers.app.install( WatchdogPlugin( args.idle_suicide_seconds,
                                          args.check_interval_seconds ) )
    CloseStdin()
    handlers.wsgi_server = StoppableWSGIServer(handlers.app,
                                               host=args.host,
                                               port=args.port,
                                               threads=30)
    handlers.wsgi_server.Run()

if __name__ == '__main__':
    main()

