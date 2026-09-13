"""Interfaz que define el contrato para objetos que pueden renderizarse en pantalla."""

from abc import ABC, abstractmethod


class Renderizable(ABC):
    """Clase abstracta que define los métodos que debe implementar cualquier objeto renderizable."""

    @abstractmethod
    def renderizar(self, pantalla):
        """Renderiza el objeto en la pantalla.

        Args:
            pantalla: Superficie de pygame donde se dibujará el objeto.
        """
        pass
