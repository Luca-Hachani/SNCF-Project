import pandas as pd
import pytest

from sncf_project.utils import find_closest_stations, load_dataset

""" Test for load_dataset """


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


""" Test for find_closest_stations """


@pytest.fixture
def sample_df_stations() -> pd.DataFrame:
    """Create a sample for testing"""
    return pd.DataFrame(
        {
            "display_name": ["GRENOBLE", "ANNECY", "LYON-PART-DIEU"],
            "Gare de départ": ["GRENOBLE", "ANNECY", "LYON PART DIEU"],
            "lon": [5.714309, 6.121833, 4.860201],
            "lat": [45.191284, 45.902211, 45.760541],
        }
    )


def test_find_closest_station_default(
    sample_df_stations: pd.DataFrame,
) -> None:
    """Return the top_1 closest station from the city Grenoble"""
    echirolles_coords = [5.7147828, 45.1441357]

    result = find_closest_stations(sample_df_stations, echirolles_coords, 1)

    assert isinstance(result, list)
    assert result == ["GRENOBLE"]


def test_find_closest_station_top_n(sample_df_stations: pd.DataFrame) -> None:
    """Return the top_3 closest station from the city Grenoble"""
    echirolles_coords = [5.7147828, 45.1441357]

    result = find_closest_stations(
        sample_df_stations, echirolles_coords, top_n=3
    )

    assert result == ["GRENOBLE", "ANNECY", "LYON PART DIEU"]


def test_find_closest_station_top_n_exceding(
    sample_df_stations: pd.DataFrame,
) -> None:
    """Return the top_n closest station from the city Grenoble without
    exceding the size of the sample_df_stations"""
    echirolles_coords = [5.7147828, 45.1441357]

    result = find_closest_stations(
        sample_df_stations, echirolles_coords, top_n=10
    )

    assert len(result) == len(sample_df_stations)
    assert result[0] == "GRENOBLE"


def test_find_closest_stations_empty_df() -> None:
    """Empty df_stations"""
    sample_df_stations = pd.DataFrame(
        columns=["display_name", "lon", "lat", "Gare de départ"]
    )
    echirolles_coords = [5.7147828, 45.1441357]
    result = find_closest_stations(
        sample_df_stations, echirolles_coords, top_n=1
    )

    assert result == []


def test_find_closest_stations_missing_columns() -> None:
    """Missing columns in dataframe"""
    bad_df = pd.DataFrame({"display_name": ["RENNES"], "lon": [45.0]})
    with pytest.raises(ValueError, match="Missing required columns"):
        find_closest_stations(bad_df, [5.7147828, 45.1441357])


def test_find_closest_stations_invalid_coords(
    sample_df_stations: pd.DataFrame,
) -> None:
    """Invalid value for city coords"""
    with pytest.raises(ValueError, match="two valid coordinates"):
        find_closest_stations(sample_df_stations, [5.7147828])

    with pytest.raises(ValueError, match="two valid coordinates"):
        find_closest_stations(sample_df_stations, [5.7147828, float("nan")])


def test_find_closest_stations_invalid_top_n(
    sample_df_stations: pd.DataFrame,
) -> None:
    """Invalid value for top_n"""
    with pytest.raises(ValueError, match="Top_n must be > 1"):
        find_closest_stations(
            sample_df_stations, [5.7147828, 45.1441357], top_n=0
        )
