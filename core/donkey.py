class Donkey:
    def __init__(self, salud, edad, energia, pasto):
        self.salud_map = {"excelente": 4, "buena": 3, "regular": 2, "mala": 1, "moribundo": 0, "muerto": -1}
        self.salud_str_map = {v: k for k, v in self.salud_map.items()}
        
        self.salud = self.salud_map.get(salud.lower(), 2) # Default a 'regular' si no se encuentra
        self.edad = edad
        self.energia = energia
        self.pasto = pasto
        self.vida_restante = self.calcular_vida_inicial()

    def calcular_vida_inicial(self):
        # Lógica de ejemplo para calcular la vida inicial.
        # Puedes ajustar esta fórmula según los requisitos.
        return (100 - self.edad) * 10

    def get_salud_str(self):
        return self.salud_str_map.get(self.salud, "desconocido")

    def comer(self, kg_pasto, estrella):
        if self.energia < 50:
            if self.salud == self.salud_map["excelente"]:
                self.energia += kg_pasto * 5
            elif self.salud == self.salud_map["regular"]:
                self.energia += kg_pasto * 3
            elif self.salud == self.salud_map["mala"]:
                self.energia += kg_pasto * 2
            
            if self.energia > 100:
                self.energia = 100
            self.pasto -= kg_pasto

    def investigar(self, estrella):
        self.energia -= estrella['energia_costo']
        self.vida_restante += estrella['vida_cambio']

    def viajar(self, distancia):
        self.vida_restante -= distancia