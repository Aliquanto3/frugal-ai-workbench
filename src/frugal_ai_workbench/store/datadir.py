"""Dossier de données : création, alerte OneDrive et verrou d'instance unique (AD-23)."""

from __future__ import annotations

import errno
import os
import sqlite3
import sys
from pathlib import Path
from typing import IO

LOCK_NAME = ".frugal-ai-workbench.lock"
# Base de l'ancien nom du projet (wavelocalai, jusqu'à 2.0.0a8), copiée au premier lancement.
LEGACY_DB_NAME = "wavelocalai.db"


class DataDirLockError(Exception):
    """Le verrou du dossier de données n'a pas pu être pris (la cause est dans le message)."""


class DataDirLockedError(DataDirLockError):
    """Un autre serveur utilise déjà ce dossier de données."""


# Codes d'un verrou déjà tenu (`msvcrt.locking` : EACCES ou EDEADLOCK ; `flock` : EAGAIN).
_HELD = {errno.EACCES, errno.EAGAIN, errno.EDEADLK, getattr(errno, "EWOULDBLOCK", errno.EAGAIN)}


def ensure_data_dir(path: Path) -> Path:
    """Crée le dossier de données (et son sous-dossier de journaux) s'il manque."""
    (path / "logs").mkdir(parents=True, exist_ok=True)
    return path


def migrate_legacy_db(data_dir: Path, db_name: str) -> list[Path]:
    """Copie la base de l'ancien nom (`wavelocalai.db`) vers `db_name`, par l'API de sauvegarde
    de SQLite.

    Seulement si la nouvelle base n'existe pas encore : l'ancienne n'est jamais supprimée ni
    modifiée (ouverte en lecture seule), et un second appel ne fait rien. La sauvegarde lit un
    instantané cohérent, `-wal` compris, même si un ancien serveur a encore la base ouverte ; elle
    écrit dans un fichier de transit propre au processus, renommé ensuite : la nouvelle base
    n'apparaît que complète. En cas d'`OSError` ou de `sqlite3.Error` (verrou, disque plein, base
    illisible), le fichier de transit est retiré avant de relancer l'erreur : la copie sera
    retentée au lancement suivant. Rend les fichiers créés.
    """
    new = data_dir / db_name
    old = data_dir / LEGACY_DB_NAME
    if new.exists() or not old.is_file():
        return []
    staging = new.with_name(f"{new.name}.copie-{os.getpid()}")
    try:
        staging.unlink(missing_ok=True)
        source = sqlite3.connect(f"{old.resolve().as_uri()}?mode=ro", uri=True)
        try:
            target = sqlite3.connect(staging)
            try:
                source.backup(target)
                # La copie garde le mode WAL de l'originale : on la referme propre, sans `-wal`.
                target.execute("PRAGMA journal_mode=DELETE")
            finally:
                target.close()
        finally:
            source.close()
        os.replace(staging, new)
    except (OSError, sqlite3.Error):
        for leftover in (staging, *_sidecars(staging)):
            leftover.unlink(missing_ok=True)
        raise
    return [new]


def _sidecars(path: Path) -> tuple[Path, ...]:
    return tuple(path.with_name(path.name + suffix) for suffix in ("-wal", "-shm", "-journal"))


def is_under_onedrive(path: Path) -> bool:
    """Vrai si un composant du chemin est un dossier OneDrive : la synchronisation peut corrompre
    la base SQLite en mode WAL."""
    return any(part.lower().startswith("onedrive") for part in path.resolve().parts)


class DataDirLock:
    """Verrou exclusif sur un fichier du dossier de données, tenu tant que le serveur vit.

    Le système le libère aussi si le processus meurt : pas de verrou périmé à nettoyer.
    """

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.path = data_dir / LOCK_NAME
        self._handle: IO[bytes] | None = None

    def acquire(self) -> None:
        """Prend le verrou. `DataDirLockedError` si un serveur vivant le tient ; toute autre
        cause (droits, disque plein, dossier absent) est dite telle quelle (`DataDirLockError`)."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.path.touch(exist_ok=True)
            handle = self.path.open("r+b")
        except OSError as exc:
            raise DataDirLockError(
                f"Impossible de créer le verrou {self.path} : {exc.strerror or exc}. "
                "Vérifiez les droits et l'espace disque du dossier de données, ou choisissez un "
                "autre dossier (--data-dir)."
            ) from exc
        try:
            _lock(handle)
        except OSError as exc:
            handle.close()
            if exc.errno in _HELD or getattr(exc, "winerror", None) in {33, 32}:
                raise DataDirLockedError(
                    f"Un autre frugal-ai-workbench-v2 utilise déjà le dossier de données {self.data_dir}. "
                    "Arrêtez-le, ou choisissez un autre dossier (--data-dir)."
                ) from exc
            raise DataDirLockError(
                f"Impossible de prendre le verrou {self.path} : {exc.strerror or exc}."
            ) from exc
        self._handle = handle

    def release(self) -> None:
        if self._handle is None:
            return
        try:
            _unlock(self._handle)
        finally:
            self._handle.close()
            self._handle = None

    def __enter__(self) -> DataDirLock:
        self.acquire()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.release()


if sys.platform == "win32":  # pragma: no cover - une seule branche par plateforme
    import msvcrt

    def _lock(handle: IO[bytes]) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(handle: IO[bytes]) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:  # pragma: no cover
    import fcntl

    def _lock(handle: IO[bytes]) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(handle: IO[bytes]) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
