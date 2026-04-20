import numpy as np
import pandas as pd

from src.models.is_fishing import train_is_fishing


def make_synthetic_training_data(n=100):
    features = train_is_fishing.get_feature_columns()
    data = {feature: np.random.rand(n) for feature in features}
    data["is_fishing"] = np.random.choice([0, 1], size=n)
    return pd.DataFrame(data)


def test_train_model_succeeds_and_saves(tmp_path):
    df = make_synthetic_training_data(100)
    X_train, X_test, y_train, y_test = train_is_fishing.split_data(
        df, test_size=0.2, random_state=0, stratify=False
    )

    model = train_is_fishing.train_model(
        X_train, y_train, n_estimators=10, n_jobs=1, random_state=0
    )

    assert hasattr(model, "predict")
    metrics = train_is_fishing.evaluate_model(model, X_test, y_test)
    assert "precision_score" in metrics

    output_path = tmp_path / "model.pkl"
    saved_path = train_is_fishing.save_model(model, output_path)
    loaded_model = train_is_fishing.load_model(saved_path)
    assert loaded_model.predict(X_test).shape[0] == len(X_test)
