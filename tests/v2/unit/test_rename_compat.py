"""Compatibilité avec l'ancien nom (wavelocalai, jusqu'à 2.0.0a8) : variables d'environnement
lues en repli et base de données copiée au premier lancement."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import warnings

import pytest

from frugal_ai_workbench.__main__ import main
from frugal_ai_workbench.config import load_settings, with_legacy_env
from frugal_ai_workbench.store.datadir import LEGACY_DB_NAME, migrate_legacy_db
from frugal_ai_workbench.store.db import DB_NAME
from frugal_ai_workbench.store.logs import close_logging

# --- Variables d'environnement ------------------------------------------------------------------


def test_legacy_variable_is_read_when_the_new_one_is_absent():
    with pytest.warns(FutureWarning, match="WAVELOCALAI_PORT est dépréciée.*FRUGAL_AI_PORT"):
        values = with_legacy_env({"WAVELOCALAI_PORT": "9300", "OTHER": "x"})
    assert values == {"WAVELOCALAI_PORT": "9300", "FRUGAL_AI_PORT": "9300", "OTHER": "x"}


def test_new_variable_wins_without_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        values = with_legacy_env({"WAVELOCALAI_PORT": "9300", "FRUGAL_AI_PORT": "9400"})
    assert values["FRUGAL_AI_PORT"] == "9400"


def test_empty_new_variable_falls_back_to_the_legacy_one():
    with pytest.warns(FutureWarning):
        values = with_legacy_env({"FRUGAL_AI_TESTING": "", "WAVELOCALAI_TESTING": "1"})
    assert values["FRUGAL_AI_TESTING"] == "1"


def test_empty_legacy_variable_is_ignored():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert with_legacy_env({"WAVELOCALAI_PORT": ""}) == {"WAVELOCALAI_PORT": ""}


def test_load_settings_reads_legacy_variables(tmp_path):
    toml = tmp_path / "frugal-ai-workbench.toml"
    toml.write_text("", encoding="utf-8")
    with pytest.warns(FutureWarning) as caught:
        settings = load_settings(
            toml,
            tmp_path / "absent.env",
            environ={"WAVELOCALAI_PORT": "9301", "WAVELOCALAI_TESTING": "1"},
        )
    assert settings.server.port == 9301
    assert settings.testing is True
    assert {str(w.message).split()[2] for w in caught} == {
        "WAVELOCALAI_PORT",
        "WAVELOCALAI_TESTING",
    }


def test_v1_reads_the_legacy_variable_with_a_warning():
    from src.core.config import env_with_legacy

    with pytest.warns(FutureWarning, match="WAVELOCAL_PUE est dépréciée.*FRUGAL_AI_PUE"):
        assert env_with_legacy("PUE", "1.1", {"WAVELOCAL_PUE": "1.4"}) == "1.4"
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        environ = {"WAVELOCAL_PUE": "1.4", "FRUGAL_AI_PUE": "1.2"}
        assert env_with_legacy("PUE", "1.1", environ) == "1.2"
        assert env_with_legacy("PUE", "1.1", {}) == "1.1"


# --- Base de données -----------------------------------------------------------------------------


def test_legacy_db_and_wal_are_copied_and_kept(tmp_path):
    (tmp_path / LEGACY_DB_NAME).write_bytes(b"base")
    (tmp_path / f"{LEGACY_DB_NAME}-wal").write_bytes(b"journal")
    created = migrate_legacy_db(tmp_path, DB_NAME)
    assert created == [tmp_path / f"{DB_NAME}-wal", tmp_path / DB_NAME]
    assert (tmp_path / DB_NAME).read_bytes() == b"base"
    assert (tmp_path / f"{DB_NAME}-wal").read_bytes() == b"journal"
    assert (tmp_path / LEGACY_DB_NAME).read_bytes() == b"base"  # jamais supprimée
    assert (tmp_path / f"{LEGACY_DB_NAME}-wal").read_bytes() == b"journal"
    assert not (tmp_path / f"{DB_NAME}.copie").exists()


def test_second_migration_does_nothing(tmp_path):
    (tmp_path / LEGACY_DB_NAME).write_bytes(b"base")
    migrate_legacy_db(tmp_path, DB_NAME)
    (tmp_path / DB_NAME).write_bytes(b"nouvelle")
    assert migrate_legacy_db(tmp_path, DB_NAME) == []
    assert (tmp_path / DB_NAME).read_bytes() == b"nouvelle"


def test_no_legacy_db_means_no_copy(tmp_path):
    assert migrate_legacy_db(tmp_path, DB_NAME) == []
    assert list(tmp_path.iterdir()) == []


def test_launch_copies_the_legacy_db(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / LEGACY_DB_NAME).write_bytes(b"base")
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen()
    try:  # port occupé : le lancement s'arrête après la copie, sans servir
        assert main(["--port", str(holder.getsockname()[1]), "--data-dir", str(data)]) == 1
    finally:
        holder.close()
        close_logging()
    assert (data / DB_NAME).read_bytes() == b"base"
    assert (data / LEGACY_DB_NAME).is_file()
    log = (data / "logs" / "frugal-ai-workbench.log").read_text(encoding="utf-8")
    assert "copiée vers frugal-ai-workbench.db" in log


def test_failed_copy_leaves_nothing_behind_and_keeps_the_old_db(tmp_path, monkeypatch):
    """Disque plein ou verrou au moment de copier la base : rien de partiel ne reste."""
    from frugal_ai_workbench.store import datadir

    (tmp_path / LEGACY_DB_NAME).write_bytes(b"base")
    (tmp_path / f"{LEGACY_DB_NAME}-wal").write_bytes(b"journal")
    real_copy = datadir.shutil.copy2

    def copy_then_fail(source, target):
        if source.name == LEGACY_DB_NAME:
            raise OSError(28, "Plus de place sur le disque")
        return real_copy(source, target)

    monkeypatch.setattr(datadir.shutil, "copy2", copy_then_fail)
    with pytest.raises(OSError, match="Plus de place"):
        migrate_legacy_db(tmp_path, DB_NAME)
    assert sorted(p.name for p in tmp_path.iterdir()) == [LEGACY_DB_NAME, f"{LEGACY_DB_NAME}-wal"]


def test_launch_goes_on_when_the_copy_fails(tmp_path, monkeypatch, capsys):
    from frugal_ai_workbench.store import datadir

    data = tmp_path / "data"
    data.mkdir()
    (data / LEGACY_DB_NAME).write_bytes(b"base")

    def fail(source, target):
        raise PermissionError(13, "Fichier verrouillé")

    monkeypatch.setattr(datadir.shutil, "copy2", fail)
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen()
    port = holder.getsockname()[1]
    try:
        assert main(["--port", str(port), "--data-dir", str(data)]) == 1
    finally:
        holder.close()
        close_logging()
    err = capsys.readouterr().err
    assert "copie de l'ancienne base wavelocalai.db impossible" in err
    assert f"port {port} est occupé" in err  # le lancement a continué jusqu'au port
    assert (data / LEGACY_DB_NAME).read_bytes() == b"base"
    assert not (data / DB_NAME).exists()


def test_legacy_variable_warning_is_visible_by_default():
    """Dans un processus neuf, aux filtres par défaut de Python (hors pytest), l'avertissement
    s'affiche : un DeprecationWarning émis hors `__main__` serait masqué."""
    code = (
        "from frugal_ai_workbench.config import with_legacy_env; "
        "with_legacy_env({'WAVELOCALAI_OLLAMA_HOST': 'http://127.0.0.1:1'})"
    )
    done = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONWARNINGS": "", "PYTHONIOENCODING": "utf-8"},
        check=True,
    )
    assert "FutureWarning: La variable WAVELOCALAI_OLLAMA_HOST est dépréciée" in done.stderr
