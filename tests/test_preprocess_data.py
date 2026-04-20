import pandas as pd

from src.models.is_fishing.preprocess_data import label_encode_data


def test_label_encode_data_encodes_string_columns():
    df = pd.DataFrame(
        {
            "color": ["red", "blue", "red"],
            "size": ["S", "M", "L"],
            "value": [10, 20, 30],
        }
    )

    encode_cols, encoded = label_encode_data(df.copy())

    assert set(encode_cols) == {"color", "size"}
    assert encoded["value"].tolist() == [10, 20, 30]
    assert encoded["color"].nunique() == 2
    assert encoded["size"].nunique() == 3


def test_label_encode_data_with_only_numeric_columns_returns_same_dataframe():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})

    encode_cols, encoded = label_encode_data(df.copy())

    assert list(encode_cols) == []
    pd.testing.assert_frame_equal(encoded, df)
