# tldrh — Data Architecture

## Sources canoniques

6 sources de données, dont 3 automatiques et 3 manuelles.

### Sources automatiques (mises à jour par Hermes)

| Source | Contenu | Accès | Utilisation |
|--------|---------|-------|-------------|
| [Docs page](https://hermes-agent.nousresearch.com/docs/reference/slash-commands) | Noms, descriptions longues, catégories | HTTP (BS4) | Description + catégories du listing |
| `COMMAND_REGISTRY` (`commands.py`) | args_hint, aliases, cli_only, gateway_only | Fichier local | Syntax, Aliases, Available, args_hint listing |
| `config.yaml` (clés top-level) | Dashboard config_bool | Fichier local | Dashboard section (section >) |

### Sources manuelles (maintenues par l'humain)

| Source | Contenu | Entrées |
|--------|---------|---------|
| `exclusions.yaml` | Commandes à exclure de tldrh | 25 |
| `notes.yaml` | Notes Dashboard + annotations | 10 |
| `examples.yaml` | Exemples au format OG tldr | 46 |

## Pipeline de génération

```
Docs page ──> 72 commandes brutes
                   │
                   ├── filtrer gateway_only (8) ──> 64 commandes TUI
                   │
                   ├── filtrer exclusions.yaml (25) ──> 47 commandes
                   │
                   ├── generate_listing.py
                   │     └── catégories + descriptions + args_hint
                   │     └── _listing.md (3 colonnes, largeur col2=64)
                   │
                   ├── generate_pages.py
                   │     ├── pour chaque commande :
                   │     │     ├── description  → docs page (1ère phrase)
                   │     │     ├── syntax       → args_hint
                   │     │     ├── aliases      → CommandDef.aliases
                   │     │     ├── available    → cli_only / gateway_only
                   │     │     ├── dashboard    → config.yaml (si clé top-level)
                   │     │     ├── notes        → notes.yaml (si entrée)
                   │     │     └── exemples     → examples.yaml (si entrée)
                   │     └── nettoie les .page.md orphelines
                   │
                   └── update.sh
                         ├── run listing + pages
                         ├── copie runtime
                         └── rapport diff examples.yaml vs commandes actuelles
```

## Format listing (`_listing.md`)

3 colonnes par catégorie. Largeur col2 = 64 caractères.

```
f"/{name:<20} {short:<64} {hint}"
```

- `{short:<64}` ne tronque PAS les descriptions > 64 chars
- Les catégories suivent l'ordre de la page docs

## Format page (`.page.md`)

Sections dans l'ordre, chaque ligne est optionnelle sauf Description et Available :

```
# command

> Description.                            ← 1ère phrase docs page
> Syntax: /cmd [arg]                      ← args_hint (si non vide)
> Aliases: /alias1, /alias2               ← CommandDef.aliases (si non vide)
> Available: Hermes TUI + Gateway         ← toujours

> Dashboard note...                       ← si clé top-level config.yaml
> Notes...                                ← si dans notes.yaml

- Example description:

`/command {{arg}}`

- Another example:

`/command --option`
```

Voir `tldrh_pages_style_guide.md` pour les règles détaillées.

## Exclusions (`exclusions.yaml`)

25 commandes exclues manuellement. Raisons :
- Commandes avancées (steer, branch, subgoal, bundles...)
- Gateway-only (footer)
- Enfantines ou redondantes (voice, yolo, skin...)

Les commandes `gateway_only=True` sont filtrées automatiquement par le générateur
et ne sont pas listées dans `exclusions.yaml`.

## Notes (`notes.yaml`)

10 commandes avec annotations :
- 8 commandes Dashboard (model, cron, skills, tools, toolsets, plugins, profile, kanban)
- goal : lien guide utilisateur + importance
- snapshot : conseil d'utilisation
- reasoning : commandes reliées

## Exemples (`examples.yaml`)

Format YAML :

```yaml
command-name:
  - desc: "Imperative description:"
    cmd: "/command {{value}}"
  - desc: "Another description:"
    cmd: "/command --option"
```

- 46 commandes avec exemples
- Les 0-arg (22 commandes) ont un exemple sans description
- Les commandes complexes (9) ont 2-4 exemples avec descriptions
- Max 5 exemples par commande

## Mise à jour

`update.sh` vérifie la cohérence entre `examples.yaml` et les commandes actuelles :
- Nouvelles commandes sans exemples → rapport diff
- Entrées orphelines dans examples.yaml → rapport diff
- Aucun fichier n'est modifié automatiquement. L'humain agit sur le rapport.

## Distribution

- `install.sh` : copie wrapper + pages + config
- README.md : documentation utilisateur
- CHANGELOG.md : historique des versions
- MIT License
