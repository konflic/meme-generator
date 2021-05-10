import abc

from typing import List
from .models.QuoteModel import QuoteModel


class IngestorInterface(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def parse(cls, path: str) -> List[QuoteModel]:
        pass

    @classmethod
    @abc.abstractmethod
    def can_ingest(cls, path) -> bool:
        pass
