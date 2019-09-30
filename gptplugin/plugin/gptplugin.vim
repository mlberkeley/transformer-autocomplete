
let s:completion = {}
let s:script_folder_path = escape( expand( '<sfile>:p:h' ), '\' )
let g:gpt_server_python_interpreter = '//anaconda/bin/python3.7'
let s:pollers = {
      \   'completion': {
      \     'id': -1,
      \     'wait_milliseconds': 10
      \   },
      \   'file_parse_response': {
      \     'id': -1,
      \     'wait_milliseconds': 100
      \   },
      \   'server_ready': {
      \     'id': -1,
      \     'wait_milliseconds': 100
      \   },
      \   'receive_messages': {
      \     'id': -1,
      \     'wait_milliseconds': 100
      \   }
      \ }

function! s:UsingPython3()
  if has('python3')
    return 1
  endif
  return 0
endfunction
let s:using_python3 = s:UsingPython3()
let s:python_until_eof = s:using_python3 ? "python3 << EOF" : "python << EOF"
let s:python_command = s:using_python3 ? "py3 " : "py "

function! s:SetUpPython()
    exec s:python_until_eof
from __future__ import print_function
import os.path as p
import re
import sys
import traceback
import vim

print("Hello from python version {}.{} with executable {}".format(sys.version_info[0], sys.version_info[1], sys.executable))
root_folder = p.normpath( p.join( vim.eval( 's:script_folder_path' ), '..' ) )
print("Root folder {}".format(root_folder))
dependencies = [p.normpath(p.join(root_folder, '../server')),
                '//anaconda3/lib/python3.7', '/Users/phil/.local/lib/python3.7/site-packages',
                '//anaconda3/lib/python3.7/site-packages']
#if sys.version_info[0] == 2:
#    dependencies.append(p.join('pythonfutures'))

for d in dependencies:
	sys.path.append(d)
try:
    import base, vimsupport, completion
    gpt_state = completion.Completer()
except Exception as error:
    for line in traceback.format_exc().splitlines():
        vim.command( "echom '{0}'".format( line.replace( "'", "''" ) ) )

        vim.command( "echo 'YouCompleteMe unavailable: {0}'"
                     .format( str( error ).replace( "'", "''" ) ) )
        vim.command( 'echohl None' )
        vim.command( 'return 0' )
else:
	vim.command('return 1')

EOF
endfunction

function! s:Enable()
	echom "Hello"
	let s:status = s:SetUpPython()
	if !s:status
		return
	endif
	call s:SetCompleteFunc()
	call s:SetUpCompleteopt()
	augroup completion
		autocmd!
		autocmd VimLeave * call s:OnVimLeave()
	augroup END
	let s:default_completion = s:Pyeval('vimsupport.NO_COMPLETIONS')
	let s:completion = s:default_completion
endfunction

function! s:Pyeval(eval_string)
	if s:using_python3
		return py3eval(a:eval_string)
	endif
	return pyeval(a:eval_string)
endfunction

function! s:SetCompleteFunc()
	let &completefunc='gptplugin#CompleteFunc'
endfunction

function! gptplugin#CompleteFunc( findstart, base )
  if a:findstart
    if s:completion.line != line( '.' )
      let s:completion.completion_start_column +=
            \ col( '.' ) - s:completion.column
    endif
    return s:completion.completion_start_column - 1
  endif
  return s:completion.completions
endfunction

function! s:OnVimLeave()
	for poller in values(s:pollers)
		call timer_stop(poller.id)
	endfor
	exec s:python_command "gpt_state.OnVimLeave()"
endfunction

function! s:SetUpCompleteopt()
	set completeopt-=menu
	set completeopt+=menuone
	set completeopt-=longest
endfunction

function! s:DoCompletion()
	if s:completion_stopped
		let s:completion_stopped = 0
		let s:completion = s:default_completion
		return
	endif
	call s:Complete()
	call s:RequestCompletion()
endfunction


function! s:RequestCompletion()
	exec s:python_command "gpt_state.SendCompletionRequest()"
	call s:PollCompletion()
endfunction

function! s:StopCompletion(key)
	call timer_stop(s:pollers.completion.id)
	if pumvisible()
		let s:completion_stopped = 1
		return "\<C-y>"
	endif
	return a:key
endfunction

function! s:PollCompletion(...)
	if !s:Pyeval('gpt_state.CompletionRequestReady()')
		let s:pollers.completion.id = timer_start(
			\ s:poller.completion.wait_milliseconds,
			\ function('s:PollCompletion'))
		return
	endif
	let s:completion = s:Pyeval('gpt_state.GetCompletionResponse()')
	call s:Complete()
endfunction

function! s:Complete()
	if s:completion.completion_start_column > s:completion.column ||
		\ empty(s:completion.completions)
		call s:CloseCompletionMenu()
	else
		call s:SendKeys("\<C-X>\<C-U>\<C-P>")
	endif
endfunction

function! s:CloseCompletionMenu()
	if pumvisible()
		call s:SendKeys("\C-e>")
	endif
endfunction

function! s:SendKeys(keys)
	call feedkeys(a:keys, 'in')
endfunction
	
inoremap <silent> <C-g> :call DoCompletion()<CR>
call s:Enable()
