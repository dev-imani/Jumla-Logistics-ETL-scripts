import csv
import json
from pathlib import Path
from typing import Any

from etl.errors import LoadingError


class DataLoader:
    """Writes records to CSV or JSON."""

    def __init__(self, destination: Path) -> None:
        self.destination = Path(destination)
        self.extension = self.destination.suffix.lower()

        if self.extension not in {".csv", ".json"}:
            raise ValueError(
                f"Unsupported output extension: {self.extension!r}. "
                "Use .csv or .json."
            )

    def load(self, records: list[dict[str, Any]]) -> int:
        """Write records and return the number written."""
        try:
            self.destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            if self.extension == ".json":
                with self.destination.open(
                    "w", encoding="utf-8"
                ) as file:
                    json.dump(records, file, indent=4, ensure_ascii=False)

            else:
                if records:
                    # Include columns that appear in any record.
                    fieldnames = list(
                        dict.fromkeys(
                            key
                            for record in records
                            for key in record.keys()
                        )
                    )

                    with self.destination.open(
                        "w", newline="", encoding="utf-8"
                    ) as file:
                        writer = csv.DictWriter(
                            file,
                            fieldnames=fieldnames,
                            extrasaction="ignore",
                        )
                        writer.writeheader()
                        writer.writerows(records)
                else:
                    # Create an empty output file for zero records.
                    self.destination.write_text(
                        "", encoding="utf-8"
                    )

            return len(records)

        except (OSError, csv.Error, TypeError, ValueError) as exc:
            raise LoadingError(
                f"Could not write to {self.destination}: {exc}"
            ) from exc