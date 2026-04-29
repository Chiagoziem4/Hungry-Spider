from __future__ import annotations

import csv
import json
from pathlib import Path

from spider.storage.repository import ExtractedDataRepository, serialise_records
from spider.utils.validators import ensure_parent_dir



def export_data(
    *,
    format: str = "json",
    output_path: str = "data/exports/output",
    limit: int | None = None,
    job_id: int | None = None,
) -> str:
    repo = ExtractedDataRepository()
    records = serialise_records(repo.list_extracted(limit=limit, job_id=job_id))
    destination = ensure_parent_dir(f"{output_path}.{format}")

    if format == "json":
        destination.write_text(json.dumps(records, indent=2), encoding="utf-8")
    elif format == "jsonl":
        destination.write_text(
            "\n".join(json.dumps(row) for row in records),
            encoding="utf-8",
        )
    elif format == "csv":
        fieldnames = sorted({key for row in records for key in row.keys()}) or ["url"]
        with destination.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in records:
                writer.writerow(row)
    else:
        raise ValueError(f"Unsupported export format: {format}")

    return str(Path(destination).resolve())
