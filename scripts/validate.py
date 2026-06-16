"""Validate telecom source data and build a quarantined issue feed.

Checks included:
- NULL customer_id in customers
- NULL transaction_id in billings_transactions
- NULL session_id in networks_sessions
- duplicate transaction_id in billings_transactions
- duplicate session_id in networks_sessions

Quarantine output contains columns: issue_json, source, detected_at.
"""

import json
from datetime import datetime
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
CUSTOMERS_FILE = DATA_DIR / "src_customers.csv"
TRANSACTIONS_FILE = DATA_DIR / "src_billing_transactions.csv"
SESSIONS_FILE = DATA_DIR / "src_network_sessions.csv"
QUARANTINE_FILE = DATA_DIR / "quarantine.csv"


def load_source(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    return pd.read_csv(path, keep_default_na=True, na_values=["", "NULL", "NaN"])


def to_json_string(record: dict) -> str:
    return json.dumps(record, default=str, ensure_ascii=False)


def freeze_record(row: pd.Series) -> str:
    record = row.where(pd.notnull(row), None).to_dict()
    return to_json_string(record)


def detect_null_primary_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    return df[df[key].isna()]


def detect_duplicate_keys(df: pd.DataFrame, key: str) -> pd.DataFrame:
    duplicated_mask = df[key].notna() & df.duplicated(subset=[key], keep=False)
    return df[duplicated_mask]


def build_quarantine_frame() -> pd.DataFrame:
    customers = load_source(CUSTOMERS_FILE)
    transactions = load_source(TRANSACTIONS_FILE)
    sessions = load_source(SESSIONS_FILE)

    issues = []
    detected_at = datetime.utcnow().isoformat() + "Z"

    for _, row in detect_null_primary_key(customers, "customer_id").iterrows():
        issues.append({
            "issue_json": freeze_record(row),
            "source": "customers",
            "detected_at": detected_at,
        })

    for _, row in detect_null_primary_key(transactions, "transaction_id").iterrows():
        issues.append({
            "issue_json": freeze_record(row),
            "source": "billings_transactions",
            "detected_at": detected_at,
        })

    for _, row in detect_null_primary_key(sessions, "session_id").iterrows():
        issues.append({
            "issue_json": freeze_record(row),
            "source": "networks_sessions",
            "detected_at": detected_at,
        })

    duplicate_transactions = detect_duplicate_keys(transactions, "transaction_id")
    for _, row in duplicate_transactions.iterrows():
        issues.append({
            "issue_json": freeze_record(row),
            "source": "billings_transactions",
            "detected_at": detected_at,
        })

    duplicate_sessions = detect_duplicate_keys(sessions, "session_id")
    for _, row in duplicate_sessions.iterrows():
        issues.append({
            "issue_json": freeze_record(row),
            "source": "networks_sessions",
            "detected_at": detected_at,
        })

    if issues:
        return pd.DataFrame(issues)

    return pd.DataFrame(columns=["issue_json", "source", "detected_at"])


def save_quarantine(quarantine_df: pd.DataFrame) -> None:
    quarantine_df.to_csv(QUARANTINE_FILE, index=False)


def print_summary(quarantine_df: pd.DataFrame) -> None:
    if quarantine_df.empty:
        print("✅ No issues found in source files.")
        return

    counts = quarantine_df["source"].value_counts()
    print("⚠️ Validation issues found:")
    for source, count in counts.items():
        print(f"- {source}: {count} quarantined rows")
    print(f"Quarantine file written to: {QUARANTINE_FILE}")


def main() -> None:
    quarantine_df = build_quarantine_frame()
    save_quarantine(quarantine_df)
    print_summary(quarantine_df)


if __name__ == "__main__":
    main()
