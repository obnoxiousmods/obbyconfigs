# Manjaro + Dracula zsh setup.
# Keeps the Manjaro feature set: p10k, autosuggestions, syntax highlighting,
# history substring search, completion caching, title hooks, and keybindings.

USE_POWERLINE="true"
HAS_WIDECHARS="false"

umask 077

export PATH="$HOME/.local/bin:$PATH"
export LS_COLORS="rs=0:di=38;5;146:ln=38;5;182:mh=00:pi=38;5;103:so=38;5;103:do=38;5;103:bd=38;5;174:cd=38;5;174:or=38;5;174:mi=38;5;174:su=38;5;174:sg=38;5;139:ca=38;5;139:tw=38;5;146:ow=38;5;146:st=38;5;103:ex=38;5;182:*.tar=38;5;222:*.tgz=38;5;222:*.arc=38;5;222:*.arj=38;5;222:*.taz=38;5;222:*.lha=38;5;222:*.lz4=38;5;222:*.lzh=38;5;222:*.lzma=38;5;222:*.tlz=38;5;222:*.txz=38;5;222:*.tzo=38;5;222:*.t7z=38;5;222:*.zip=38;5;222:*.z=38;5;222:*.dz=38;5;222:*.gz=38;5;222:*.lrz=38;5;222:*.lz=38;5;222:*.lzo=38;5;222:*.xz=38;5;222:*.zst=38;5;222:*.tzst=38;5;222:*.bz2=38;5;222:*.bz=38;5;222:*.tbz=38;5;222:*.tbz2=38;5;222:*.tz=38;5;222:*.deb=38;5;222:*.rpm=38;5;222:*.jar=38;5;222:*.war=38;5;222:*.ear=38;5;222:*.sar=38;5;222:*.rar=38;5;222:*.alz=38;5;222:*.ace=38;5;222:*.zoo=38;5;222:*.cpio=38;5;222:*.7z=38;5;222:*.rz=38;5;222:*.cab=38;5;222:*.wim=38;5;222:*.swm=38;5;222:*.dwm=38;5;222:*.esd=38;5;222:*.jpg=38;5;183:*.jpeg=38;5;183:*.mjpg=38;5;183:*.mjpeg=38;5;183:*.gif=38;5;183:*.bmp=38;5;183:*.pbm=38;5;183:*.pgm=38;5;183:*.ppm=38;5;183:*.tga=38;5;183:*.xbm=38;5;183:*.xpm=38;5;183:*.tif=38;5;183:*.tiff=38;5;183:*.png=38;5;183:*.svg=38;5;183:*.svgz=38;5;183:*.mng=38;5;183:*.pcx=38;5;183:*.mov=38;5;139:*.mpg=38;5;139:*.mpeg=38;5;139:*.m2v=38;5;139:*.mkv=38;5;139:*.webm=38;5;139:*.ogm=38;5;139:*.mp4=38;5;139:*.m4v=38;5;139:*.mp4v=38;5;139:*.vob=38;5;139:*.qt=38;5;139:*.nuv=38;5;139:*.wmv=38;5;139:*.asf=38;5;139:*.rm=38;5;139:*.rmvb=38;5;139:*.flc=38;5;139:*.avi=38;5;139:*.fli=38;5;139:*.flv=38;5;139:*.gl=38;5;139:*.dl=38;5;139:*.xcf=38;5;139:*.xwd=38;5;139:*.yuv=38;5;139:*.cgm=38;5;139:*.emf=38;5;139:*.ogv=38;5;139:*.ogx=38;5;139:*.aac=38;5;103:*.au=38;5;103:*.flac=38;5;103:*.m4a=38;5;103:*.mid=38;5;103:*.midi=38;5;103:*.mka=38;5;103:*.mp3=38;5;103:*.mpc=38;5;103:*.ogg=38;5;103:*.ra=38;5;103:*.wav=38;5;103:*.oga=38;5;103:*.opus=38;5;103:*.spx=38;5;103:*.xspf=38;5;103:*.ts=38;5;117:*.tsx=38;5;117:*.js=38;5;222:*.jsx=38;5;222:*.json=38;5;183:*.md=38;5;183:*.py=38;5;146:*.rs=38;5;174:*.go=38;5;117"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"

export N_PREFIX="$HOME/n"
[[ :$PATH: == *":$N_PREFIX/bin:"* ]] || PATH+=":$N_PREFIX/bin"

obby_path_prepend() {
  [[ -n "$1" && -d "$1" && ":$PATH:" != *":$1:"* ]] && export PATH="$1:$PATH"
}

obby_path_prepend "$HOME/.local/bin"
obby_path_prepend "$HOME/bin"
obby_path_prepend "$HOME/.cargo/bin"
obby_path_prepend "$HOME/go/bin"
obby_path_prepend "$HOME/.npm-global/bin"
obby_path_prepend "$HOME/.yarn/bin"
obby_path_prepend "$HOME/.bun/bin"
obby_path_prepend "$HOME/.deno/bin"
obby_path_prepend "$HOME/.pyenv/bin"
obby_path_prepend "$HOME/.rye/shims"
obby_path_prepend "$HOME/.local/share/uv/tools"
obby_path_prepend "$HOME/.local/share/pnpm"
obby_path_prepend "$HOME/.config/yarn/global/node_modules/.bin"
obby_path_prepend "$PWD/node_modules/.bin"
[[ -d ".venv/bin" ]] && obby_path_prepend "$PWD/.venv/bin"
[[ -d "venv/bin" ]] && obby_path_prepend "$PWD/venv/bin"

export PNPM_HOME="${PNPM_HOME:-$HOME/.local/share/pnpm}"
export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
export GOPATH="${GOPATH:-$HOME/go}"

[[ $- != *i* ]] && return

if [[ -z "$TMUX" && -z "$NO_AUTO_TMUX" && "${TERM:-}" != "dumb" ]] && command -v tmux >/dev/null 2>&1; then
  if tmux has-session 2>/dev/null; then
    _auto_tmux_target="$(
      tmux list-sessions -F '#{?session_attached,1,0} #{session_activity} #{session_name}' \
        | sort -k1,1nr -k2,2nr \
        | awk 'NR == 1 { print $3 }'
    )"
    exec tmux attach -t "$_auto_tmux_target"
  else
    exec tmux new-session -s "${OBBY_TMUX_SESSION:-main}"
  fi
fi

if [[ -e /usr/share/zsh/manjaro-zsh-config ]]; then
  source /usr/share/zsh/manjaro-zsh-config
fi

if [[ -e /usr/share/zsh/manjaro-zsh-prompt ]]; then
  if [[ -o monitor ]]; then
    source /usr/share/zsh/manjaro-zsh-prompt
  else
    source /usr/share/zsh/manjaro-zsh-prompt 2>/dev/null
  fi
else
  autoload -U compinit colors
  compinit -d
  colors

  [[ -r "__OBBY_P10K_THEME__" ]] && source "__OBBY_P10K_THEME__"
  [[ -r "__OBBY_ZSH_CUSTOM__/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && source "__OBBY_ZSH_CUSTOM__/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"
  [[ -r "__OBBY_ZSH_CUSTOM__/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && source "__OBBY_ZSH_CUSTOM__/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
  [[ -r "__OBBY_ZSH_CUSTOM__/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh" ]] && source "__OBBY_ZSH_CUSTOM__/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh"
  zmodload zsh/terminfo 2>/dev/null || true
  bindkey "$terminfo[kcuu1]" history-substring-search-up 2>/dev/null || true
  bindkey "$terminfo[kcud1]" history-substring-search-down 2>/dev/null || true
  bindkey '^[[A' history-substring-search-up
  bindkey '^[[B' history-substring-search-down
fi

##### Dracula polish ##########################################################

# Muted Dracula/pastel-purple p10k palette using Manjaro's powerline shape.
dracula_p10k() {
  (( $+functions[p10k] )) || return

  typeset -g POWERLEVEL9K_MODE=nerdfont-complete
  typeset -g POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(
    os_icon
    dracula_identity
    dir
    vcs
    prompt_char
  )
  typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    status
    command_execution_time
    background_jobs
    direnv
    virtualenv
    anaconda
    pyenv
    nvm
    nodeenv
    node_version
    package
    kubecontext
    terraform
    aws
    gcloud
    time
  )
  typeset -g POWERLEVEL9K_ICON_PADDING=none
  typeset -g POWERLEVEL9K_PROMPT_ON_NEWLINE=false
  typeset -g POWERLEVEL9K_PROMPT_ADD_NEWLINE=false
  typeset -g POWERLEVEL9K_RPROMPT_ON_NEWLINE=false
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_PREFIX=''
  typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_PREFIX=''
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_SUFFIX=''
  typeset -g POWERLEVEL9K_MULTILINE_LAST_PROMPT_SUFFIX=''
  typeset -g POWERLEVEL9K_LEFT_SEGMENT_SEPARATOR=$'\uE0B0'
  typeset -g POWERLEVEL9K_RIGHT_SEGMENT_SEPARATOR=$'\uE0B2'
  typeset -g POWERLEVEL9K_LEFT_SUBSEGMENT_SEPARATOR=$'\uE0B1'
  typeset -g POWERLEVEL9K_RIGHT_SUBSEGMENT_SEPARATOR=$'\uE0B3'
  typeset -g POWERLEVEL9K_LEFT_PROMPT_LAST_SEGMENT_END_SYMBOL=$'\uE0B0'
  typeset -g POWERLEVEL9K_RIGHT_PROMPT_FIRST_SEGMENT_START_SYMBOL=$'\uE0B2'
  typeset -g POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_CHAR=' '

  typeset -g POWERLEVEL9K_OS_ICON_FOREGROUND=252
  typeset -g POWERLEVEL9K_OS_ICON_BACKGROUND=236
  typeset -g POWERLEVEL9K_OS_ICON_CONTENT_EXPANSION=$'\uF303'
  typeset -g POWERLEVEL9K_DRACULA_IDENTITY_FOREGROUND=252
  typeset -g POWERLEVEL9K_DRACULA_IDENTITY_BACKGROUND=236
  typeset -g POWERLEVEL9K_CONTEXT_FOREGROUND=252
  typeset -g POWERLEVEL9K_CONTEXT_BACKGROUND=236
  typeset -g POWERLEVEL9K_CONTEXT_ROOT_FOREGROUND=236
  typeset -g POWERLEVEL9K_CONTEXT_ROOT_BACKGROUND=174
  typeset -g POWERLEVEL9K_CONTEXT_TEMPLATE='%n'
  typeset -g POWERLEVEL9K_CONTEXT_{REMOTE,REMOTE_SUDO}_TEMPLATE='%n@%m'
  typeset -g POWERLEVEL9K_CONTEXT_{DEFAULT,SUDO}_{CONTENT,VISUAL_IDENTIFIER}_EXPANSION=

  typeset -g POWERLEVEL9K_DIR_FOREGROUND=252
  typeset -g POWERLEVEL9K_DIR_BACKGROUND=61
  typeset -g POWERLEVEL9K_DIR_SHORTENED_FOREGROUND=146
  typeset -g POWERLEVEL9K_DIR_ANCHOR_FOREGROUND=252
  typeset -g POWERLEVEL9K_DIR_ANCHOR_BOLD=true
  typeset -g POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_unique
  typeset -g POWERLEVEL9K_DIR_MAX_LENGTH=56
  typeset -g POWERLEVEL9K_DIR_MIN_COMMAND_COLUMNS=50

  typeset -g POWERLEVEL9K_VCS_CLEAN_FOREGROUND=252
  typeset -g POWERLEVEL9K_VCS_CLEAN_BACKGROUND=103
  typeset -g POWERLEVEL9K_VCS_MODIFIED_FOREGROUND=252
  typeset -g POWERLEVEL9K_VCS_MODIFIED_BACKGROUND=97
  typeset -g POWERLEVEL9K_VCS_UNTRACKED_FOREGROUND=252
  typeset -g POWERLEVEL9K_VCS_UNTRACKED_BACKGROUND=139
  typeset -g POWERLEVEL9K_VCS_CONFLICTED_FOREGROUND=236
  typeset -g POWERLEVEL9K_VCS_CONFLICTED_BACKGROUND=174
  typeset -g POWERLEVEL9K_VCS_LOADING_FOREGROUND=252
  typeset -g POWERLEVEL9K_VCS_LOADING_BACKGROUND=60
  typeset -g POWERLEVEL9K_VCS_BRANCH_ICON=$'\uF126 '

  typeset -g POWERLEVEL9K_STATUS_OK_FOREGROUND=139
  typeset -g POWERLEVEL9K_STATUS_OK_BACKGROUND=236
  typeset -g POWERLEVEL9K_STATUS_ERROR_FOREGROUND=236
  typeset -g POWERLEVEL9K_STATUS_ERROR_BACKGROUND=174
  typeset -g POWERLEVEL9K_STATUS_ERROR_SIGNAL_FOREGROUND=236
  typeset -g POWERLEVEL9K_STATUS_ERROR_SIGNAL_BACKGROUND=174
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND=252
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_BACKGROUND=60
  typeset -g POWERLEVEL9K_COMMAND_EXECUTION_TIME_THRESHOLD=2
  typeset -g POWERLEVEL9K_BACKGROUND_JOBS_FOREGROUND=252
  typeset -g POWERLEVEL9K_BACKGROUND_JOBS_BACKGROUND=61

  typeset -g POWERLEVEL9K_NVM_FOREGROUND=252
  typeset -g POWERLEVEL9K_NVM_BACKGROUND=60
  typeset -g POWERLEVEL9K_NODEENV_FOREGROUND=252
  typeset -g POWERLEVEL9K_NODEENV_BACKGROUND=60
  typeset -g POWERLEVEL9K_NODE_VERSION_FOREGROUND=252
  typeset -g POWERLEVEL9K_NODE_VERSION_BACKGROUND=60
  typeset -g POWERLEVEL9K_PACKAGE_FOREGROUND=252
  typeset -g POWERLEVEL9K_PACKAGE_BACKGROUND=97
  typeset -g POWERLEVEL9K_VIRTUALENV_FOREGROUND=252
  typeset -g POWERLEVEL9K_VIRTUALENV_BACKGROUND=61
  typeset -g POWERLEVEL9K_ANACONDA_FOREGROUND=252
  typeset -g POWERLEVEL9K_ANACONDA_BACKGROUND=61
  typeset -g POWERLEVEL9K_PYENV_FOREGROUND=252
  typeset -g POWERLEVEL9K_PYENV_BACKGROUND=61
  typeset -g POWERLEVEL9K_TIME_FOREGROUND=252
  typeset -g POWERLEVEL9K_TIME_BACKGROUND=61
  typeset -g POWERLEVEL9K_TIME_FORMAT='%D{%H:%M}'

  typeset -g POWERLEVEL9K_PROMPT_CHAR_OK_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND=139
  typeset -g POWERLEVEL9K_PROMPT_CHAR_ERROR_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND=174
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VIINS_CONTENT_EXPANSION='❯'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_{OK,ERROR}_VICMD_CONTENT_EXPANSION='❮'
  typeset -g POWERLEVEL9K_PROMPT_CHAR_BACKGROUND=

  p10k reload
}

prompt_dracula_identity() {
  local label="%n@%m"
  local icon="λ"
  local fg=117

  if [[ -n "$SSH_CONNECTION" || -n "$SSH_CLIENT" || -n "$SSH_TTY" ]]; then
    icon="ssh"
    fg=146
  fi

  if [[ -n "$WSL_DISTRO_NAME" || -n "$WSL_INTEROP" ]] || grep -qi microsoft /proc/version 2>/dev/null; then
    icon="wsl"
    fg=103
  fi

  if [[ "$EUID" == 0 ]]; then
    icon="root"
    fg=174
    if [[ -n "$SUDO_USER" && "$SUDO_USER" != root ]]; then
      label="%n@%m from ${SUDO_USER}"
    fi
  elif [[ -n "$SUDO_USER" && "$SUDO_USER" != "$USER" ]]; then
    icon="sudo"
    fg=139
    label="%n@%m from ${SUDO_USER}"
  fi

  p10k segment -f "$fg" -b "${POWERLEVEL9K_DRACULA_IDENTITY_BACKGROUND:-117}" -i "$icon" -t "$label"
}

dracula_p10k

##### Terminal cursor #########################################################

_dracula_cursor() {
  printf '\e]12;#c4a7e7\a'
}

precmd_functions+=(_dracula_cursor)

##### Syntax colors ###########################################################

# Recolor Manjaro's syntax highlighting from bright red/green to the same
# muted purple family as tmux and p10k.
typeset -A ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[default]='fg=#e8e3f4'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#e78284'
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#c4a7e7,bold'
ZSH_HIGHLIGHT_STYLES[alias]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[global-alias]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[function]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[command]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[precommand]='fg=#9aa5ce'
ZSH_HIGHLIGHT_STYLES[hashed-command]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=#817c9c'
ZSH_HIGHLIGHT_STYLES[path]='fg=#b7bdf8'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg=#817c9c'
ZSH_HIGHLIGHT_STYLES[path_prefix]='fg=#9aa5ce'
ZSH_HIGHLIGHT_STYLES[globbing]='fg=#e5c890'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg=#e5c890'
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#9aa5ce'
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#9aa5ce'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#b7bdf8'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#b7bdf8'
ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=#b7bdf8'
ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]='fg=#c4a7e7'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg=#c4a7e7'

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#817c9c'

##### Fuzzy-ish hotkeys #######################################################

if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
  alias cd='z'
fi

export FZF_DEFAULT_COMMAND="rg --files --hidden --glob '!.git/*' 2>/dev/null"
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_ALT_C_COMMAND="find . -type d -not -path '*/.git/*' 2>/dev/null"
export FZF_DEFAULT_OPTS="--height=45% --layout=reverse --border --prompt='λ ' --pointer='❯' --marker='✓' --color=bg+:#36364d,bg:#20202d,spinner:#c4a7e7,hl:#a78bfa,fg:#e8e3f4,header:#817c9c,info:#9aa5ce,pointer:#c4a7e7,marker:#b7bdf8,fg+:#e8e3f4,prompt:#c4a7e7,hl+:#c4a7e7"

if command -v fzf >/dev/null 2>&1; then
  [[ -f /usr/share/fzf/key-bindings.zsh ]] && source /usr/share/fzf/key-bindings.zsh
  [[ -f /usr/share/fzf/completion.zsh ]] && source /usr/share/fzf/completion.zsh

  _dracula_fzf_file() {
    emulate -L zsh
    local file
    file="$(eval "$FZF_DEFAULT_COMMAND" | fzf --preview 'sed -n "1,120p" {} 2>/dev/null' --preview-window='right:55%:wrap')" || return
    LBUFFER+="${(q)file}"
    zle redisplay
  }
  zle -N _dracula_fzf_file
  bindkey '^P' _dracula_fzf_file

  _dracula_fzf_cd() {
    emulate -L zsh
    local dir
    dir="$(find . -type d -not -path '*/.git/*' 2>/dev/null | fzf)" || return
    cd -- "$dir"
    zle reset-prompt
  }
  zle -N _dracula_fzf_cd
  bindkey '^G' _dracula_fzf_cd
elif command -v zoxide >/dev/null 2>&1; then
  _dracula_zoxide_cd() {
    emulate -L zsh
    local query dir
    zle -I
    print -n "zoxide query> "
    read -r query
    dir="$(zoxide query -- "$query" 2>/dev/null)" || return
    cd -- "$dir"
    zle reset-prompt
  }
  zle -N _dracula_zoxide_cd
  bindkey '^G' _dracula_zoxide_cd
fi

##### Local convenience #######################################################

if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons=auto --group-directories-first'
  alias ll='eza -lah --icons=auto --group-directories-first --git'
  alias la='eza -la --icons=auto --group-directories-first --git'
  alias tree='eza --tree --icons=auto --group-directories-first'
elif command -v exa >/dev/null 2>&1; then
  alias ls='exa --icons --group-directories-first'
  alias ll='exa -lah --icons --group-directories-first --git'
  alias la='exa -la --icons --group-directories-first --git'
else
  alias ls='ls --color=auto'
  alias ll='ls -lah --color=auto'
  alias la='ls -A --color=auto'
fi
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias c='clear'
alias t='tmux'
alias ta='tmux attach -t'
alias tl='tmux list-sessions'
alias tn='tmux new -s'

mkcd() {
  mkdir -p -- "$1" && cd -- "$1"
}

take() {
  mkcd "$@"
}
