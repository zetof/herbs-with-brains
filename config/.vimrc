set number
set nowrap
syntax enable
set tabstop=2
set shiftwidth=2
set cursorline
set autowrite
let mapleader = "ù"
nnoremap <Leader>ww :!platformio run --target upload<CR>
nnoremap <Leader>wx :!python boot.py<CR>
