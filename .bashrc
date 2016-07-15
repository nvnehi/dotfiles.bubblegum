#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls -Glh --color=auto'
export PROMPT_COMMAND='echo -ne "\033]0;urvxt\007"'
export LS_COLORS="di=1;95:ln=95:ex=92:fi=91:"
export PS1="\[\033[38;5;7m\]\w\[$(tput sgr0)\]\[\033[38;5;15m\]\[$(tput sgr0)\]\[\033[38;5;8m\]\\$\[$(tput sgr0)\]\[\033[38;5;15m\] \[$(tput sgr0)\]"
export VISUAL=atom-beta
export EDITOR=vim
