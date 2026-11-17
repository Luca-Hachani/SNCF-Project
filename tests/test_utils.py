import pandas as pd

from sncf_project.utils import load_dataset


def test_load_dataset_success(tmp_path):
    directory = tmp_path / "sub"
    directory.mkdir()
    path = directory / "test.csv"
    path.write_text("COLUMN1;COLUMN2\nJohn;Doe", encoding="utf-8")
    df = load_dataset(str(path), sep=";")
    assert df is not None
    assert len(df) == 1
    assert "COLUMN1" in df.columns


def test_load_dataset_not_found():
    df = load_dataset("fichier_imaginaire.csv", sep=";")
    assert df is None


def test_load_dataset_empty_data(tmp_path):
    directory = tmp_path / "sub"
    directory.mkdir()
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    df = load_dataset(str(path), sep=";")
    assert df is None


def test_load_dataset_parser_error(tmp_path):
    directory = tmp_path / "sub"
    directory.mkdir()
    path = tmp_path / "parsing_error.csv"
    path.write_text('COLUMN1;COLUMN2\n"John;Doe;18', encoding="utf-8")
    df = load_dataset(str(path), sep=";")
    assert df is None


def test_load_dataset_permission_error(monkeypatch):
    monkeypatch.setattr(
        pd,
        "read_csv",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            PermissionError("Permission denied")
        ),
    )
    df = load_dataset("secret.csv", sep=";")
    assert df is None
