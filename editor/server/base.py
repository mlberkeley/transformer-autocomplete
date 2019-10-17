import vimsupport

VAR_PREFIX='gpt_'

def GetUserOptions():
    keys = vimsupport.GetVimGlobalsKeys()
    user_options = {}
    for key in keys:
        if not key.startswith(VAR_PREFIX):
            continue
        new_key = key[len(VAR_PREFIX)]
        new_value = vimsupport.VimExpressionToPythonType('g:'+key)
        user_options[new_key] = new_value
    return user_options
