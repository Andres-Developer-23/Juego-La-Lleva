from abc import ABC, abstractmethod


class Renderizable(ABC):
    @abstractmethod
    def renderizar(self, pantalla):
        pass
