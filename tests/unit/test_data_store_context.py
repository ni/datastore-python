"""Tests for the isolated Data Store test context."""

import os
from pathlib import Path

import pytest
from utilities import DataStoreContext


def test___v2_mode___uses_v2_paths_and_restores_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base_directory = tmp_path / "v2"
    monkeypatch.setenv("NIDATASTORE_APIMODE", "before")
    monkeypatch.setenv("NIDATASTORE_V2DATASTORESETTINGS__SQLITEDATABASEPATH", "before-db")
    monkeypatch.setenv("NIDATASTORE_V2DATASTORESETTINGS__DATAFILESDIRECTORY", "before-files")
    monkeypatch.setenv("NIDATASTORE_DATASTORESETTINGS__SQLITEDATABASEPATH", "legacy-db")

    with DataStoreContext(base_directory, api_mode="v2"):
        assert os.environ["NIDATASTORE_APIMODE"] == "v2"
        assert os.environ["NIDATASTORE_V2DATASTORESETTINGS__SQLITEDATABASEPATH"] == str(
            base_directory / "DataStore.db"
        )
        assert os.environ["NIDATASTORE_V2DATASTORESETTINGS__DATAFILESDIRECTORY"] == str(
            base_directory / "DataFiles"
        )
        assert os.environ["NIDATASTORE_DATASTORESETTINGS__SQLITEDATABASEPATH"] == "legacy-db"

    assert os.environ["NIDATASTORE_APIMODE"] == "before"
    assert os.environ["NIDATASTORE_V2DATASTORESETTINGS__SQLITEDATABASEPATH"] == "before-db"
    assert os.environ["NIDATASTORE_V2DATASTORESETTINGS__DATAFILESDIRECTORY"] == "before-files"
