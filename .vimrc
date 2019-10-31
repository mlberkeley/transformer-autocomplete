:set nocompatible
set backspace=indent,eol,start
:let mapleader = ","
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
Plugin 'file:///Users/phil/nvidia/gptplugin'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
set autoindent
set tabstop=4
set softtabstop=4
set shiftwidth=2
set expandtab
colorscheme desert
set ignorecase
set smartcase
nnoremap \yeet :echo "Ye yeeet"<CR>
filetype plugin on
syntax on
"Support <C-j> and <C-k> to swap adjacent lines
function! SwapDown()
    if line('$') > 1
        let pos = getpos('.')
        if pos[1] != getpos('$')[1]
            m +1
            let pos[1] += 1
            call setpos('.', pos)
        endif
    endif
endfunction

function! SwapUp()
    if line('$') > 1
        let pos = getpos('.')
        if pos[1] != 1
            m -2
            let pos[1] -= 1
            call setpos('.', pos)
        endif
    endif
endfunction

nnoremap <silent> <C-j> :call SwapDown()<CR>
nnoremap <silent> <C-k> :call SwapUp()<CR>
inoremap <c-u> <esc>viwUea
iabbrev waht what
iabbrev tehn then
iabbrev slef self 
iabbrev adn and
nnoremap <leader>" viw<esc>a"<esc>bi"<esc>lel
