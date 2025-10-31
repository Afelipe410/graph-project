class Donkey:
    def __init__(self, salud, edad, energia, pasto):
        self.salud_map = {"excelente": 4, "buena": 3, "regular": 2, "mala": 1, "moribundo": 0}
        self.salud_str_map = {v: k for k, v in self.salud_map.items()}

        self.salud = self.salud_map.get(salud.lower(), 2) # Default a 'regular' si no se encuentra
        self.edad = edad
        self.energia = energia
        self.pasto = pasto
        self.vida_restante = self.calcular_vida_inicial()
        # Logs para el reporte de acciones del burro
        self.food_consumption_log = []
        self.research_log = []
    def calcular_vida_inicial(self):
        # Lógica de ejemplo para calcular la vida inicial.
        # La vida es una combinación de edad y salud.
        # Un burro más viejo o con peor salud tiene menos "vida" (distancia total que puede recorrer).
        base_vida = (100 - self.edad) * 5 # La edad es un factor principal
        salud_modificador = (self.salud + 1) * 1.5 # La salud da un bonus
        return base_vida * salud_modificador

    def get_salud_str(self):
        return self.salud_str_map.get(self.salud, "desconocido")

    def procesar_estrella(self, star_label, estrella_data):
        """
        Simula las acciones del burro en una estrella: comer e investigar.
        """
        # 1. Comer si la energía es menor al 50%
        if self.energia < 50 and self.pasto > 0:
            energia_por_kg = 0
            if self.salud == self.salud_map["excelente"]:
                energia_por_kg = 5
            elif self.salud == self.salud_map["regular"]:
                energia_por_kg = 3
            elif self.salud == self.salud_map["mala"]:
                energia_por_kg = 2

            if energia_por_kg > 0:
                # El burro intenta comer para llegar al 100% de energía.
                energia_necesaria = 100 - self.energia
                kg_necesarios = energia_necesaria / energia_por_kg

                # Limita los kg a comer por el pasto disponible.
                kg_a_comer = min(kg_necesarios, self.pasto)

                # El tiempo total en la estrella es 20 (valor asumido). 50% para comer.
                tiempo_para_comer = 10
                tiempo_por_kg = estrella_data.get('tiempo_para_comer', 1)
                
                # Limita los kg a comer por el tiempo disponible.
                kg_posibles_por_tiempo = tiempo_para_comer / tiempo_por_kg
                kg_a_comer = min(kg_a_comer, kg_posibles_por_tiempo)

                # Actualizar valores
                self.pasto -= kg_a_comer
                self.energia += kg_a_comer * energia_por_kg
                if self.energia > 100: self.energia = 100

                # Registrar el consumo de pasto si fue significativo
                if kg_a_comer > 0.01:
                    self.food_consumption_log.append({
                        "star": star_label, "amount_kg": kg_a_comer
                    })

        # 2. Investigar con el tiempo restante
        # Asumimos 10 unidades de tiempo para investigar.
        tiempo_para_investigar = 10
        tiempo_por_unidad_invest = estrella_data.get('tiempo_para_comer', 1) # "X" tiempo
        costo_energia_invest = estrella_data.get('costo_energia_invest', 1) # "Y" cantidad

        # Calcular cuántas veces se puede aplicar el costo de energía
        unidades_investigadas = tiempo_para_investigar / tiempo_por_unidad_invest
        self.energia -= unidades_investigadas * costo_energia_invest

        # Aplicar efectos de la investigación sobre salud y vida
        health_effect = estrella_data.get('health_effect', 0)
        life_effect = estrella_data.get('life_effect', 0)

        self.salud += health_effect
        # Asegurar que la salud se mantenga en el rango válido (0-4)
        self.salud = max(self.salud_map["moribundo"], min(self.salud_map["excelente"], self.salud))

        self.vida_restante += life_effect

        # Registrar la investigación si hubo algún efecto
        if unidades_investigadas > 0.01 or health_effect != 0 or life_effect != 0:
            self.research_log.append({
                "star": star_label, "units_investigated": unidades_investigadas,
                "health_change": health_effect, "life_change": life_effect
            })

    def viajar(self, distancia):
        self.vida_restante -= distancia
        # El viaje también consume energía
        self.energia -= distancia * 0.1 # Ejemplo: 0.1 de energía por unidad de distancia
        if self.energia < 0: self.energia = 0