# tldrh — tldr for Hermes

`tldrh` brings the familiar **tldr** format to [Hermes Agent](https://hermes-agent.nousresearch.com) slash commands. Quickly look up any `/command` without leaving the terminal.

```
$ tldrh
=== Session ===
/compress    Compress conversation context             [here [N] | focus ...]
/goal        Set a standing goal                       [text | draft ...]
/stop        Kill all running background processes     -

=== Configuration ===
/model       Switch model                              [model] [--provider ...]
/fast        Toggle fast mode                          [normal|fast|status]
...

$ tldrh compress
  Manually compress conversation context.

  Compress the entire conversation:

      /compress

  Keep the last 5 exchanges verbatim:

      /compress here 5
```

## Prerequisites

- [tealdeer](https://github.com/dbrgn/tealdeer) (Rust `tldr` client) — installed via your package manager or cargo
- Python 3.9+ with `requests`, `beautifulsoup4`, `lxml` and `pyyaml`

## Installation

### One-liner

```bash
curl -sSL https://raw.githubusercontent.com/gentlechills-netizen/tealdhermes/main/install.sh | bash
```

### Manual

```bash
# Clone the repo
git clone https://github.com/gentlechills-netizen/tealdhermes.git ~/.hermes/tldr-hermes

# Install the wrapper in PATH
mkdir -p ~/.local/bin
cp ~/.hermes/tldr-hermes/tldrh ~/.local/bin/
chmod +x ~/.local/bin/tldrh

# Ensure ~/.local/bin is in your PATH (add to .bashrc if not)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Install tealdeer config
mkdir -p ~/.config/tldrh
cp ~/.hermes/tldr-hermes/config.toml ~/.config/tldrh/config.toml

# Copy page files
mkdir -p ~/.local/share/tldrh/pages
cp ~/.hermes/tldr-hermes/pages/*.page.md ~/.local/share/tldrh/pages/
cp ~/.hermes/tldr-hermes/pages/_listing.md ~/.local/share/tldrh/pages/

# Install Python dependencies
pip install requests beautifulsoup4 lxml pyyaml
```

> **Note:** `tldrh` coexists with your normal `tldr` command. `tldr` shows system command help (cp, ls, git...), `tldrh` shows Hermes slash commands.

## Usage

```
tldrh                    List all Hermes commands by category
tldrh /compress          Show help for /compress (slash optional)
tldrh compress           Same as above
tldrh --help             Show usage
```

## Updating

When Hermes Agent is updated (new commands, changed descriptions):

```bash
cd ~/.hermes/tldr-hermes
./update.sh
```

This regenerates all pages and the listing from current sources.

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  hermets-agent/  │     │  generate_*.py   │     │  ~/.local/share/tldrh │
│  commands.py     │────▶│                  │────▶│  /pages/*.page.md   │
│  config.yaml     │     │  sources.py      │     │  /pages/_listing.md  │
│  docs page       │     │                  │     │                      │
│  notes.yaml      │     │  listing + pages │     │  tldrh (wrapper)     │
│  examples.yaml   │     └──────────────────┘     │     │
│  exclusions.yaml │                               │  tealdeer renders   │
└─────────────────┘                               └──────────────────────┘
```

Two generators share a common `sources.py` module:

- **`generate_listing.py`** — produces the 3-column category listing (`_listing.md`)
- **`generate_pages.py`** — produces individual `.page.md` files for each command

The wrapper `tldrh` uses tealdeer as its rendering engine with a separate config (`~/.config/tldrh/`) so it never interferes with your normal `tldr` setup.

## Project Structure

```
~/.hermes/tldr-hermes/
├── generate_listing.py     Listing generator
├── generate_pages.py       Page generator
├── sources.py              Shared data module
├── exclusions.yaml         Commands to exclude
├── notes.yaml              Dashboard exceptions
├── examples.yaml           Command examples
├── config.toml             tealdeer config template
├── tldrh                   Wrapper script
├── install.sh              Installation script
├── update.sh               Regenerate everything
├── README.md               This file
└── pages/                  Generated output
    ├── _listing.md
    └── *.page.md
```

## License

MIT
