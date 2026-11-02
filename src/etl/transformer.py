import re
from copy import deepcopy
from typing import Any

from etl.errors import TransformationError


class DataTransformer:
    """Validates and normalises records."""

    POSITIVE_FIELDS = {
        "quantity",
        "unit_price",
        "price",
        "amount",
        "total",
        "total_amount",
    }

    def __init__(
        self,
        required_fields: list[str],
        positive_fields: list[str] | None = None,
        email_fields: list[str] | None = None,
    ) -> None:
        self.required_fields = required_fields
        self.positive_fields = set(
            positive_fields
            if positive_fields is not None
            else self.POSITIVE_FIELDS
        )
        self.email_fields = set(email_fields or ["email"])
        self.rejected_records: list[dict[str, Any]] = []

    def validate(self, record: dict[str, Any]) -> list[str]:
        """Return all validation errors for one record."""
        reasons: list[str] = []

        for field in self.required_fields:
            value = record.get(field)

            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
                reasons.append(f"Missing required field: {field}")

        for field, value in record.items():
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()

            if field.lower() in self.email_fields or field.lower().endswith(
                "_email"
            ):
                if not isinstance(value, str) or not re.fullmatch(
                    r"[^@\s]+@[^@\s]+\.[^@\s]+", value
                ):
                    reasons.append(f"Invalid email: {field}")

            if field in self.positive_fields:
                try:
                    number = float(value)
                    if number <= 0:
                        reasons.append(
                            f"{field} must be greater than zero"
                        )
                except (TypeError, ValueError):
                    reasons.append(f"{field} must be numeric")

        return reasons

    def clean(self, record: dict[str, Any]) -> dict[str, Any]:
        """Return a normalised copy of a valid record."""
        cleaned = deepcopy(record)

        def normalise(value: Any, key: str = "") -> Any:
            if isinstance(value, dict):
                return {
                    child_key: normalise(child_value, child_key)
                    for child_key, child_value in value.items()
                }

            if isinstance(value, list):
                return [normalise(item, key) for item in value]

            if isinstance(value, str):
                value = value.strip()

                if key.lower() in self.email_fields or key.lower().endswith(
                    "_email"
                ):
                    return value.lower()

                if key.lower() == "city":
                    return value.title()

                if key in self.positive_fields:
                    number = float(value)
                    return (
                        int(number)
                        if number.is_integer()
                        else number
                    )

                return value

            return value

        cleaned = normalise(cleaned)

        # Calculate a useful order total when the fields are present.
        if (
            "quantity" in cleaned
            and "unit_price" in cleaned
        ):
            quantity = cleaned["quantity"]
            price = cleaned["unit_price"]

            if isinstance(quantity, (int, float)) and isinstance(
                price, (int, float)
            ):
                cleaned["total_amount"] = quantity * price

        # Flatten the city from the JSONPlaceholder user address.
        address = cleaned.get("address")
        if isinstance(address, dict) and "city" in address:
            cleaned["city"] = address["city"]

        return cleaned

    def transform(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Transform valid records and retain rejected records."""
        self.rejected_records = []
        valid_records: list[dict[str, Any]] = []

        for index, record in enumerate(records, start=1):
            try:
                if not isinstance(record, dict):
                    self.rejected_records.append({
                        "record": record,
                        "reasons": ["Record must be a dictionary"],
                    })
                    continue

                reasons = self.validate(record)

                if reasons:
                    self.rejected_records.append({
                        "record": deepcopy(record),
                        "reasons": reasons,
                    })
                    continue

                valid_records.append(self.clean(record))

            except (TypeError, ValueError, KeyError) as exc:
                self.rejected_records.append({
                    "record": deepcopy(record),
                    "reasons": [
                        f"Transformation failed for record {index}: {exc}"
                    ],
                })
            except Exception as exc:
                raise TransformationError(
                    f"Unexpected transformation failure at "
                    f"record {index}: {exc}"
                ) from exc

        return valid_records