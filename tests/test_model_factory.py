from src.models.is_fishing.model_factory import create_model, supported_model_types


def test_supported_model_types_include_expected_models():
    types = supported_model_types()
    assert "random_forest" in types
    assert "gradient_boosting" in types
    assert "logistic_regression" in types
    assert "extra_trees" in types


def test_create_model_returns_correct_classifier():
    rf = create_model("random_forest", n_estimators=10, random_state=0)
    assert rf.__class__.__name__ == "RandomForestClassifier"

    gb = create_model("gradient_boosting", n_estimators=10, random_state=0)
    assert gb.__class__.__name__ == "GradientBoostingClassifier"

    lr = create_model("logistic_regression", random_state=0, max_iter=100)
    assert lr.__class__.__name__ == "LogisticRegression"

    et = create_model("extra_trees", n_estimators=10, random_state=0)
    assert et.__class__.__name__ == "ExtraTreesClassifier"


def test_create_model_rejects_unknown_type():
    try:
        create_model("unsupported_model")
    except ValueError as exc:
        assert "Unsupported model type" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported model type")
