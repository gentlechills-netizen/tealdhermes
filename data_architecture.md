# tldrh — Data Architecture

## Sources canoniques

6 sources de données, dont 1 automatique et 5 manuelles.

### Source automatique (mise à jour par Hermes)

| Source | Contenu | Accès | Utilisation |
|--------|---------|-------|-------------|
| `COMMAND_REGISTRY` (`commands.py`) | Noms, descriptions courtes, catégories, args_hint, aliases, cli_only, gateway_only | Fichier local (parse statique) | Nom + description listing, syntaxe, aliases, disponibilité, args_hint |

### Sources manuelles (maintenues par l'humain)

| Source | Contenu | Entrées |
|--------|---------|---------|
| `descriptions_longues.yaml` | Descriptions longues figées (dernier scraping docs, juillet 2026) | 72 |
| `exclusions.yaml` | Commandes à exclure de tldrh | 25 |
| `overrides.yaml` | Remplacements manuels pour args_hint (et autres champs) | 2 |
| `notes.yaml` | Notes Dashboard + annotations | 11 |
| `examples.yaml` | Exemples au format OG tldr | 49 |

### Déprécié

La page docs (`/reference/slash-commands`) n'est plus utilisée comme source.
Elle était incomplète et décalée par rapport au code. COMMAND_REGISTRY est
maintenant la source canonique unique.

## Pipeline de génération

```
COMMAND_REGISTRY ──> 82 CommandDef
       │
       ├── filtrer gateway_only (7) ──> 75 commandes TUI
       │
       ├── filtrer exclusions.yaml (25) ──> 50 commandes
       │
       ├── filtrer cli/gateway (1) ──> 49 pages
       │
       ├── generate_listing.py
       │     └── catégories + descriptions + args_hint
       │     └── _listing.md (3 colonnes, largeur col2=64)
       │
       ├── generate_pages.py
       │     ├── pour chaque commande :
       │     │     ├── description  → descriptions_longues.yaml (fallback: COMMAND_REGISTRY)
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
- Les catégories suivent l'ordre de COMMAND_REGISTRY

## Format page (`.page.md`)

Sections dans l'ordre, chaque ligne est optionnelle sauf Description et Available :

```
# command

> Description.                            ← descriptions_longues.yaml (fallback COMMAND_REGISTRY)
> Syntax: /cmd [arg]                      ← args_hint (si non vide)
> Aliases: /alias1, /alias2               ← CommandDef.aliases (si non vide)
> Available: Hermes TUI                   ← toujours

> Dashboard note...                       ← si clé top-level config.yaml
> Notes...                                ← si dans notes.yaml

- Example description:

`/command {{arg}}`
```

Voir `tldrh_pages_style_guide.md` pour les règles détaillées.

## Exclusions (`exclusions.yaml`)

25 commandes exclues manuellement. Raisons :
- Commandes avancées (steer, branch, subgoal, bundles...)
- Gateway-only (footer)
- Enfantines ou redondantes (voice, yolo, skin...)

Les commandes `gateway_only=True` sont filtrées automatiquement par le générateur
et ne sont pas listées dans `exclusions.yaml`.

## Descriptions longues (`descriptions_longues.yaml`)

Fichier figé contenant les descriptions longues extraites de la page docs Hermes
lors du dernier scraping (16 juillet 2026). Utilisé par `generate_pages.py` pour
la section `> Description` des pages. Si une commande n'y figure pas, le générateur
utilise la description courte de COMMAND_REGISTRY (fallback inoffensif).

Ajout manuel possible : éditer le fichier YAML et ajouter une entrée.

## Overrides (`overrides.yaml`)

Remplacements manuels pour certains champs de `COMMAND_REGISTRY`.
Utile pour raccourcir un `args_hint` trop long sans modifier `commands.py`.

Structure :
```yaml
command_name:
  args_hint: "[valeur personnalisée]"
```

Actuellement : 2 overrides — `compress` et `goal` (args_hint raccourcis).

## Notes (`notes.yaml`)

11 commandes avec annotations :
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

- 49 commandes avec exemples
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
