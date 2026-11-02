from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests

from etl.errors import ExtractionError


class DataExtractor(ABC):
    """Common interface for every data source."""

    def __init__(self, source: str, name: str | None = None) -> None:
        self.source = source
        self.name = name or source

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]:
        """Return records from the source."""
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r}, source={self.source!r})"
        )


class CSVExtractor(DataExtractor):
    """Reads records from a CSV file."""

    def extract(self) -> list[dict[str, Any]]:
        path = Path(self.source)

        try:
            with path.open("r", newline="", encoding="utf-8-sig") as file:
                reader = csv.DictReader(file)

                if not reader.fieldnames:
                    raise ExtractionError(
                        f"CSV file has no header: {path}"
                    )

                return [dict(row) for row in reader]

        except ExtractionError:
            raise
        except (OSError, UnicodeError, csv.Error) as exc:
            raise ExtractionError(
                f"Could not read CSV source {path}: {exc}"
            ) from exc


class APIExtractor(DataExtractor):
    """Reads records from a JSON HTTP endpoint."""

    def __init__(
        self,
        source: str,
        name: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        super().__init__(source, name)
        self.timeout = timeout

    def __repr__(self) -> str:
        return (
            f"APIExtractor(name={self.name!r}, "
            f"source={self.source!r}, timeout={self.timeout!r})"
        )

    def extract(self) -> list[dict[str, Any]]:
        try:
            response = requests.get(
                self.source,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise ExtractionError(
                    "API response must contain a JSON list."
                )

            if not all(isinstance(record, dict) for record in data):
                raise ExtractionError(
                    "Every API record must be a JSON object."
                )

            return data

        except ExtractionError:
            raise
        except (requests.RequestException, ValueError) as exc:
            raise ExtractionError(
                f"Could not extract API data from "
                f"{self.source}: {exc}"
            ) from exc