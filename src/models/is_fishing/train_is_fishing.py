"""Train a fishing detection model based on AIS vessel data."""

import argparse
import itertools
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import precision_score
from sklearn.model_selection import train_test_split

from utils import db_connect

from . import config
from .model_factory import create_model, supported_model_types


def get_feature_columns():
    return list(itertools.chain.from_iterable(config.features.values()))


def get_training_data(table_name="ais_is_fishing_model.training_data_features"):
    features = get_feature_columns()
    query = "SELECT " + ", ".join(features) + ", is_fishing FROM {}".format(table_name)
    conn_input, conn_output = db_connect.alchemy_input_output_open()
    df = pd.read_sql_query(query, con=conn_input)
    db_connect.alchemy_input_output_close(conn_input, conn_output)
    return df


def split_data(df, test_size=0.2, random_state=0, stratify=True):
    X = df.drop(columns=["is_fishing"])
    y = df["is_fishing"]
    stratify_arg = y if stratify else None
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_arg,
    )


def train_model(
    X_train,
    y_train,
    model_type="random_forest",
    n_estimators=450,
    n_jobs=-1,
    random_state=0,
):
    model = create_model(
        model_type,
        n_estimators=n_estimators,
        n_jobs=n_jobs,
        random_state=random_state,
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    return {"precision_score": precision_score(y_test, y_pred)}


def save_model(model, output_path="models/model_1.pkl"):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    return str(output_path)


def load_model(model_path):
    return joblib.load(model_path)


def main():
    parser = argparse.ArgumentParser(description="Train the fishing detection model.")
    parser.add_argument(
        "--train-table",
        default="ais_is_fishing_model.training_data_features",
        help="PostgreSQL table or query for training data",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=0)
    parser.add_argument(
        "--model-type",
        choices=supported_model_types(),
        default="random_forest",
        help="Model architecture to train",
    )
    parser.add_argument("--n-estimators", type=int, default=450)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--output-model", default="models/model_1.pkl")
    args = parser.parse_args()

    if args.output_model == "models/model_1.pkl":
        args.output_model = f"models/model_{args.model_type}.pkl"

    df = get_training_data(args.train_table)
    X_train, X_test, y_train, y_test = split_data(
        df,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=True,
    )
    model = train_model(
        X_train,
        y_train,
        model_type=args.model_type,
        n_estimators=args.n_estimators,
        n_jobs=args.n_jobs,
        random_state=args.random_state,
    )
    metrics = evaluate_model(model, X_test, y_test)
    model_path = save_model(model, args.output_model)
    print(f"Saved model to {model_path}")
    print("Evaluation metrics:")
    for name, value in metrics.items():
        print(f"  {name}: {value:.4f}")


if __name__ == "__main__":
    main()
