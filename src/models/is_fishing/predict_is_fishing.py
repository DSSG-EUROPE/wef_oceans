"""Predict fishing labels for AIS vessel data using a trained model."""

import argparse
import itertools
from pathlib import Path

import joblib
import pandas as pd

from utils import db_connect, db_manipulate

from . import config


def get_feature_columns():
    return list(itertools.chain.from_iterable(config.features.values()))


def load_model(model_path="models/model_1.pkl"):
    return joblib.load(model_path)


def predict_dataframe(model, df):
    features = get_feature_columns()
    missing = [f for f in features if f not in df.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    predictions = pd.Series(model.predict_proba(df[features])[:, 1], name="is_fishing")
    return pd.concat(
        [df.reset_index(drop=True), predictions.reset_index(drop=True)], axis=1
    )


def predict_table(
    read_query,
    model_path,
    output_schema,
    output_table,
    chunk_size=10000,
    parallel=True,
):
    model = load_model(model_path)

    def predict_chunk(chunk):
        return predict_dataframe(model, chunk)

    db_manipulate.loop_chunks(
        read_query,
        predict_chunk,
        output_schema,
        output_table,
        size_chunk=chunk_size,
        parallel=parallel,
    )


def main():
    parser = argparse.ArgumentParser(description="Run fishing predictions on AIS data.")
    parser.add_argument(
        "--read-query",
        default="SELECT * FROM ais_is_fishing_model.test_data_features;",
        help="SQL query to read input data",
    )
    parser.add_argument("--model-path", default="models/model_1.pkl")
    parser.add_argument("--output-schema", default="ais_is_fishing_model")
    parser.add_argument("--output-table", default="test_data_predictions")
    parser.add_argument("--chunk-size", type=int, default=10000)
    parser.add_argument("--no-parallel", action="store_true")
    args = parser.parse_args()

    predict_table(
        args.read_query,
        args.model_path,
        args.output_schema,
        args.output_table,
        chunk_size=args.chunk_size,
        parallel=not args.no_parallel,
    )


if __name__ == "__main__":
    main()
