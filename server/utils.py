from future.utils import PY2, native
import os
import socket
import threading
import logging
import tempfile
import datetime

EXECUTABLE_FILE_MASK = os.F_OK | os.X_OK
if PY2:
    from urlparse import urljoin, urlparse
else:
    from urllib.parse import urljoin, urlparse

def ToUnicode(value):
    if not value:
        return str()
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return str(value, 'utf8')
    return str(value)

def ToBytes( value ):
    if not value:
        return bytes()

    if type( value ) == bytes:
        return value

    # This is meant to catch Python 2's native str type.
    if isinstance( value, bytes ):
        return bytes( value, encoding = 'utf8' )

    if isinstance( value, str ):
        if PY2:
            return bytes( value.encode( 'utf8' ), encoding = 'utf8' )
        else:
            return bytes( value, encoding = 'utf8' )

    # This is meant to catch `int` and similar non-string/bytes types.
    return ToBytes(str(value))

def GetCurrentDirectory():
  """Returns the current directory as an unicode object. If the current
  directory does not exist anymore, returns the temporary folder instead."""
  try:
    if PY2:
      return os.getcwdu()
    return os.getcwd()
  except OSError:
    return tempfile.gettempdir()

def GetUnusedLocalhostPort():
    sock = socket.socket()
    # This tells the OS to give us any free port in the range [1024 - 65535]
    sock.bind( ( '', 0 ) )
    port = sock.getsockname()[ 1 ]
    sock.close()
    return port
def FindExecutable( executable ):
      # If we're given a path with a directory part, look it up directly rather
      # than referring to PATH directories. This includes checking relative to the
      # current directory, e.g. ./script
    if os.path.dirname( executable ):
        return GetExecutable( executable )

    paths = os.environ[ 'PATH' ].split( os.pathsep )

    for path in paths:
        exe = GetExecutable( os.path.join( path, executable ) )
        if exe:
            return exe
    return None

def GetExecutable( filename ):
    if ( os.path.isfile( filename )
        and os.access( filename, EXECUTABLE_FILE_MASK ) ):
        return filename
    return None

def StartThread(func, *args):
    thread = threading.Thread(target=func, args=args)
    thread.daemon = True
    thread.start()
    return thread

def CreateLogfile( prefix = '' ):
    with tempfile.NamedTemporaryFile(prefix = prefix,
                                     suffix = '.log',
                                     delete = False ) as logfile:
        return logfile.name

def JoinLinesAsUnicode( lines ):
    try:
        first = next( iter( lines ) )
    except StopIteration:
        return str()
    if isinstance( first, str ):
        return ToUnicode( '\n'.join( lines ) )
    if isinstance( first, bytes ):
        return ToUnicode( b'\n'.join( lines ) )
    raise ValueError( 'lines must contain either strings or bytes.' )

def OpenForStdHandle(filepath):
    # Need to open the file in binary mode on py2 because of bytes vs unicode.
    # If we open in text mode (default), then third-party code that uses `print`
    # (we're replacing sys.stdout!) with an `str` object on py2 will cause
    # tracebacks because text mode insists on unicode objects. (Don't forget,
    # `open` is actually `io.open` because of future builtins.)
    # Since this function is used for logging purposes, we don't want the output
    # to be delayed. This means no buffering for binary mode and line buffering
    # for text mode. See https://docs.python.org/2/library/io.html#io.open
    if PY2:
        return open(filepath, mode = 'wb', buffering = 0)
    return open(filepath, mode = 'w', buffering = 1)

def get_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return ToUnicode(''.join(lines) )

def GetLogFile():
    return './logs/log{}'.format(datetime.datetime.today().isoformat('_')[:-10])

logfile = GetLogFile()
logging.basicConfig(filename=logfile)
LOGGER = logging.getLogger('server')
