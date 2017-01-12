set number
set nowrap
syntax enable
set tabstop=2
set shiftwidth=2
set cursorline
command ACU !platformio run --target upload
command PR !python ./%
