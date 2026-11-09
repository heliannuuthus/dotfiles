# dotfiles

[chezmoi](https://www.chezmoi.io) managed dotfiles，按 **profile** 区分三种环境：

| Profile | 场景 | 典型机器 |
|---------|------|----------|
| `macos` | macOS 桌面 | MacBook + Homebrew + Rio + OrbStack |
| `ubuntu` | Linux 桌面 | Ubuntu/Debian 工作站 + fcitx5 + Rio + 字体 |
| `server` | Debian/Ubuntu 无头服务器 | 远程开发机，精简但完整的 CLI 工具链 |

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
| Rio + 字体 | ✓ | ✓ | — |
| Kitty 兼容配置 + clash-party | ✓ | ✓ | — |
| eza / fzf / neovim / pnpm | ✓ | ✓ | ✓ |
| bat / zoxide / nerdctl | ✓ | ✓ | — |
| asdf + starship + gh | ✓ | ✓ | ✓ |
| kubectl | ✓ | ✓ | — |
| kubecm | ✓ | 可选 | — |
| Rust + hostctl | ✓ | ✓ | ✓ |

### Git / Tools / Neovim

| Target | Description |
|--------|-------------|
| `~/.gitconfig` | name/email + includeIf + gh credential (Linux) |
| `~/.config/starship.toml` | no-runtime-versions preset |
| `~/.config/pip/pip.conf` | 清华 PyPI 镜像 |
| `~/.config/nvim/` | Neovim 配置 |

### 桌面终端：Rio

`macos`、`ubuntu` profile 会安装 Rio，并部署 `~/.config/rio/config.toml` 与 Zsh 提示符标记脚本；`server` 不安装或部署这些桌面终端配置。Rio 存在时，桌面 Shell 设置 `TERMINAL=rio`，不改系统的默认终端关联。原有 Kitty 安装和配置保留作兼容。

配置以 **Rio 0.5.29** 核对，保留 Material Dark 配色、**LXGW WenKai Mono 16pt**、每个分屏 **16px 留白**、1px 分隔线和非当前分屏的柔和调暗：

- macOS 使用 `NativeTab`，标题跟随当前分屏，全屏标题栏显隐由系统控制；Linux 使用 `Tab`，渲染结果不包含 macOS 专属的 `NativeTab`。
- macOS 使用 Apple Color Emoji 和对应 Homebrew 路径的 Neovim；Ubuntu 安装 Noto Color Emoji，并使用 `/usr/bin/nvim`。
- 中文组词背景在此版 Rio 中与光标颜色共用，因此使用可读的灰蓝色；普通选区使用深蓝灰底、浅色字。
- 历史浏览使用 Rio 原生 Vi 模式，提示符跳转由仅在 Rio 中加载的 Zsh hook 提供。Kitty 的自动布局、完整焦点外框和 kittens API 没有原生等价配置；保留的 `kitty-scrollback.nvim` 仅供 Kitty 使用。

macOS 和 Linux 通过 chezmoi 条件生成各自键位，不会把 `Super` 机械替换后造成按键冲突：

| 操作 | macOS | Linux 桌面 |
|------|-------|------------|
| 右分屏 / 下分屏 | ⌘T / ⌘D | Ctrl⇧Enter / Ctrl⇧D |
| 新建标签 | ⌘⇧T | Ctrl⇧T |
| 关闭当前分屏 / 整个标签 | ⌘W / ⌘⇧W | Ctrl⇧W / Ctrl⇧Q |
| 前后标签 / 编号选择 | ⌘⇧[、] / ⌘1…9 | Ctrl⇧[、] / Alt1…9 |
| 前后分屏循环 | ⌘⌥方向键 | CtrlAlt方向键 |
| 调整分屏 | ⌘⌃方向键 | Ctrl⇧方向键 |
| 历史 Vi 浏览 | ⌘G / Ctrl⇧H | Ctrl⇧H |
| 前一条提示符 | Ctrl⇧G | Ctrl⇧G |
| 前 / 后提示符 | ⌘⇧↑ / ⌘⇧↓ | Ctrl⇧AltPageUp / Ctrl⇧AltPageDown |
| 搜索 / URL 提示选择 | ⌘F / ⌘⇧E | Ctrl⇧F / Ctrl⇧E |
| 复制 / 普通粘贴 | ⌘C / ⌘V | Ctrl⇧C / Ctrl⇧V |
| OMP 图片优先备用 | ⌘⇧V 或 CtrlV | Ctrl⇧AltV 或 CtrlV |
| 字号增加 / 减小 / 重置 | ⌘+ / ⌘− / ⌘0 | Ctrl+ / Ctrl− / Ctrl0 |
| 编辑配置 / 全屏 / 命令面板 | ⌘, / ⌘Enter / ⌘⇧Esc | Ctrl⇧F5 / Ctrl⇧F11 / Ctrl⇧Esc |

Vi 浏览可再次按对应快捷键退出。macOS 的字符查看器快捷键不会部署到 Linux；Linux 输入 Unicode 使用桌面或输入法自带功能。

Ubuntu 新安装默认下载官方 **0.5.29** `.deb`，支持 `amd64`、`arm64`，并校验官方 release API 提供的 SHA256 摘要。根据 `WAYLAND_DISPLAY`、`XDG_SESSION_TYPE` 自动选择 Wayland 或 X11 构建；通过 SSH 初始化桌面机器时可显式选择：

```bash
RIO_LINUX_BACKEND=wayland chezmoi apply
# 或 RIO_LINUX_BACKEND=x11
```

新安装也可用 `RIO_VERSION=0.5.29` 指定稳定版版本号。已有 `rio` 不会被强制升级或切换后端；重新运行模板不等于重装已有终端。没有 root / 免密 sudo 权限时明确跳过 `.deb` 安装。脚本检查 `rio` terminfo，缺少时从相同固定版本安装到 `~/.terminfo`。

这些模板按默认 `~/.config` 目录部署，未额外映射自定义 `XDG_CONFIG_HOME` 或 `RIO_CONFIG_HOME`。切换标题栏模式、分屏留白等窗口布局参数后，需要新建 Rio 窗口。

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
├── dot_config/                     # starship, rio, kitty, nvim, gh, pip, ...
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
| `.chezmoiignore` | server 跳过 rio/kitty/clash-party |
| `.chezmoiexternal.toml.tmpl` | server 不下载 kitty-themes |
| `run_onchange_` | 按 profile 安装依赖 |

## 配置验证

需要 chezmoi 和 Python 3.11+；安装了 Zsh 时还会检查生成的 Shell 语法。验证只渲染模板，不执行包安装，也不应用到本机：

```bash
python3 -m unittest discover -s tests -v
```
