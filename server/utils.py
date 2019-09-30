from future.utils import PY2, native
import os
import socket
import threading

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
