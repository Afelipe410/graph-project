import json
import random
from PyQt6.QtGui import QColor

class GraphManager:
    def __init__(self):
        self.stars = {}
        self.connections = set()
        self.blocked_connections = set()
        self.constellation_colors = {}
        self.initial_donkey_data = {}

    def _generate_random_color(self):
        """Genera un color aleatorio brillante."""
        return QColor(random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def reset(self):
        """Limpia todos los datos del grafo."""
        self.stars.clear()
        self.connections.clear()
        self.blocked_connections.clear()
        self.constellation_colors.clear()
        self.initial_donkey_data.clear()

    def load_from_json(self, file_path):
        """Carga y procesa los datos de las constelaciones desde un archivo JSON con la nueva estructura."""
        self.reset()
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Guardar datos iniciales del burro
        self.initial_donkey_data = {
            'energia': data.get('burroenergiaInicial', 100),
            'salud': data.get('estadoSalud', 'excelente'),
            'pasto': data.get('pasto', 100),
            'edad': data.get('startAge', 10)
        }

        id_to_label_map = {}

        # --- Primer paso: Registrar todas las estrellas y sus propiedades ---
        for constellation in data['constellations']:
            constellation_name = constellation['name']
            
            # Asignar un color a la constelación si no lo tiene
            if constellation_name not in self.constellation_colors:
                self.constellation_colors[constellation_name] = self._generate_random_color()

            for star_data in constellation.get('starts', []):
                star_label = star_data['label']
                star_id = star_data['id']
                id_to_label_map[star_id] = star_label

                if star_label not in self.stars:
                    self.stars[star_label] = {
                        'id': star_id,
                        'pos': (star_data['coordenates']['x'] * 4, star_data['coordenates']['y'] * 4), # Escalado
                        'hipergigante': star_data.get('hypergiant', False),
                        'constelaciones': set(),
                        'vida_cambio': 0, # Placeholder, se puede modificar desde la UI
                        'tiempo_para_comer': star_data.get('timeToEat', 1),
                        'costo_energia_invest': star_data.get('amountOfEnergy', 1)
                    }
                
                self.stars[star_label]['constelaciones'].add(constellation_name)

        # --- Segundo paso: Crear las conexiones usando el mapa de ID a Label ---
        for constellation in data['constellations']:
            for star_data in constellation.get('starts', []):
                star1_label = star_data['label']
                
                for link in star_data.get('linkedTo', []):
                    star2_id = link['starId']
                    distance = link['distance']

                    if star2_id in id_to_label_map:
                        star2_label = id_to_label_map[star2_id]
                        
                        # Evitar duplicados y auto-conexiones
                        if star1_label != star2_label:
                            # Guardar la conexión ordenada para evitar (A,B) y (B,A)
                            connection_tuple = tuple(sorted((star1_label, star2_label)))
                            self.connections.add(connection_tuple + (distance,))

    def get_distance(self, star1_label, star2_label):
        """Obtiene la distancia entre dos estrellas."""
        search_tuple = tuple(sorted((star1_label, star2_label)))
        for conn in self.connections:
            if (conn[0], conn[1]) == search_tuple:
                return conn[2]
        return float('inf') # Retorna infinito si no hay conexión directa

    def get_neighbors(self, star_label):
        """Obtiene una lista de vecinos y distancias para una estrella dada."""
        neighbors = []
        for s1, s2, distance in self.connections:
            if s1 == star_label:
                neighbors.append((s2, distance))
            elif s2 == star_label:
                neighbors.append((s1, distance))
        return neighbors

    def get_star_pos(self, star_label):
        return self.stars.get(star_label, {}).get('pos')