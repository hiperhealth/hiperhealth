"""Utility functions for file parsing and directory management."""

import csv
import json
import os

from typing import Any, Dict, Tuple


def ensure_upload_dir(path: str) -> None:
    """Ensure upload directory exists, create if needed."""
    os.makedirs(path, exist_ok=True)


def parse_wearable_file(path: str) -> Tuple[int, Dict[str, Any]]:
    """Parse wearable CSV/JSON file and extract basic statistics.

    For CSV: counts rows and computes numeric column averages for
    columns like 'hr', 'heart_rate', 'bpm', 'steps'.
    For JSON: if array of records, returns length and averages;
    if dict, returns 1 and keys.

    Parameters
    ----------
    path : str
        File path to parse (CSV or JSON).

    Returns
    -------
    Tuple[int, Dict[str, Any]]
        Tuple of (row_count, summary_dict) where summary_dict contains
        numeric averages and any errors encountered.
    """
    _, ext = os.path.splitext(path.lower())
    summary: Dict[str, Any] = {}
    rows = 0
    try:
        if ext == '.csv':
            with open(path, newline='', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                sums: Dict[str, float] = {}
                counts: Dict[str, int] = {}
                for r in reader:
                    rows += 1
                    for k, v in r.items():
                        if v is None or v == '':
                            continue
                        lk = k.lower()
                        if lk in ('hr', 'heart_rate', 'bpm', 'steps'):
                            try:
                                val = float(v)
                                sums[lk] = sums.get(lk, 0.0) + val
                                counts[lk] = counts.get(lk, 0) + 1
                            except ValueError:
                                pass
                for k in sums:
                    summary[f'{k}_avg'] = (
                        sums[k] / counts[k] if counts[k] else None
                    )
        elif ext == '.json':
            with open(path, encoding='utf-8') as fh:
                j = json.load(fh)
                if isinstance(j, list):
                    rows = len(j)
                    # try numeric fields
                    sums = {}
                    counts = {}
                    for item in j:
                        if not isinstance(item, dict):
                            continue
                        for k, v in item.items():
                            lk = k.lower()
                            if lk in ('hr', 'heart_rate', 'bpm', 'steps'):
                                try:
                                    val = float(v)
                                    sums[lk] = sums.get(lk, 0.0) + val
                                    counts[lk] = counts.get(lk, 0) + 1
                                except ValueError:
                                    pass
                    for k in sums:
                        summary[f'{k}_avg'] = (
                            sums[k] / counts[k] if counts[k] else None
                        )
                elif isinstance(j, dict):
                    # not an array; store top-level length as 1
                    rows = 1
                    summary['keys'] = list(j.keys())
    except Exception as e:
        summary['error'] = str(e)

    return rows, summary
