"""Stage 2 - Staging Layer

This script loads raw source CSV files from `data/`, applies schema casting,
cleans the fields requested in the staging layer, and writes out deduplicated
and typed staging CSV files for use in downstream analytics.

Staging tables produced:
- stg_customers
- stg_billing
- stg_sessions

Deduplication rationale for `stg_billing`:
Keeping the most recent record for duplicate `transaction_id` values preserves
freshest source data and is safer than keeping the first-seen row or an
arbitrary duplicate. If duplicate billing rows represent corrected or updated
transactions, the latest timestamp is the best single source for downstream
financial and reconciliation logic.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
CUSTOMERS_FILE = DATA_DIR / "src_customers.csv"
TRANSACTIONS_FILE = DATA_DIR / "src_billing_transactions.csv"
SESSIONS_FILE = DATA_DIR / "src_network_sessions.csv"

STG_CUSTOMERS_FILE = DATA_DIR / "stg_customers.csv"
STG_BILLING_FILE = DATA_DIR / "stg_billing.csv"
STG_SESSIONS_FILE = DATA_DIR / "stg_sessions.csv"


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")
    return pd.read_csv(path, keep_default_na=True, na_values=["", "NULL", "NaN"])


def build_stg_customers(customers: pd.DataFrame) -> pd.DataFrame:
    df = customers.copy()

    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["name"] = df["name"].astype("string").str.title()
    df["email"] = df["email"].astype("string").str.lower()
    df["country"] = df["country"].fillna("Nigeria").astype("string")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    return df[["customer_id", "name", "email", "country", "created_at"]]


def build_stg_billing(transactions: pd.DataFrame) -> pd.DataFrame:
    df = transactions.copy()

    df["transaction_id"] = pd.to_numeric(df["transaction_id"], errors="coerce").astype("Int64")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce", utc=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["currency"] = df["currency"].astype("string")

    df = df.sort_values(["transaction_id", "transaction_date"], ascending=[True, False])
    df = df.drop_duplicates(subset=["transaction_id"], keep="first")

    return df[["transaction_id", "customer_id", "amount", "currency", "transaction_date"]]


def build_stg_sessions(sessions: pd.DataFrame) -> pd.DataFrame:
    df = sessions.copy()

    df["session_id"] = pd.to_numeric(df["session_id"], errors="coerce").astype("Int64")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce", utc=True)
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce", utc=True)
    df["data_used_mb"] = pd.to_numeric(df["data_used_mb"], errors="coerce").fillna(0.0)

    duration = (df["end_time"] - df["start_time"]).dt.total_seconds()
    df["session_duration_sec"] = duration.where(duration > 0, 0).fillna(0).astype("Int64")

    return df[["session_id", "customer_id", "start_time", "end_time", "data_used_mb", "session_duration_sec"]]


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    customers = load_csv(CUSTOMERS_FILE)
    transactions = load_csv(TRANSACTIONS_FILE)
    sessions = load_csv(SESSIONS_FILE)

    stg_customers = build_stg_customers(customers)
    stg_billing = build_stg_billing(transactions)
    stg_sessions = build_stg_sessions(sessions)

    save_dataframe(stg_customers, STG_CUSTOMERS_FILE)
    save_dataframe(stg_billing, STG_BILLING_FILE)
    save_dataframe(stg_sessions, STG_SESSIONS_FILE)

    print("✅ Staging tables generated:")
    print(f"- {STG_CUSTOMERS_FILE.name}: {len(stg_customers)} rows")
    print(f"- {STG_BILLING_FILE.name}: {len(stg_billing)} rows")
    print(f"- {STG_SESSIONS_FILE.name}: {len(stg_sessions)} rows")


if __name__ == "__main__":
    main()
