import os
import csv

from .IngestorInterface import IngestorInterface
from .models.QuoteModel import QuoteModel


class CSVIngestor(IngestorInterface):

    def can_ingest(cls, path) -> bool:
        if not os.path.exists(path):
            return False

    def parse(self, path):
        result = []

        with open(path, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            next(reader)

            for row in reader:
                result.append(QuoteModel(**row))

        return result
