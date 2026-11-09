# OSC 133 command marks for Rio's native previous/next-prompt navigation.
# Rio's built-in integration already supplies OSC 7 working-directory updates.
[[ -o interactive && ${TERM_PROGRAM-} == rio ]] || return 0
(( ${+_RIO_COMMAND_MARKS_LOADED} )) && return 0
typeset -g _RIO_COMMAND_MARKS_LOADED=1

autoload -Uz add-zsh-hook

_rio_mark_prompt() {
  printf '\e]133;A\a'
}

add-zsh-hook precmd _rio_mark_prompt
