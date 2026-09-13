class PuntajeService:
    def __init__(self):
        self.tiempos_lleva = {}

    def registrar_lleva(self, id_jugador, tiempo):
        if id_jugador not in self.tiempos_lleva:
            self.tiempos_lleva[id_jugador] = 0
        self.tiempos_lleva[id_jugador] += tiempo

    def obtener_ganador(self):
        if not self.tiempos_lleva:
            return None
        return min(self.tiempos_lleva, key=self.tiempos_lleva.get)

    def reiniciar(self):
        self.tiempos_lleva.clear()
