#!/bin/sh
# BanglaThon Universal 1-Click macOS & Linux Standalone Installer / Updater
# Usage: curl -fsSL https://raw.githubusercontent.com/tasfiqueofficial/BanglaThon/main/install.sh | sh

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

printf "\n"
printf "${GREEN}==========================================================${NC}\n"
printf "${CYAN}   বাংলাথন (BanglaThon) — macOS / Linux ইনস্টলার ও আপডেটার${NC}\n"
printf "${YELLOW}   (এক কমান্ডেই সম্পূর্ণ সেটআপ ও সর্বশেষ বাংলা সিনট্যাক্স!)     ${NC}\n"
printf "${GREEN}==========================================================${NC}\n\n"

INSTALL_DIR="$HOME/.bangla"
RUNTIME_DIR="$INSTALL_DIR/runtime"
BIN_DIR="$INSTALL_DIR/bin"
LOCAL_BIN="$HOME/.local/bin"

mkdir -p "$RUNTIME_DIR" "$BIN_DIR" "$LOCAL_BIN"

# 1. Detect a working Python 3.7+ without triggering macOS Xcode CLT dialog
is_usable_python() {
    cand="$1"
    [ -n "$cand" ] && [ -x "$cand" ] || return 1
    # Avoid /usr/bin/python3 stub on macOS when Xcode Command Line Tools are not installed
    if [ "$cand" = "/usr/bin/python3" ] && [ "$(uname -s)" = "Darwin" ]; then
        xcode-select -p >/dev/null 2>&1 || return 1
    fi
    "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)' >/dev/null 2>&1
}

PY_EXE=""
if is_usable_python "$INSTALL_DIR/py/bin/python3"; then
    PY_EXE="$INSTALL_DIR/py/bin/python3"
else
    for cand in \
        "/opt/homebrew/bin/python3" \
        "/usr/local/bin/python3" \
        "/Library/Frameworks/Python.framework/Versions/Current/bin/python3" \
        /Library/Frameworks/Python.framework/Versions/3.*/bin/python3 \
        "$(command -v python3 2>/dev/null || true)"; do
        if is_usable_python "$cand"; then
            PY_EXE="$cand"
            break
        fi
    done
fi

# Download portable standalone Python (~25MB) if none found
if [ -z "$PY_EXE" ]; then
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    PY_REL="20261110"
    PY_VER="3.12.16%2B20261110"

    if [ "$OS" = "Darwin" ] && [ "$ARCH" = "arm64" ]; then
        TARGET="aarch64-apple-darwin"
    elif [ "$OS" = "Darwin" ] && [ "$ARCH" = "x86_64" ]; then
        TARGET="x86_64-apple-darwin"
    elif [ "$OS" = "Linux" ] && [ "$ARCH" = "x86_64" ]; then
        TARGET="x86_64-unknown-linux-gnu"
    elif [ "$OS" = "Linux" ] && { [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; }; then
        TARGET="aarch64-unknown-linux-gnu"
    else
        printf "${RED}[!] আপনার সিস্টেম (%s %s)-এর জন্য Python 3.7+ পাওয়া যায়নি। অনুগ্রহ করে Python 3 ইনস্টল করুন।${NC}\n" "$OS" "$ARCH"
        exit 1
    fi

    printf "${CYAN}[+] পোর্টেবল ইঞ্জিন ডাউনলোড হচ্ছে (~২৫ MB)...${NC}\n"
    PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PY_REL}/cpython-${PY_VER}-${TARGET}-install_only_stripped.tar.gz"
    TMPDIR_BASE="${TMPDIR:-/tmp}"
    TMP_PY="$(mktemp "${TMPDIR_BASE%/}/bangla_py.XXXXXX")"
    curl -fsSL "$PY_URL" -o "$TMP_PY"
    rm -rf "$INSTALL_DIR/py"
    mkdir -p "$INSTALL_DIR/py"
    tar -xzf "$TMP_PY" -C "$INSTALL_DIR/py" --strip-components=1
    rm -f "$TMP_PY"
    PY_EXE="$INSTALL_DIR/py/bin/python3"
fi

# 2. Download & unpack latest BanglaThon core files
printf "${CYAN}[+] সর্বশেষ BanglaThon ইঞ্জিন ডাউনলোড ও আপডেট হচ্ছে...${NC}\n"
TMPDIR_BASE="${TMPDIR:-/tmp}"
TMP_REPO="$(mktemp -d "${TMPDIR_BASE%/}/banglathon.XXXXXX")"
REPO_URL="https://github.com/tasfiqueofficial/BanglaThon/archive/refs/heads/main.tar.gz"

curl -fsSL "$REPO_URL" -o "$TMP_REPO/core.tar.gz"
tar -xzf "$TMP_REPO/core.tar.gz" -C "$TMP_REPO"

rm -rf "$RUNTIME_DIR"
mkdir -p "$RUNTIME_DIR"
cp -R "$TMP_REPO/BanglaThon-main/." "$RUNTIME_DIR/"
rm -rf "$TMP_REPO"

# 3. Create standalone launcher script (forces UTF-8 for Bangla characters)
cat > "$BIN_DIR/bangla" <<EOF
#!/bin/sh
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
exec "$PY_EXE" "$RUNTIME_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/bangla"

# Install into ~/.local/bin and standard Mac bin folders if writable
cp "$BIN_DIR/bangla" "$LOCAL_BIN/bangla"
chmod +x "$LOCAL_BIN/bangla"

for sys_bin in "/opt/homebrew/bin" "/usr/local/bin"; do
    if [ -d "$sys_bin" ] && [ -w "$sys_bin" ]; then
        cp "$BIN_DIR/bangla" "$sys_bin/bangla" 2>/dev/null && chmod +x "$sys_bin/bangla" 2>/dev/null || true
    fi
done

# 4. Ensure PATH includes ~/.local/bin & ~/.bangla/bin in zsh & bash profiles
PATH_LINE='export PATH="$HOME/.local/bin:$HOME/.bangla/bin:$PATH"'
for rc in "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.bashrc"; do
    if [ -f "$rc" ]; then
        if ! grep -q '\.bangla/bin' "$rc" 2>/dev/null; then
            printf "\n# BanglaThon\n%s\n" "$PATH_LINE" >> "$rc"
        fi
    elif [ "$rc" = "$HOME/.zshrc" ] && [ "$(uname -s)" = "Darwin" ]; then
        printf "# BanglaThon\n%s\n" "$PATH_LINE" > "$rc"
    fi
done

# 5. Auto-install BanglaThon VS Code Extension if VS Code is installed
VSIX_PATH="$RUNTIME_DIR/vscode-banglathon/banglathon-vscode-0.1.1.vsix"
if [ -f "$VSIX_PATH" ]; then
    CODE_CLI=""
    if command -v code >/dev/null 2>&1; then
        CODE_CLI="$(command -v code)"
    elif [ -x "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code" ]; then
        CODE_CLI="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
    fi

    if [ -n "$CODE_CLI" ]; then
        printf "${CYAN}[+] VS Code-এ BanglaThon এক্সটেনশন (Syntax Highlighting + ▶ Run + File Icon) যুক্ত হচ্ছে...${NC}\n"
        "$CODE_CLI" --uninstall-extension tasfique.banglathon-vscode >/dev/null 2>&1 || true
        "$CODE_CLI" --install-extension "$VSIX_PATH" --force >/dev/null 2>&1 || true
    elif [ -d "$HOME/.vscode/extensions" ]; then
        rm -rf "$HOME/.vscode/extensions/tasfique.banglathon-vscode-"* "$HOME/.vscode/extensions/TasfiqueOfficial.banglathon-vscode-"*
        EXT_DEST="$HOME/.vscode/extensions/TasfiqueOfficial.banglathon-vscode-0.1.1"
        mkdir -p "$EXT_DEST"
        cp -R "$RUNTIME_DIR/vscode-banglathon/." "$EXT_DEST/" 2>/dev/null || true
    fi
fi

printf "\n"
printf "${GREEN}==========================================================${NC}\n"
printf "${GREEN} [✓] অভিনন্দন! macOS/Linux-এ BanglaThon সফলভাবে প্রস্তুত!${NC}\n"
printf "${GREEN}==========================================================${NC}\n\n"
"$BIN_DIR/bangla" --version
printf "\n${YELLOW}এখনই আপনার ফোল্ডারে সরাসরি চালান:${NC}\n"
printf "   ${CYAN}bangla run tas.bl${NC}\n"
printf "\n${YELLOW}নোট: যদি এই টার্মিনালে সাথে সাথে 'bangla' কমান্ড না পায়, লিখুন:${NC}\n"
printf "   ${CYAN}source ~/.zshrc${NC}\n\n"
