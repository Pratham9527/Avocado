import io
import json
import uuid
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler


def _encode_categorical_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """Label-encode supported categorical columns if they exist."""
    candidate_columns = [
        "gaming_platform_top1",
        "social_platform_top1",
        "ott_top1",
        "content_creation_freq",
    ]
    cat_cols = [col for col in candidate_columns if col in df.columns]
    encoders: Dict[str, LabelEncoder] = {}

    if not cat_cols:
        return df, encoders

    for col in cat_cols:
        encoder = LabelEncoder()
        df[col] = encoder.fit_transform(df[col])
        encoders[col] = encoder

    return df, encoders


def _scale_numeric_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], StandardScaler]:
    """Standard-scale numeric columns if any exist."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        return df, numeric_cols, StandardScaler()

    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    return df, numeric_cols, scaler


def run_clustering_pipeline(file_bytes: io.BytesIO, k_opt: int = 3) -> Dict[str, object]:
    """
    Execute the clustering pipeline given a CSV file-like object.

    Args:
        file_bytes: In-memory file-like object for a CSV file.
        k_opt: Optimal number of clusters (default=3).

    Returns:
        A dictionary containing number_of_clusters and a cluster summary mapping.
    """
    df = pd.read_csv(file_bytes)

    if "name" not in df.columns:
        raise ValueError("Dataset must contain a 'name' column for person identification.")

    df, _ = _encode_categorical_columns(df)
    df, numeric_cols, _ = _scale_numeric_columns(df)

    if not numeric_cols:
        raise ValueError("Dataset must contain at least one numeric column for clustering.")

    X = df.select_dtypes(include=[np.number])
    kmeans_model = KMeans(n_clusters=k_opt, random_state=42, n_init=10)
    df["Cluster"] = kmeans_model.fit_predict(X)

    clusters_summary: Dict[str, List[str]] = {}
    for cluster_id in sorted(df["Cluster"].unique()):
        persons_in_cluster = df[df["Cluster"] == cluster_id]["name"].tolist()
        clusters_summary[f"Cluster {cluster_id}"] = persons_in_cluster

    return {
        "number_of_clusters": int(k_opt),
        "clusters": clusters_summary,
        "raw_clusters": df.to_dict(orient="records"),
    }


def serialize_clusters_to_json(clustering_result: Dict[str, object]) -> str:
    """Serialize clustering results to a JSON string."""
    payload = {
        "number_of_clusters": clustering_result["number_of_clusters"],
        "clusters": clustering_result["clusters"],
    }
    return json.dumps(payload, indent=2)


def generate_task_id() -> str:
    """Generate a unique identifier for background clustering tasks."""
    return uuid.uuid4().hex

