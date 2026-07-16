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
        └─ sources.py      ← module partagé (sans dépendances réseau)
```

## Fichiers et répertoires

```
~/.hermes/tldr-hermes/               ← Projet (sources)
├── generate_listing.py              ← Volet 1 : listing 3 colonnes
├── generate_pages.py                ← Volet 2 : pages .page.md
├── sources.py                       ← Module partagé (parsing COMMAND_REGISTRY + YAML)
├── update.sh                        ← Regénère tout + rapport diff
├── install.sh                       ← Installation one-liner
├── tldrh                            ← Wrapper bash
├── config.toml                      ← Patron config tealdeer
├── descriptions_longues.yaml        ← 72 descriptions longues figées
├── exclusions.yaml                  ← 25 commandes exclues
├── overrides.yaml                   ← 2 overrides manuels
├── examples.yaml                    ← 49 commandes avec exemples
├── notes.yaml                       ← 11 commandes avec notes Dashboard
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
| `generate_listing.py` | Parse COMMAND_REGISTRY, filtre exclusions + gateway_only, produit _listing.md |
| `generate_pages.py` | Parse COMMAND_REGISTRY + descriptions_longues.yaml + notes + examples, produit 49 .page.md |
| `install.sh` | Copie wrapper dans PATH, pages dans share/, config dans .config/ |

## Mise à jour

Quand Hermes change (nouvelles commandes, descriptions modifiées) :

```bash
cd ~/.hermes/tldr-hermes && ./update.sh
```

Le script :
1. Vérifie que tous les fichiers source existent
2. Exécute `generate_listing.py` → `pages/_listing.md` (listing 3 colonnes par catégorie)
3. Exécute `generate_pages.py` → `pages/*.page.md` (pages individuelles), nettoie les orphelines
4. Compare `examples.yaml` avec les commandes actuelles et produit un rapport de diff

Note : `generate_listing.py` applique les overrides de `overrides.yaml` (ex: args_hint personnalisé).

Le rapport de diff signale :
- Nouvelles commandes sans exemples → le mainteneur ajoute manuellement dans `examples.yaml`
- Entrées orphelines dans `examples.yaml` → le mainteneur nettoie

**Règle fondamentale :** les exemples sont créés et révisés manuellement par le mainteneur, sans automatisation ni IA. Le rapport diff est un outil d'information pour l'humain — aucun agent Hermes ne modifie `examples.yaml` suite à un diff.

Si aucune différence, aucun rapport n'est produit.

## Piège — alias bash périmé après modification

Après toute modification du wrapper (`tldrh`) ou de l'alias dans `.bash_aliases`, le développeur DOIT exécuter `source ~/.bashrc` (ou ouvrir un nouveau terminal). Les alias bash sont chargés en mémoire au démarrage de la session — changer le fichier ne met pas à jour la session courante.

Un agent Hermes qui omet cette étape force le développeur à déboguer un problème qui n'existe pas : le fichier est bon, le wrapper est bon, mais le shell exécute encore l'ancien alias pointant vers une version périmée ou un projet mort.

**Vérification :** `type tldrh` dans le terminal du développeur — si le chemin affiché n'est pas celui attendu, la session n'est pas à jour.

## Sources de données

Voir `data_architecture.md` pour la description complète des 6 sources :
COMMAND_REGISTRY, descriptions_longues.yaml, exclusions.yaml, overrides.yaml, notes.yaml, examples.yaml.
