from utils import load_dataset


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
