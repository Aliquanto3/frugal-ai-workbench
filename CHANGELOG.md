# Changelog

## 2.0.0a9 (2026-11-03)

### Changement de nom

- Le projet `wavelocalai` devient **Frugal AI Workbench** : dépôt `Aliquanto3/frugal-ai-workbench`,
  paquet Python `frugal_ai_workbench` (`src/frugal_ai_workbench/`, ancien `src/wavelocalai/`),
  commandes `frugal-ai-workbench` (v1) et `frugal-ai-workbench-v2` (v2), réglages
  `frugal-ai-workbench.toml` (ancien `wavelocalai.toml`). Les anciennes commandes n'existent plus.
- Anciens liens : `https://github.com/Aliquanto3/wavelocalai` redirige vers le nouveau dépôt, mais
  pas la page GitHub Pages : `https://aliquanto3.github.io/wavelocalai/` devient
  `https://aliquanto3.github.io/frugal-ai-workbench/`.

### Nouvelle charte

- Charte générique : primaire bleu pétrole (`#0B6B78` clair, `#4FC1CF` sombre), neutres gris
  ardoise, police Inter servie localement puis `system-ui`. Thème Streamlit
  (`.streamlit/config.toml`), jetons de la v2 (`tokens.css`, `DESIGN.md`) et maquettes mis à jour.
- Nouveau pictogramme (trois barres et un point d'accent), favicons et logotype texte.
- L'outil de démonstration « Recherche interne » devient `search_internal` (base fictive).

### Migration (anciens noms lus en repli)

- Variables d'environnement : `FRUGAL_AI_*` remplace `WAVELOCALAI_*` (v2) et `WAVELOCAL_*` (v1,
  `COUNTRY_ISO` et `PUE`). L'ancienne variable reste lue si la nouvelle est absente, avec un
  avertissement visible (`FutureWarning`).
- Réglages : sans `frugal-ai-workbench.toml`, la v2 lit `wavelocalai.toml` en repli, avec un
  avertissement visible (`FutureWarning`).
- Données : au premier lancement de la v2, `data/wavelocalai.db` est copiée vers
  `data/frugal-ai-workbench.db` si celle-ci n'existe pas encore, par l'API de sauvegarde de SQLite
  (instantané cohérent, journal `-wal` compris, même si un ancien serveur tient encore la base).
  L'ancienne base est gardée ; une seconde copie ne se fait jamais. Une copie impossible (verrou,
  disque plein, base illisible) ne bloque pas le démarrage : un avertissement s'affiche et la copie
  est retentée au lancement suivant. Le dossier `data/` ne change pas de nom.
- Les identifiants de données persistées de la v1 (collections Chroma `wavelocal_*`, projets
  CodeCarbon `wavelocal_session` et `wavelocal_audit`) gardent leur nom pour ne pas perdre
  l'historique.
- Brouillons non envoyés de la v2 (`localStorage`) : la clé passe à `frugal-ai-workbench.draft.*` ;
  un brouillon gardé sous `wavelocalai.draft.*` est repris à la première lecture.
- Équipes d'agents enregistrées avec l'ancien outil `search_wavestone_internal` : l'identifiant est
  traduit en `search_internal`, l'équipe se lance comme avant.
- Métriques Prometheus : `wavelocalai_inference_*` devient `frugal_ai_workbench_inference_*`, sans
  repli (exporteur sans usage connu).
- Exports JSON de la v2 : le champ `format` passe de `wavelocalai.conversation/1` et
  `wavelocalai.arena/1` à `frugal-ai-workbench.conversation/1` et `frugal-ai-workbench.arena/1`
  (l'application ne relit pas ces fichiers).
