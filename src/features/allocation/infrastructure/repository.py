from abc import ABC, abstractmethod

from src.features.allocation.domain import model
from src.features.allocation.infrastructure import models


# class AbstractRepository(ABC):
#     def __init__(self):
#         self.seen = set()

#     def add(self, product: model.Product):
#         self._add(product)
#         self.seen.add(product)

#     def get(self, sku) -> model.Product:
#         product = self._get(sku)
#         if product:
#             self.seen.add(product)
#         return product

#     def get_by_batchref(self, batchref) -> model.Product:
#         product = self._get_by_batchref(batchref)
#         if product:
#             self.seen.add(product)
#         return product

#     @abstractmethod
#     def _add(self, product: model.Product):
#         raise NotImplementedError

#     @abstractmethod
#     def _get(self, sku) -> model.Product:
#         raise NotImplementedError

#     @abstractmethod
#     def _get_by_batchref(self, batchref) -> model.Product:
#         raise NotImplementedError
