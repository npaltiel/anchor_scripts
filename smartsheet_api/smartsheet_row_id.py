#!/usr/bin/env python3
"""
Export Smartsheet Row IDs to an Excel file.

Creates: smartsheet_row_ids.xlsx in the current folder.

Env/.env variables required:
  SMARTSHEET_ACCESS_TOKEN
  SMARTSHEET_SHEET_ID
"""

import os
import math
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Any

BASE = "https://api.smartsheet.com/2.0"


def get_env_vars():
    load_dotenv()  # reads .env if present
    token = os.getenv("SMARTSHEET_ACCESS_TOKEN")
    sheet_id = os.getenv("SMARTSHEET_SHEET_ID")
    if not token:
        raise SystemExit("Missing SMARTSHEET_ACCESS_TOKEN (set in .env or env).")
    if not sheet_id:
        raise SystemExit("Missing SMARTSHEET_SHEET_ID (set in .env or env).")
    return token, sheet_id


def _request(method: str, url: str, headers: Dict[str, str], **kwargs) -> requests.Response:
    """HTTP with simple retries for 429/5xx."""
    max_retries = 6
    backoff = 1.0
    for _ in range(max_retries):
        resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        if resp.status_code in (429, 500, 502, 503, 504):
            time.sleep(backoff)
            backoff = min(backoff * 2, 16)
            continue
        resp.raise_for_status()
        return resp
    resp.raise_for_status()
    return resp


def get_sheet_info(sheet_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Get sheet to learn which column is primary (for a helpful label)."""
    url = f"{BASE}/sheets/{sheet_id}"
    params = {"include": "ownerInfo"}  # avoid pulling rows here
    return _request("GET", url, headers=headers, params=params).json()


def get_all_rows(sheet_id: str, headers: dict) -> list[dict]:
    """
    Fetch all rows using the Get Sheet endpoint with pagination.
    Docs: GET /sheets/{sheetId}?pageSize=&page=
    """
    rows = []
    page_size = 500
    page = 1
    while True:
        url = f"{BASE}/sheets/{sheet_id}"
        # include=rowNumbers helps if you want r['rowNumber']
        params = {"pageSize": page_size, "page": page, "include": "rowNumbers"}
        resp = _request("GET", url, headers=headers, params=params).json()

        page_rows = resp.get("rows", [])
        rows.extend(page_rows)

        total = resp.get("totalRowCount") or resp.get("totalCount")
        if total:
            last_page = math.ceil(total / page_size)
            if page >= last_page:
                break
        else:
            if len(page_rows) < page_size:
                break

        page += 1

    return rows


def extract_row_records(rows: list[dict], primary_col_id: int, phone_col_id: int) -> list[dict]:
    records = []
    for r in rows:
        primary_value = None
        phone_value = None
        for c in r.get("cells", []):
            if c.get("columnId") == primary_col_id:
                primary_value = c.get("displayValue") or c.get("value")
            elif c.get("columnId") == phone_col_id:
                phone_value = c.get("displayValue") or c.get("value")

        records.append({
            "Row ID": r["id"],
            "Row Number": r.get("rowNumber"),
            "Primary Column": primary_value,
            "Phone": phone_value,
            "Created": r.get("createdAt")  # <-- new
        })
    return records


def main():
    token, sheet_id = get_env_vars()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("Fetching sheet info…")
    sheet = get_sheet_info(sheet_id, headers)

    primary_col_id = next((col["id"] for col in sheet["columns"] if col.get("primary")), None)
    phone_col_id = next((col["id"] for col in sheet["columns"] if col["title"].lower() == "phone"), None)

    if not primary_col_id:
        raise SystemExit("Could not determine primary column ID.")
    if not phone_col_id:
        raise SystemExit("Could not find a column named 'Phone'.")

    print("Fetching all rows…")
    rows = get_all_rows(sheet_id, headers)
    print(f"Found {len(rows)} rows.")

    print("Building records…")
    records = extract_row_records(rows, primary_col_id, phone_col_id)

    print("Writing Excel…")
    df = pd.DataFrame(records)
    output = "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Salesforce\\SmartsheetIDs.xlsx"
    df.to_excel(output, index=False)
    print(f"Done ✅ Wrote {len(df)} rows to {output}")


if __name__ == "__main__":
    main()
