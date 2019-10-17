try:
    import vim
except ImportError:
    print("paths without vim")

def PathToPythonInterpreter():
    import utils

    return "//anaconda3/bin/python3.7"
    python_interpreter = vim.eval( 'g:gpt_server_python_interpreter' )
    print("Interpreter value is: {}".format(python_interpreter))
    if python_interpreter:
        python_interpreter = utils.FindExecutable( python_interpreter )
        if python_interpreter:
            return python_interpreter

        raise RuntimeError( "Path in 'g:gpt_server_python_interpreter' option "
            "does not point to a valid Python 2.7 or 3.5+." )

