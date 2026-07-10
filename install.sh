#!/bin/bash
# install.sh — Installe tldrh (TLDR pour Hermes)
# Usage: curl -sSL https://.../install.sh | bash

set -e

TLDRH_BIN="${TLDRH_BIN:-$HOME/.local/bin/tldrh}"
TLDRH_PAGES="${TLDRH_PAGES:-$HOME/.local/share/tldrh/pages}"
TLDRH_CONFIG="${TLDRH_CONFIG:-$HOME/.config/tldrh/config.toml}"

echo "📦 Installation de tldrh..."

# 1. Créer les répertoires
mkdir -p "$(dirname "$TLDRH_BIN")"
mkdir -p "$TLDRH_PAGES"
mkdir -p "$(dirname "$TLDRH_CONFIG")"

# 2. Installer le wrapper
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/tldrh" ]; then
    cp "$SCRIPT_DIR/tldrh" "$TLDRH_BIN"
else
    echo "⚠ Script tldrh introuvable. Télécharger depuis GitHub..."
    curl -sSL -o "$TLDRH_BIN" "https://raw.githubusercontent.com/gentlechills-netizen/tealdhermes/main/tldrh"
fi
chmod +x "$TLDRH_BIN"

# 3. Installer les pages
if [ -d "$SCRIPT_DIR/pages" ]; then
    cp "$SCRIPT_DIR/pages/"*.page.md "$TLDRH_PAGES/" 2>/dev/null || true
    cp "$SCRIPT_DIR/pages/_listing.md "$TLDRH_PAGES/" 2>/dev/null || true
fi

# 4. Config tealdeer
if [ ! -f "$TLDRH_CONFIG" ]; then
    cat > "$TLDRH_CONFIG" << 'EOF'
[directories]
custom_pages_dir = "${HOME}/.local/share/tldrh/pages"
[updates]
auto_update = false
[display]
compact = true
use_pager = false
EOF
fi

# 5. Ajouter ~/.local/bin au PATH si pas déjà
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "→ ~/.local/bin ajouté au PATH dans .bashrc"
fi

echo "✅ tldrh installé dans $TLDRH_BIN"
echo ""
echo "Ouvre un nouveau terminal ou source ~/.bashrc :"
echo "  source ~/.bashrc"
echo ""
echo "Usage :"
echo "  tldrh              Lister les commandes"
echo "  tldrh stop         Page d'aide de /stop"
