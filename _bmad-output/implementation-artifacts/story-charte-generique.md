---
title: 'Story 1.2 du run « dépôts publics » : Frugal AI Workbench, nom et charte génériques'
type: 'chore'
created: '2026-11-03'
status: 'review'
baseline_commit: 'c3195e5'
context:
  - 'brief-story-1x.md, regles-debrand.md, charte-generique.md (dossier _bmad-output/implementation-artifacts du dossier GitHub parent)'
warnings:
  - 'primaryColor sombre de Streamlit : #0B7A86 au lieu de #4FC1CF de la charte (Streamlit pose du texte blanc sur la primaire ; #4FC1CF ne donne que 2,13:1)'
  - 'Écart accepté par axe (pastilles Agent_Lab sombres) recalculé, pas mesuré : #0b7a86 sur #0e1d21, 3,41:1, à confirmer par la suite E2E nocturne'
deferred:
  - '2.1 : workflow sync-slm-results.yml, dépôt privé wavelocalai-private-questions, chemins data/quality_bench/wavelocalai de slm-quality-bench'
  - 'Captures (docs/assets, tools/e2e) non régénérées dans cette story'
  - 'Archive docs/archive/ancienne-v2 et audits : nom de l ancien dépôt wave_local_ai_v2 gardé (autre projet, historique)'
---

# Story 1.2 : Frugal AI Workbench, nom et charte génériques

Le dépôt `wavelocalai` devient `frugal-ai-workbench` (nom affiché « Frugal AI Workbench »), version
2.0.0a9. Paquet `src/frugal_ai_workbench/`, commandes `frugal-ai-workbench` et
`frugal-ai-workbench-v2`, réglages `frugal-ai-workbench.toml`, préfixe d'environnement `FRUGAL_AI_`.

## Fait

1. Renommage complet (code, tests, docs, `_bmad-output`, `pyproject.toml`, `uv.lock`, CITATION.cff,
   AGENTS.md), sans alias des anciennes commandes.
2. Compatibilité : `config.with_legacy_env` (v2) et `src/core/config.env_with_legacy` (v1, la v1
   n'important jamais la v2) lisent les anciennes variables en repli avec un `FutureWarning`
   (visible par défaut) ;
   `store.datadir.migrate_legacy_db` copie `wavelocalai.db` et son `-wal` au lancement (transit
   propre au processus, nettoyé en cas d'`OSError` ; un échec n'empêche jamais le démarrage). Preuve :
   `tests/v2/unit/test_rename_compat.py`.
3. Charte générique : `.streamlit/config.toml`, `tokens.css` de la v2 et `DESIGN.md` (que
   `test_shell_static.py` compare), maquettes, trois favicons, logotype `src/app/static/wordmark.svg`.
   En v2, `chart-2` reste vert (local, réussi) et `chart-4` or (attention) : `succes` et `cat-8` de la
   charte, pour garder le sens des badges et bandeaux. Aucun texte posé sur `risk` ou `accent-green` :
   le jeton `sur-statut` n'avait pas d'usage ; le texte sur la primaire suit `on-primary`.
4. Marque retirée : mentions Wavestone, affiliation, remerciements, outil « Recherche interne
   Wavestone » (`search_internal`), rapport `output/benchmark-slm-wavelocalai.html` aux couleurs
   Wavestone supprimé.
5. CHANGELOG créé avec l'entrée 2.0.0a9.
