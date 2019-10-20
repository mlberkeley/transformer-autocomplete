try:
    import vim
except ImportError:
    print("Vimsupport without vim")
import os
from utils import ToUnicode, ToBytes, GetCurrentDirectory, JoinLinesAsUnicode

NO_COMPLETIONS = {
    'line': -1,
    'column': -1,
    'completion_start_column': -1,
    'completions': []
}

def CurrentLineAndColumn():
    line, column = vim.current.window.cursor
    line -= 1
    return line, column

def CurrentColumn():
    return vim.current.window.cursor[1]

def TextBeforeCursor():
    return ToUnicode(vim.current.line[CurrentColumn():])

def GetUnsavedAndSpecifiedBufferData(included_buffer, included_filepath):
    buffers_data = {included_filepath:GetBufferData(included_buffer)} 

    for buffer_object in vim.buffers:
        if not BufferModified(buffer_object):
            continue
        filepath = GetBufferFilepath(buffer_object)
        if filepath in buffers_data:
            continue
        buffers_data[filepath] = GetBufferData(buffer_object)

    return buffers_data

def BufferModified( buffer_object ):
    return buffer_object.options[ 'mod' ]

def GetBufferData( buffer_object ):
    return {
      # Add a newline to match what gets saved to disk. See #1455 for details.
        'contents': JoinLinesAsUnicode( buffer_object ) + '\n',
        #'filetypes': FiletypesForBuffer( buffer_object )
    }

def GetBufferFilepath( buffer_object ):
    if buffer_object.name:
        return os.path.normpath( ToUnicode( buffer_object.name ) )
      # Buffers that have just been created by a command like :enew don't have any
      # buffer name so we use the buffer number for that.
    return os.path.join( GetCurrentDirectory(), str( buffer_object.number ) )

def GetVimGlobalsKeys():
    return vim.eval('keys( g: )')

def VimExpressionToPythonType(vim_expression):
    """Returns a Python type from the return value of the supplied Vim expression.
    If the expression returns a list, dict or other non-string type, then it is
    returned unmodified. If the string return can be converted to an
    integer, returns an integer, otherwise returns the result converted to a
    Unicode string."""

    result = vim.eval( vim_expression )
    if not ( isinstance( result, str ) or isinstance( result, bytes ) ):
        return result

    try:
        return int( result )
    except ValueError:
        return ToUnicode( result )

def EscapeForVim(text):
    return ToUnicode(text.replace( "'", "''" ))

def PostVimMessage( message, warning = True, truncate = False ):
    """Display a message on the Vim status line. By default, the message is
    highlighted and logged to Vim command-line history (see :h history).
    Unset the |warning| parameter to disable this behavior. Set the |truncate|
    parameter to avoid hit-enter prompts (see :h hit-enter) when the message is
    longer than the window width."""
    echo_command = 'echom' if warning else 'echo'

    # Displaying a new message while previous ones are still on the status line
    # might lead to a hit-enter prompt or the message appearing without a
    # newline so we do a redraw first.
    vim.command( 'redraw' )

    if warning:
        vim.command( 'echohl WarningMsg' )

    message = ToUnicode( message )

    if truncate:
        vim_width = GetIntValue( '&columns' )
        message = message.replace( '\n', ' ' )
        if len( message ) >= vim_width:
            message = message[ : vim_width - 4 ] + '...'

            old_ruler = GetIntValue( '&ruler' )
            old_showcmd = GetIntValue( '&showcmd' )
            vim.command( 'set noruler noshowcmd' )

            vim.command( "{0} '{1}'".format( echo_command,
                             EscapeForVim( message ) ) )

            SetVariableValue( '&ruler', old_ruler )
            SetVariableValue( '&showcmd', old_showcmd )
    else:
        for line in message.split( '\n' ):
          vim.command( "{0} '{1}'".format( echo_command,
                           EscapeForVim( line ) ) )
    if warning:
        vim.command( 'echohl None' )
