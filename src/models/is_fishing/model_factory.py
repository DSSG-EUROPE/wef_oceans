"""Build classification models for the fishing detection pipeline."""

from inspect import signature

from sklearn.ensemble import (
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression

_MODEL_REGISTRY = {
    "random_forest": RandomForestClassifier,
    "gradient_boosting": GradientBoostingClassifier,
    "logistic_regression": LogisticRegression,
    "extra_trees": ExtraTreesClassifier,
}


def supported_model_types():
    return list(_MODEL_REGISTRY.keys())


def create_model(model_type="random_forest", **kwargs):
    model_type = model_type.lower()
    if model_type not in _MODEL_REGISTRY:
        raise ValueError(
            f"Unsupported model type '{model_type}'. Supported types: {supported_model_types()}"
        )

    model_cls = _MODEL_REGISTRY[model_type]
    sig = signature(model_cls)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return model_cls(**valid_kwargs)
