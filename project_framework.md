# tldrh — Project Framework

## Objectif

Un `tldr` pour Hermes. L'utilisateur tape `tldrh goal` et voit la page d'aide de
`/goal` au format OG tldr. Il tape `tldrh` et voit la liste des commandes Hermes
disponibles, groupées par catégorie.

`tldr tar` continue de fonctionner pour les commandes Linux. Les deux cohabitent
via `TEALDEER_CONFIG_DIR` séparé.

**Public cible :** Utilisateurs TUI d'Hermes Agent.

## Architecture

```
tealdeer (Rust, 2MB)
   └─ TEALDEER_CONFIG_DIR=~/.config/tldrh/   ← config séparée
        └─ custom_pages_dir → ~/.local/share/tldrh/pages/
              ├── _listing.md                 ← listing 3 colonnes
              └── compress.page.md            ← page individuelle

wrapper ~/.local/bin/tldrh (bash)
   ├─ `tldrh`         → cat _listing.md
   └─ `tldrh model`   → TEALDEER_CONFIG_DIR=... tldr model

générateurs (Python)
   ├─ generate_listing.py  → _listing.md
   └─ generate_pages.py    → *.page.md
        └─ sources.py      ← module partagé
```

## Fichiers et répertoires

```
~/.hermes/tldr-hermes/               ← Projet (sources)
├── generate_listing.py              ← Volet 1 : listing 3 colonnes
├── generate_pages.py                ← Volet 2 : pages .page.md
├── sources.py                       ← Module partagé (scraping, parsing)
├── update.sh                        ← Regénère tout + rapport diff
├── install.sh                       ← Installation one-liner
├── tldrh                            ← Wrapper bash
├── config.toml                      ← Patron config tealdeer
├── exclusions.yaml                  ← 25 commandes exclues
├── examples.yaml                    ← 46 commandes avec exemples
├── notes.yaml                       ← 10 commandes avec notes Dashboard
├── .gitignore
├── README.md                        ← Documentation utilisateur
├── project_framework.md             ← Ce fichier
├── data_architecture.md             ← Sources de données canoniques
├── tldrh_pages_style_guide.md       ← Règles de format des pages
├── LICENSE                          ← MIT
├── CHANGELOG.md                     ← Historique des versions
└── reports/                         ← Rapports de diff (générés)

~/.local/bin/tldrh                   ← Wrapper installé (PATH)
~/.config/tldrh/config.toml          ← Config tealdeer runtime
~/.local/share/tldrh/pages/          ← Pages runtime
```

## Principaux scripts

| Script | Rôle |
|--------|------|
| `update.sh` | Vérifie les sources, génère listing + pages, copie runtime, produit rapport diff |
| `generate_listing.py` | Scrape docs + COMMAND_REGISTRY, filtre exclusions, produit _listing.md |
| `generate_pages.py` | Scrape docs + COMMAND_REGISTRY + notes + examples, produit 47 .page.md |
| `install.sh` | Copie wrapper dans PATH, pages dans share/, config dans .config/ |

## Mise à jour

Quand Hermes change (nouvelles commandes, descriptions modifiées) :

```bash
cd ~/.hermes/tldr-hermes && ./update.sh
```

Le script :
1. Vérifie que tous les fichiers source existent
2. Exécute `generate_listing.py` et `generate_pages.py`
3. Copie les pages dans le répertoire runtime
4. Compare `examples.yaml` avec les commandes actuelles et produit un rapport de diff

Le rapport de diff signale :
- Nouvelles commandes sans exemples → à ajouter dans `examples.yaml`
- Entrées orphelines dans `examples.yaml` → commandes supprimées, à nettoyer

Si aucune différence, aucun rapport n'est produit.

## Sources de données

Voir `data_architecture.md` pour la description complète des 6 sources canoniques :
docs page, COMMAND_REGISTRY, config.yaml, exclusions.yaml, notes.yaml, examples.yaml.
