from pathlib import Path

from etl import (APIExtractor,CSVExtractor,DataLoader,DataTransformer,Pipeline,RunSummary,)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def build_pipelines() -> list[Pipeline]:
    """Create pipelines from configuration."""

    configurations = [
        {
            "name": "Orders CSV",
            "extractor": CSVExtractor(str(DATA_DIR / "orders.csv"), name="Orders CSV",),
            "required_fields": [
                "order_id",
                "city",
                "quantity",
                "unit_price_kes",
            ],
            "positive_fields": ["quantity", "unit_price_kes"],
            "destination": OUTPUT_DIR / "orders_clean.csv",
        },
        {
            "name": "Users API",
            "extractor": APIExtractor(
                "https://jsonplaceholder.typicode.com/users",
                name="Users API",
            ),
            "required_fields": ["id", "name", "email"],
            "destination": OUTPUT_DIR / "users_clean.json",
        },
        {
            "name": "Missing CSV demonstration",
            "extractor": CSVExtractor( str(DATA_DIR / "missing_orders.csv"),name="Missing CSV demonstration",),
            "required_fields": [
                "order_id",
                "city",
                "quantity",
                "unit_price_kes",
            ],
            "positive_fields": ["quantity", "unit_price_kes"],
            "destination": OUTPUT_DIR / "missing_orders.csv",
        },
        {
            "name": "Invalid URL demonstration",
            "extractor": APIExtractor(
                "not-a-valid-url",
                name="Invalid URL demonstration",
            ),
            "required_fields": ["id", "name", "email"],
            "destination": OUTPUT_DIR / "invalid_users.json",
        },
    ]

    pipelines: list[Pipeline] = []

    for config in configurations:
        transformer = DataTransformer(required_fields=config["required_fields"],positive_fields=config.get("positive_fields"), )

        loader = DataLoader(config["destination"])

        pipelines.append(
            Pipeline(extractor=config["extractor"], transformer=transformer, loader=loader,) )

    return pipelines


def main() -> None:
    summaries: list[RunSummary] = []

    for pipeline in build_pipelines():
        print(f"\nRunning {pipeline.extractor!r}")

        summary = pipeline.run()
        summaries.append(summary)

        # Preserve rejected records for inspection.
        rejected = pipeline.transformer.rejected_records

        if rejected:
            rejected_path = (
                OUTPUT_DIR
                / f"{pipeline.extractor.name.lower().replace(' ', '_')}"
                / "rejected_records.json"
            )

            try:
                DataLoader(rejected_path).load(rejected)
            except Exception as exc:
                summary.errors.append(
                    f"Could not save rejected records: {exc}"
                )

        print(summary.report())
        print("-" * 45)

    total = RunSummary(source="TOTAL")

    for summary in summaries:
        total.extracted += summary.extracted
        total.valid += summary.valid
        total.rejected += summary.rejected
        total.loaded += summary.loaded
        total.errors.extend(
            f"{summary.source}: {error}"
            for error in summary.errors
        )

    print("\nEXECUTION SUMMARY")
    print(total.report())


if __name__ == "__main__":
    main()