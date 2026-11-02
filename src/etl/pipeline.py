from etl.errors import ETLError
from etl.extractors import DataExtractor
from etl.loader import DataLoader
from etl.summary import RunSummary
from etl.transformer import DataTransformer


class Pipeline:
    """Runs extraction, transformation and loading."""

    def __init__(
        self,
        extractor: DataExtractor,
        transformer: DataTransformer,
        loader: DataLoader,
    ) -> None:
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def run(self) -> RunSummary:
        summary = RunSummary(source=self.extractor.name)

        try:
            records = self.extractor.extract()
            summary.extracted = len(records)

            valid_records = self.transformer.transform(records)

            summary.valid = len(valid_records)
            summary.rejected = len(
                self.transformer.rejected_records
            )

            summary.loaded = self.loader.load(valid_records)

        except ETLError as exc:
            summary.errors.append(str(exc))

        return summary