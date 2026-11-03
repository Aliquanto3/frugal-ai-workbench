import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

# Chargement du .env
load_dotenv()

# Définition des chemins absolus
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
LOGS_DIR = DATA_DIR / "logs"
EMISSIONS_DIR = LOGS_DIR / "emissions"
BENCHMARKS_DIR = LOGS_DIR / "benchmarks"

# Source de vérité unique pour les modèles
MODELS_JSON_PATH = DATA_DIR / "models.json"

# Création des dossiers s'ils n'existent pas
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Marge de sécurité RAM (en GB) pour l'OS et les autres apps
SYSTEM_RAM_BUFFER_GB = 0.5

# Configuration API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


def env_with_legacy(name: str, default: str, environ=None) -> str:
    """Lit `FRUGAL_AI_<name>`, sinon l'ancien `WAVELOCAL_<name>` (dépréciation signalée), sinon
    `default`."""
    env = os.environ if environ is None else environ
    value = env.get(f"FRUGAL_AI_{name}")
    if value:
        return value
    legacy = env.get(f"WAVELOCAL_{name}")
    if legacy:
        warnings.warn(
            f"La variable WAVELOCAL_{name} est dépréciée : renommez-la en FRUGAL_AI_{name}.",
            FutureWarning,
            stacklevel=2,
        )
        return legacy
    return default


# --- CONFIGURATION GREEN IT (Restaurée) ---
DEFAULT_COUNTRY_ISO_CODE = env_with_legacy("COUNTRY_ISO", "FRA")
DEFAULT_PUE = float(env_with_legacy("PUE", "1.1"))


def get_emissions_path() -> str:
    return str(EMISSIONS_DIR / "emissions.csv")
