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

$ tldrh journey

  A playable and editable timeline of the memories and skills Hermes has
  learned with you over time.

  Show the learning timeline:

      /journey

  List all learned items:

      /journey list
```

## Prerequisites

- [tealdeer](https://github.com/dbrgn/tealdeer) (Rust `tldr` client) — installed via your package manager or cargo
- Python 3.9+ with `pyyaml`

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
```

> **Note:** `tldrh` coexists with your normal `tldr` command. `tldr` shows system command help (cp, ls, git...), `tldrh` shows Hermes slash commands.

## Usage

```
tldrh                    List all Hermes commands by category
tldrh /journey           Show help for /journey (slash optional)
tldrh journey            Same as above
tldrh --help             Show usage
```

## Updating

When Hermes Agent is updated (new commands, changed descriptions):

```bash
cd ~/.hermes/tldr-hermes
./update.sh
```

This regenerates all pages and the listing from `COMMAND_REGISTRY` (no network calls).

## How It Works

The wrapper `tldrh` searches only the custom pages directory. If a page isn't found, it shows a clear error (no fallback to system tldr pages).

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  hermes-agent/   │     │  generate_*.py   │     │  ~/.local/share/tldrh │
│  commands.py     │────▶│                  │────▶│  /pages/*.page.md   │
│  config.yaml     │     │  sources.py      │     │  /pages/_listing.md  │
│  descriptions    │     │                  │     │                      │
│   _longues.yaml  │     │  listing + pages │     │  tldrh (wrapper)     │
│  notes.yaml      │     └──────────────────┘     │     │
│  examples.yaml   │                               │  tealdeer renders   │
│  exclusions.yaml │                               └──────────────────────┘
└─────────────────┘
```

Two generators share a common `sources.py` module:

- **`generate_listing.py`** — parses `COMMAND_REGISTRY`, produces the 3-column category listing (`_listing.md`)
- **`generate_pages.py`** — parses `COMMAND_REGISTRY` + `descriptions_longues.yaml`, produces individual `.page.md` files for each command

No external dependencies beyond `pyyaml`. No network calls. All data comes from Hermes' own `commands.py` and local YAML files.

The wrapper `tldrh` uses tealdeer as its rendering engine with a separate config (`~/.config/tldrh/`) so it never interferes with your normal `tldr` setup.

## Project Structure

```
~/.hermes/tldr-hermes/
├── generate_listing.py          Listing generator
├── generate_pages.py            Page generator
├── sources.py                   Shared data module
├── descriptions_longues.yaml    Long descriptions (frozen)
├── exclusions.yaml              Commands to exclude
├── notes.yaml                   Dashboard exceptions
├── examples.yaml                Command examples
├── overrides.yaml               Manual field overrides
├── config.toml                  tealdeer config template
├── tldrh                        Wrapper script
├── install.sh                   Installation script
├── update.sh                    Regenerate everything
├── README.md                    This file
└── pages/                       Generated output
    ├── _listing.md
    └── *.page.md
```

## License

MIT
