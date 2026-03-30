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
| `~/.zshrc` | oh-my-zsh + zsh-autocomplete/autosuggestions/completions/syntax-highlighting/fzf-tab, starship prompt, eza aliases |
| `~/.zshenv` | Cargo env |
| `~/.zprofile` | OrbStack init (macOS only) |
| `~/.vimrc` | 完整 vim 配置：相对行号、智能搜索、缩进、鼠标、系统剪贴板 |

### Git

| Target | Description |
|--------|-------------|
| `~/.gitconfig` | Template — name/email from chezmoi data, includeIf multi-identity, gh credential (Linux) |
| `~/.gitconfig-heliannuuthus` | Personal GitHub identity |

### Tools

| Target | Description |
|--------|-------------|
| `~/.config/starship.toml` | Starship prompt — compact format (symbol only, no version) |
| `~/.config/pip/pip.conf` | 清华大学 PyPI 镜像 (HTTPS) |
| `~/.config/gh/hosts.yml` | GitHub CLI — SSH protocol |
| `~/.config/hostctl/profiles/` | Local hosts profiles |

### Terminal (Kitty)

| Target | Description |
|--------|-------------|
| `~/.config/kitty/kitty.conf` | Kitty 终端配置：Monaspace + LXGW WenKai 字体、分屏快捷键 |
| `~/.config/kitty/theme.conf` | Symlink → kitty-themes/MaterialDark |
| `~/.config/kitty/themes/` | 自定义主题：Catppuccin Mocha、Dracula、Nord |

### Auto-installed Dependencies

**macOS (Homebrew):** chezmoi, eza, fzf, gh, git, glab, go, kubecm, kubectl, mkcert, n, neovim, oath-toolkit, ripgrep, starship, wget + Kitty, OrbStack, Cursor, Google Chrome, Monaspace NF fonts, etc.

**Linux (apt + binary):** git, curl, wget, eza, fzf, ripgrep, bat, fd-find, dust, zoxide, neovim, kitty, starship, gh, kubectl, go, n, pnpm, pyenv + Monaspace Nerd Font, LXGW WenKai

**Cross-platform:** Rust (rustup), hostctl (go install)

## Cross-platform Strategy

| Mechanism | Usage |
|-----------|-------|
| Template conditionals (`{{ .chezmoi.os }}`) | PATH, fcitx5 env, Linux aliases (batcat/fdfind/dust), pyenv, pnpm, gh credential |
| `.chezmoiignore` | Skip `.zprofile` on Linux |
| `.chezmoiexternal.toml` | oh-my-zsh + 5 plugins + kitty-themes auto-downloaded as archives |
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
├── .chezmoiexternal.toml                  # oh-my-zsh + plugins + kitty-themes
├── .chezmoiignore                         # platform-conditional ignores
├── dot_zshrc.tmpl                         # zsh config (templated)
├── dot_zshenv / dot_profile               # cargo env + PATH
├── dot_zprofile.tmpl                      # OrbStack (darwin only)
├── dot_vimrc                              # vim
├── dot_gitconfig.tmpl                     # git config (templated)
├── dot_gitconfig-heliannuuthus            # personal git identity
├── dot_config/
│   ├── starship.toml                      # prompt
│   ├── pip/pip.conf                       # 清华 PyPI 镜像
│   ├── gh/private_hosts.yml               # GitHub CLI
│   ├── hostctl/profiles/test.toml         # local hosts
│   └── kitty/                             # cross-platform
│       ├── kitty.conf                     # terminal config
│       ├── symlink_theme.conf.tmpl        # → kitty-themes/MaterialDark
│       └── themes/                        # custom themes
│           ├── catppuccin-mocha.conf
│           ├── dracula.conf
│           └── nord.conf
└── run_onchange_install-packages.sh.tmpl  # dependency installer
```
