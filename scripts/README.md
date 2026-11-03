# 📂 Scripts d'Administration & Maintenance

Ce répertoire contient les outils en ligne de commande (CLI) permettant de gérer le cycle de vie de l'application Frugal AI Workbench, de la configuration des modèles à l'audit de performance avancé.

## 📋 Prérequis

Tous les scripts doivent être exécutés depuis la **racine du projet** pour que les imports Python (`src.core...`) fonctionnent correctement. Assurez-vous d'utiliser l'environnement virtuel du projet.

**Exemple d'exécution standard :**
```bash
# Windows
.venv\Scripts\python scripts/nom_du_script.py

# Mac/Linux
.venv/bin/python scripts/nom_du_script.py
```

---

## 📦 1. Gestionnaire de Modèles (`setup_models.py`)

Synchronise votre instance locale Ollama avec le fichier de configuration central `data/models.json`.

**Fonctionnalités :**
* Détection automatique des modèles manquants.
* Téléchargement avec barre de progression.
* Vérification des conflits de tags.

**Arguments :**

| Argument | Description |
| :--- | :--- |
| `(aucun)` | Installe tous les modèles manquants définis dans le JSON. |
| `--dry-run` | **Simulation :** Affiche ce qui serait installé sans rien télécharger. Utile pour vérifier l'état. |
| `--force` | **Réparation :** Force le re-téléchargement même si le modèle existe déjà (utile en cas de fichier GGUF corrompu). |

---

## 📈 2. Audit & Green Benchmark (`audit_and_update.py`)

Un outil avancé d'évaluation ("Eval Ops") qui réalise un **Stress Test progressif** sur chaque modèle installé.

**Ce que fait le script :**
1.  **Vérification Technique :** Tente un *Tool Call* réel pour vérifier si le modèle est compatible "Agent".
2.  **Stress Test Progressif (Ramp-up) :**
    * Teste des contextes croissants : **2k, 8k, 16k, 32k, 64k**.
    * **Sécurité RAM :** Vérifie la RAM système disponible avant chaque palier. Arrête l'escalade si la marge de sécurité (< 2 GB) est atteinte pour éviter le crash du PC.
    * **Détection de boucles :** Identifie si un modèle est trop "bavard" ou boucle, mais continue les tests de performance si la RAM le permet.
3.  **Métriques Précises :**
    * **RAM Modèle :** Isole la consommation spécifique des processus Ollama (ex: 0.5 GB).
    * **System Peak :** Mesure la charge totale du PC (ex: 14/32 GB).
    * **Empreinte Carbone :** Mesure via **CodeCarbon**.
4.  **Exports et Rapports :**
    * Mise à jour de `data/models.json` avec l'historique hiérarchique.
    * Génération d'un rapport lisible : `data/benchmark_report.md`.
    * **Nouveau :** Génération d'un dataset plat pour analyse (Data Science) : `data/benchmarks_data.csv`.

**Utilisation :**
Ce script ne prend pas d'arguments obligatoires. Il itère sur tous les modèles présents dans `models.json`.
*Note : Le benchmark peut prendre du temps car il teste plusieurs contextes par modèle.*

```bash
python scripts/audit_and_update.py
```

**Options disponibles :**

| Option | Description |
| :--- | :--- |
| `--skip-tested` | **Reprise intelligente :** Ignore les modèles qui possèdent déjà des données de benchmark. Utile pour reprendre un audit interrompu sans tout relancer. |

Exemple :
```bash
python scripts/audit_and_update.py --skip-tested
```

---

## ⚠️ Troubleshooting

**Erreur : `ModuleNotFoundError: No module named 'src'`**
* **Cause :** Vous avez lancé le script depuis le dossier `scripts/` (ex: `cd scripts && python setup_models.py`).
* **Solution :** Revenez à la racine du projet et lancez `python scripts/setup_models.py`.

**Erreur : `Ollama connection failed`**
* **Solution :** Assurez-vous que l'application Ollama tourne en arrière-plan et est accessible sur `http://localhost:11434`.

**"La RAM mesurée diminue quand le contexte augmente (Swap Detecté)"**
* **Symptôme :** Le rapport indique une RAM de 0.4GB pour un contexte de 32k tokens, alors qu'elle était de 4GB pour 16k tokens.
* **Cause :** Votre machine a saturé sa mémoire physique (RAM). Le système d'exploitation a déplacé la mémoire du modèle sur le disque dur (**Swapping**). 
* **Conséquence :** Le script détecte cette anomalie, arrête le test pour ce modèle et ne conserve que le "Max Valid Context" (le dernier avant le swap) pour garantir des métriques de performance fiables.

**"Mon nouveau modèle ajouté dans JSON n'est pas détecté"**
* **Symptôme :** Vous avez ajouté un bloc dans `models.json`, mais `setup_models.py` ne l'installe pas et le script d'audit le saute.
* **Cause :** Il manque probablement la clé `"type": "local"` dans votre configuration JSON. Les scripts filtrent les modèles pour ignorer ceux basés sur des API Cloud.
* **Solution :** Ajoutez `"type": "local"` dans l'objet JSON du modèle.

**"Logs : ⚠️ Bavard (Max output atteint)"**
* **Explication :** Ce n'est pas une erreur. Cela signifie que le modèle a généré une réponse plus longue que la limite de sécurité (512 tokens) imposée par le benchmark. Le test est considéré comme **VALIDE** (la RAM et la vitesse ont bien été mesurées), le script a simplement coupé la parole au modèle pour passer à la suite.