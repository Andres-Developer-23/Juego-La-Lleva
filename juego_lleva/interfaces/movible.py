from abc import ABC, abstractmethod


class Movible(ABC):
    @abstractmethod
    def mover(self, teclas=None):
        pass

    @abstractmethod
    def obtener_posicion(self):
        pass

    @abstractmethod
    def obtener_rectangulo(self):
        pass
