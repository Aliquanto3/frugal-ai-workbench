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
  - '2.1 : workflow sync-slm-results.yml, le dépôt privé de questions, chemins data/quality_bench/wavelocalai de slm-quality-bench'
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
   `store.datadir.migrate_legacy_db` copie `wavelocalai.db` au lancement, après la prise du verrou,
   par l'API de sauvegarde de SQLite (source en lecture seule, instantané cohérent `-wal` compris,
   même si un ancien serveur tient la base ; ni `-wal` ni `-shm` à copier), vers un fichier de
   transit propre au processus puis `os.replace` ; nettoyé en cas d'`OSError` ou de
   `sqlite3.Error`, un échec n'empêche jamais le démarrage. Repli de `wavelocalai.toml`
   (`FutureWarning`), des brouillons `wavelocalai.draft.*` et de l'outil
   `search_wavestone_internal` (`agents/tools/registry.LEGACY_TOOL_IDS`). Preuve :
   `tests/v2/unit/test_rename_compat.py`, `test_agent_crews.py`, `tests/v2/e2e/test_chat.py`.
3. Charte générique : `.streamlit/config.toml`, `tokens.css` de la v2 et `DESIGN.md` (que
   `test_shell_static.py` compare), maquettes, trois favicons, logotype `src/app/static/wordmark.svg`.
   En v2, `chart-2` reste vert (local, réussi) et `chart-4` or (attention) : `succes` et `cat-8` de la
   charte, pour garder le sens des badges et bandeaux. Aucun texte posé sur `risk` ou `accent-green` :
   le jeton `sur-statut` n'avait pas d'usage ; le texte sur la primaire suit `on-primary`.
4. Marque retirée : mentions de l'ancienne marque, affiliation, remerciements, outil « Recherche
   interne » de l'ancienne marque (`search_internal`), rapport `output/benchmark-slm-wavelocalai.html`
   aux couleurs de l'ancienne marque supprimé.
5. CHANGELOG créé avec l'entrée 2.0.0a9.

## Revue

### Passe 1 (2026-11-03, SHA revu 28db4ed)

Base à jour (`origin/master` c3195e5, aucun rebase nécessaire).

- Important, medium, second avis 1 : équipe enregistrée avec `search_wavestone_internal` refusée (422). Corrigé : alias unique `registry.LEGACY_TOOL_IDS`, appliqué par `ToolRegistry.get` et `crews.agent_from` ; test `test_a_crew_stored_with_the_legacy_tool_id_still_runs`.
- Important, medium, second avis 2 : brouillons `wavelocalai.draft.*` perdus. Corrigé : `loadDraft` reprend l'ancienne clé, la range sous la nouvelle et retire l'ancienne ; test E2E `test_a_draft_kept_under_the_legacy_name_is_migrated` (Edge local, vert). CHANGELOG mis à jour.
- Important, medium, second avis 3 : `wavelocalai.toml` non lu en repli. Corrigé : `config._default_toml` (`FutureWarning`) ; deux tests, ligne au CHANGELOG.
- Important, medium, second avis 4 et 5 : copie fichier par fichier d'une base WAL peut-être ouverte. Corrigé : API de sauvegarde SQLite (source `mode=ro` en URI, transit propre au processus, `os.replace`), déjà après la prise du verrou ; `sqlite3.Error` non bloquant au lancement. Le lecteur en lecture seule peut poser un `-wal`/`-shm` vides à côté de l'ancienne base (fichiers de SQLite, la base n'est pas modifiée).
- Important, low, second avis 6 : tests de migration sur des octets factices. Corrigé : vraie base WAL avec lignes encore au journal, connexion tenue ouverte pendant la copie ; base illisible au lancement.
- Nit, low, second avis 7 : métriques Prometheus renommées sans mention. Corrigé : ligne au CHANGELOG.
- Nit, low, second avis 8 : `WAVELOCALAI_E2E_CHROMIUM` sans repli. Rejeté : variable de test seulement.
- Important, low, second avis 9 : « Wavestone » et nom du dépôt privé dans cette spec. Corrigé.
- Second avis 10 : captures. Rejeté : `docs/assets/v2-*` régénérées par ce commit, `docs/audits/*/captures` archives datées.
- Nit, low, reviewer : champ `format` des exports JSON renommé sans mention. Corrigé : ligne au CHANGELOG (aucun lecteur dans l'application).
- Nit, low, reviewer : `src/core/config.py` (importé par `scripts/benchmark_slm.py`) modifié hors PR de benchmark, contre la règle d'AGENTS.md. Rejeté : défauts inchangés (`FRA`, `1.1`), seul le nom de la variable lue change, imposé par le renommage.
- Complexité : 0 constat.
