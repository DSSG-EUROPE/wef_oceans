import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from src.models.is_fishing.predict_is_fishing import (
    get_feature_columns,
    predict_dataframe,
)


def make_synthetic_predict_data(n=20):
    features = get_feature_columns()
    return pd.DataFrame({feature: np.random.rand(n) for feature in features})


def test_predict_dataframe_adds_is_fishing_column():
    df = make_synthetic_predict_data(20)
    target = np.random.choice([0, 1], size=20)
    model = RandomForestClassifier(n_estimators=10, random_state=0)
    model.fit(df, target)

    result = predict_dataframe(model, df)
    assert "is_fishing" in result.columns
    assert len(result) == len(df)
    assert result["is_fishing"].between(0, 1).all()


def test_predict_dataframe_raises_when_features_missing():
    df = pd.DataFrame({"latitude": [0.0], "longitude": [0.0]})
    target = np.array([0, 1])
    model = RandomForestClassifier(n_estimators=10, random_state=0)
    # train on a full feature set so predict_proba exists
    full_df = make_synthetic_predict_data(2)
    model.fit(full_df, np.array([0, 1]))

    with pytest.raises(ValueError, match="Missing required features"):
        predict_dataframe(model, df)
