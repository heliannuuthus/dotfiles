# dotfiles

[chezmoi](https://www.chezmoi.io) managed dotfiles，按 **profile** 区分三种环境：

| Profile | 场景 | 典型机器 |
|---------|------|----------|
| `macos` | macOS 桌面 | MacBook + Homebrew + Kitty + OrbStack |
| `ubuntu` | Linux 桌面 | Ubuntu/Debian 工作站 + fcitx5 + Kitty + 字体 |
| `server` | Unix 无头服务器 | 远程 dev/CI 机，最小工具链 |

## Quick Start

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply heliannuuthus
```

首次运行会询问 Git name / email；Linux 上还会选择 **ubuntu** 或 **server** profile。macOS 自动设为 `macos`。

### 已有机器切换 profile

编辑 `~/.config/chezmoi/chezmoi.toml`：

```toml
[data]
    profile = "server"   # macos | ubuntu | server
```

然后：

```bash
chezmoi apply
```

## What's Included

### Shell（所有 profile）

| Target | Description |
|--------|-------------|
| `~/.zshrc` | OMZ + zsh-autocomplete/autosuggestions/fzf-tab + starship + asdf |
| `~/.zshenv` | Cargo env + asdf PATH |
| `~/.tool-versions` | asdf 全局版本 (nodejs 22.16.0, python 3.12.12) |
| `~/.zprofile` | OrbStack init（仅 macos） |

### Profile 差异

| 组件 | macos | ubuntu | server |
|------|:-----:|:------:|:------:|
| Homebrew / apt 全量工具 | brew | apt | apt 最小集 |
| fcitx5 / 输入法 | — | ✓ | — |
| Kitty + 字体 + clash-party | ✓ | ✓ | — |
| eza / bat / zoxide / nerdctl | ✓ | ✓ | — |
| asdf + starship + gh + kubectl | ✓ | ✓ | ✓ |
| Rust + hostctl | ✓ | ✓ | ✓ |

### Git / Tools / Neovim

| Target | Description |
|--------|-------------|
| `~/.gitconfig` | name/email + includeIf + gh credential (Linux) |
| `~/.config/starship.toml` | no-runtime-versions preset |
| `~/.config/pip/pip.conf` | 清华 PyPI 镜像 |
| `~/.config/nvim/` | Neovim 配置 |

## 架构

```
.
├── .chezmoi.toml.tmpl              # name, email, profile
├── .chezmoiexternal.toml.tmpl      # OMZ 插件；kitty-themes 仅非 server
├── .chezmoiignore                  # 按 profile 跳过文件
├── .chezmoitemplates/              # 可复用模板片段
│   ├── zsh-*.tmpl                  # PATH / common / extras
│   └── install-*.sh.tmpl           # macos / ubuntu / server / common
├── dot_zshrc.tmpl                  # 组装 zsh 配置
├── dot_zshenv / dot_tool-versions
├── dot_zprofile.tmpl               # macOS OrbStack
├── dot_config/                     # starship, kitty, nvim, gh, pip, ...
└── run_onchange_install-packages.sh.tmpl
```

## Daily Usage

```bash
chezmoi edit ~/.zshrc
chezmoi diff
chezmoi apply
chezmoi update
```

## Cross-platform 机制

| 机制 | 用途 |
|------|------|
| `profile` (chezmoi data) | macos / ubuntu / server 三分 |
| `.chezmoitemplates/` | zsh 与 install 脚本模块化 |
| `.chezmoiignore` | server 跳过 kitty/clash-party |
| `.chezmoiexternal.toml.tmpl` | server 不下载 kitty-themes |
| `run_onchange_` | 按 profile 安装依赖 |
