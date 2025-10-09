import json

class GraphManager:
    def __init__(self):
        self.constellations = {}
        self.stars = {}
        self.connections = []
        self.star_positions = {}
        self.blocked_connections = set()

    def load_from_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)

        self.constellations = {}
        self.stars = {}
        self.connections = []
        self.star_positions = {}

        # Procesar estrellas y constelaciones
        for const_name, const_data in data.get('constelaciones', {}).items():
            self.constellations[const_name] = []
            for star_name, star_info in const_data.get('estrellas', {}).items():
                if star_name not in self.stars:
                    self.stars[star_name] = {
                        'pos': (star_info['x'], star_info['y']),
                        'constellations': [],
                        'vida_cambio': star_info.get('vida_cambio', 0),
                        'energia_costo': star_info.get('energia_costo', 0),
                        'hipergigante': star_info.get('hipergigante', False)
                    }
                self.stars[star_name]['constellations'].append(const_name)
                self.constellations[const_name].append(star_name)

            # Procesar conexiones
            for conn in const_data.get('conexiones', []):
                self.connections.append(tuple(conn))

    def toggle_connection(self, star1, star2):
        connection = tuple(sorted((star1, star2)))
        if connection in self.blocked_connections:
            self.blocked_connections.remove(connection)
        else:
            self.blocked_connections.add(connection)