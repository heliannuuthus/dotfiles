# dotfiles

[chezmoi](https://www.chezmoi.io) managed dotfiles for macOS & Linux.

## Quick Start

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply heliannuuthus
```

首次运行会交互式询问 Git name 和 email，随后自动完成：

1. 安装系统依赖（Homebrew / apt）
2. 下载 oh-my-zsh 及插件
3. 部署所有配置文件

## What's Included

### Shell

| Target | Description |
|--------|-------------|
| `~/.zshrc` | oh-my-zsh + zsh-autocomplete/autosuggestions/syntax-highlighting/fzf-tab, starship prompt, eza aliases |
| `~/.zshenv` | Cargo env |
| `~/.zprofile` | OrbStack init (macOS only) |
| `~/.vimrc` | Syntax highlighting + desert colorscheme |

### Git

| Target | Description |
|--------|-------------|
| `~/.gitconfig` | Template — name/email from chezmoi data, includeIf multi-identity |
| `~/.gitconfig-heliannuuthus` | Personal GitHub identity |

### Tools

| Target | Description |
|--------|-------------|
| `~/.config/starship.toml` | Starship prompt — compact format (symbol only, no version) |
| `~/.config/pip/pip.conf` | Aliyun mirror |
| `~/.config/gh/hosts.yml` | GitHub CLI — SSH protocol |
| `~/.config/hostctl/profiles/` | Local hosts profiles |

### macOS Only

| Target | Description |
|--------|-------------|
| `~/.config/iterm2/Geek-Black-Green.itermcolors` | iTerm2 color scheme |

### Auto-installed Dependencies

**macOS (Homebrew):** chezmoi, eza, fzf, gh, git, glab, go, kubecm, kubectl, mkcert, n, neovim, oath-toolkit, ripgrep, starship, wget + iTerm2, OrbStack, Cursor, Google Chrome, Monaspace NF fonts, etc.

**Linux (apt):** git, curl, wget, eza, fzf, ripgrep, neovim, starship, gh, kubectl, go, n + Monaspace Nerd Font

**Cross-platform:** Rust (rustup), hostctl (go install)

## Cross-platform Strategy

| Mechanism | Usage |
|-----------|-------|
| Template conditionals (`{{ .chezmoi.os }}`) | PATH differences in `.zshrc`, OrbStack blocks in `.zprofile` / `.ssh/config` |
| `.chezmoiignore` | Skip iTerm2 config and `.zprofile` on Linux |
| `.chezmoiexternal.toml` | oh-my-zsh + 4 plugins auto-downloaded as archives |
| `run_onchange_` script | Platform-specific package installation |

## Daily Usage

```bash
chezmoi edit ~/.zshrc        # edit in source dir
chezmoi diff                 # preview changes
chezmoi apply                # apply to home

chezmoi cd                   # cd to source dir
git add -A && git commit -m "update" && git push

chezmoi update               # pull + apply on another machine
```

## Structure

```
.
├── .chezmoi.toml.tmpl                     # interactive init config (name, email)
├── .chezmoiexternal.toml                  # oh-my-zsh + plugins
├── .chezmoiignore                         # platform-conditional ignores
├── dot_zshrc.tmpl                         # zsh config (templated)
├── dot_zshenv / dot_profile               # cargo env
├── dot_zprofile.tmpl                      # OrbStack (darwin only)
├── dot_vimrc                              # vim
├── dot_gitconfig.tmpl                     # git config (templated)
├── dot_gitconfig-heliannuuthus            # personal git identity
├── dot_config/
│   ├── starship.toml                      # prompt
│   ├── pip/pip.conf                       # mirror
│   ├── gh/private_hosts.yml               # GitHub CLI
│   ├── hostctl/profiles/test.toml         # local hosts
│   └── iterm2/                            # macOS only
│       └── Geek-Black-Green.itermcolors   # color scheme
└── run_onchange_install-packages.sh.tmpl  # dependency installer
```
