"""Render desktop/server profiles without applying dotfiles or installing packages.

Run with: python3 -m unittest discover -s tests -p test_rio.py -v
Requires Python 3.11+ and chezmoi; shell syntax checks use bash and zsh when present.
"""

from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
DESKTOPS = (
    ("macos", "darwin", "arm64"),
    ("macos", "darwin", "amd64"),
    ("ubuntu", "linux", "amd64"),
    ("ubuntu", "linux", "arm64"),
)
PROFILES = DESKTOPS + (("server", "linux", "amd64"),)


def binding_key(binding):
    aliases = {"command": "super", "cmd": "super", "option": "alt", "ctrl": "control"}
    mods = frozenset(
        aliases.get(part.strip().lower(), part.strip().lower())
        for part in binding.get("with", "").split("|")
        if part.strip()
    )
    key = binding["key"].lower()
    key = {"return": "enter", "back": "backspace", "esc": "escape"}.get(key, key)
    modes = frozenset(part.strip().lower() for part in binding.get("mode", "").split("|") if part.strip())
    return key, mods, modes


def luminance(color):
    values = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in values]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    low, high = sorted((luminance(first), luminance(second)))
    return (high + 0.05) / (low + 0.05)


class RioTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chezmoi = shutil.which("chezmoi")
        if cls.chezmoi is None:
            raise unittest.SkipTest("chezmoi is required to render the profile matrix")
        cls.scratch = tempfile.TemporaryDirectory(prefix="dotfiles-rio-tests-")
        cls.addClassCleanup(cls.scratch.cleanup)

    @classmethod
    @lru_cache(maxsize=None)
    def render(cls, relative_path, profile, platform, architecture):
        scratch = Path(cls.scratch.name)
        data = {
            "profile": profile,
            "name": "Template Test",
            "email": "template@example.invalid",
            "clash_party_proxy_group": "test",
            "chezmoi": {"os": platform, "arch": architecture},
        }
        command = [
            cls.chezmoi,
            "--config", os.devnull,
            "--config-format", "toml",
            "--source", str(ROOT),
            "--destination", str(scratch / "home"),
            "--cache", str(scratch / "cache"),
            "--persistent-state", str(scratch / "state.boltdb"),
            "--no-tty",
            "--refresh-externals=never",
            "--override-data", json.dumps(data),
            "execute-template", "--file", str(ROOT / relative_path),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=30)
        if result.returncode:
            raise AssertionError(f"Cannot render {relative_path} for {profile}/{architecture}:\n{result.stderr}")
        return result.stdout

    def config(self, case):
        return tomllib.loads(self.render("dot_config/rio/config.toml.tmpl", *case))

    def test_platform_specific_configuration(self):
        for case in DESKTOPS:
            profile, _, architecture = case
            with self.subTest(profile=profile, architecture=architecture):
                rendered = self.render("dot_config/rio/config.toml.tmpl", *case)
                config = tomllib.loads(rendered)
                self.assertTrue(config["navigation"]["use-split"])
                self.assertEqual(config["fonts"]["family"], "LXGW WenKai Mono")
                self.assertEqual(config["panel"]["margin"], [16])
                self.assertTrue(0.15 <= config["navigation"]["unfocused-split-opacity"] <= 1)
                self.assertIn("TITLE", config["title"]["content"])
                mapped_fonts = {mapping["font-family"] for mapping in config["fonts"]["symbol-map"]}
                if profile == "macos":
                    self.assertEqual(config["navigation"]["mode"], "NativeTab")
                    self.assertIn("Apple Color Emoji", mapped_fonts)
                    prefix = "/opt/homebrew" if architecture == "arm64" else "/usr/local"
                    self.assertEqual(config["editor"]["program"], prefix + "/bin/nvim")
                else:
                    self.assertEqual(config["navigation"]["mode"], "Tab")
                    self.assertIn("Noto Color Emoji", mapped_fonts)
                    self.assertEqual(config["editor"]["program"], "/usr/bin/nvim")
                    for mac_only_value in ("NativeTab", "Apple Color Emoji", "CharacterPalette", "/opt/homebrew", "/usr/local/bin/nvim"):
                        self.assertNotIn(mac_only_value, rendered)

    def test_custom_bindings_do_not_collide(self):
        for case in DESKTOPS:
            with self.subTest(profile=case[0], architecture=case[2]):
                bindings = self.config(case)["bindings"]["keys"]
                keys = [binding_key(binding) for binding in bindings]
                self.assertEqual(len(keys), len(set(keys)), "duplicate custom key/modifier/mode mapping")
                self.assertTrue(all(bool(binding.get("action")) != bool(binding.get("esc")) for binding in bindings))
                if case[0] != "macos":
                    self.assertTrue(all("super" not in key[1] for key in keys), "Linux keys should not depend on desktop-reserved Super chords")

    def test_split_tab_and_paste_chords_remain_distinct(self):
        for case in DESKTOPS:
            with self.subTest(profile=case[0], architecture=case[2]):
                bindings = {binding_key(binding): binding for binding in self.config(case)["bindings"]["keys"]}

                def get(key, modifiers):
                    return bindings[(key, frozenset(modifiers), frozenset())]

                if case[0] == "macos":
                    self.assertEqual(get("t", ("super",))["action"], "SplitRight")
                    self.assertEqual(get("d", ("super",))["action"], "SplitDown")
                    self.assertEqual(get("t", ("super", "shift"))["action"], "CreateTab")
                    self.assertEqual(get("v", ("super",))["action"], "Paste")
                    self.assertEqual(get("v", ("super", "shift"))["esc"], "\x16")
                else:
                    self.assertEqual(get("enter", ("control", "shift"))["action"], "SplitRight")
                    self.assertEqual(get("d", ("control", "shift"))["action"], "SplitDown")
                    self.assertEqual(get("t", ("control", "shift"))["action"], "CreateTab")
                    self.assertEqual(get("v", ("control", "shift"))["action"], "Paste")
                    self.assertEqual(get("v", ("control", "shift", "alt"))["esc"], "\x16")

    def test_input_and_selection_colors_stay_readable(self):
        for case in DESKTOPS:
            with self.subTest(profile=case[0], architecture=case[2]):
                colors = self.config(case)["colors"]
                # Rio 0.5.29 uses the cursor color as the IME preedit background,
                # and the terminal background as its text color.
                self.assertGreaterEqual(contrast(colors["cursor"], colors["background"]), 4.5)
                self.assertLess(luminance(colors["cursor"]), 0.6, "IME must not return to the glaring white highlight")
                self.assertGreaterEqual(contrast(colors["selection-foreground"], colors["selection-background"]), 4.5)
                self.assertLess(luminance(colors["selection-background"]), 0.2)

    def test_repository_tests_are_never_deployed(self):
        for case in PROFILES:
            with self.subTest(profile=case[0], architecture=case[2]):
                ignored = self.render(".chezmoiignore", *case)
                patterns = {
                    line.strip()
                    for line in ignored.splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                }
                self.assertIn("tests/", patterns)

    def test_server_excludes_rio_and_desktop_shell_integration(self):
        server = ("server", "linux", "amd64")
        ignored = self.render(".chezmoiignore", *server)
        patterns = {line.strip() for line in ignored.splitlines() if line.strip() and not line.lstrip().startswith("#")}
        self.assertIn(".config/rio/", patterns)
        for case in DESKTOPS:
            self.assertNotIn(".config/rio/", self.render(".chezmoiignore", *case).splitlines())
            self.assertIn("rio/zsh-integration.zsh", self.render("dot_zshrc.tmpl", *case))
        self.assertNotIn("rio/zsh-integration.zsh", self.render("dot_zshrc.tmpl", *server))
        installer = self.render("run_onchange_install-packages.sh.tmpl", *server).lower()
        for desktop_dependency in ("rioterm_", "installing rio", "rio_linux_backend", "font-lxgw-wenkai", "fonts-noto-color-emoji"):
            self.assertNotIn(desktop_dependency, installer)

    def test_rendered_installers_are_valid_bash(self):
        bash = shutil.which("bash")
        if bash is None:
            self.skipTest("bash is unavailable; installer syntax was not checked")
        for case in PROFILES:
            with self.subTest(profile=case[0], architecture=case[2]):
                result = subprocess.run([bash, "-n"], input=self.render("run_onchange_install-packages.sh.tmpl", *case), text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_rendered_shells_are_valid_zsh(self):
        zsh = shutil.which("zsh")
        if zsh is None:
            self.skipTest("zsh is unavailable; shell syntax was not checked")
        for case in PROFILES:
            with self.subTest(profile=case[0], architecture=case[2]):
                result = subprocess.run([zsh, "-n"], input=self.render("dot_zshrc.tmpl", *case), text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([zsh, "-n", str(ROOT / "dot_config/rio/zsh-integration.zsh")], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_prompt_marks_only_activate_in_interactive_rio(self):
        zsh = shutil.which("zsh")
        if zsh is None:
            self.skipTest("zsh is unavailable; Rio prompt-mark behavior was not checked")
        hook = str(ROOT / "dot_config/rio/zsh-integration.zsh")
        script = 'source "$1"; source "$1"; for hook_fn in $precmd_functions; do "$hook_fn"; done'
        for interactive, terminal, expected in ((True, "rio", b"\x1b]133;A\x07"), (True, "kitty", b""), (False, "rio", b"")):
            with self.subTest(interactive=interactive, terminal=terminal):
                environment = os.environ.copy()
                environment["TERM_PROGRAM"] = terminal
                flags = "-fic" if interactive else "-fc"
                result = subprocess.run([zsh, flags, script, "--", hook], env=environment, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                self.assertEqual(result.stdout, expected, "prompt marks must be Rio-only and must not duplicate on repeated source")


if __name__ == "__main__":
    unittest.main()
