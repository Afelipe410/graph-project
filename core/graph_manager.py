from PyQt6.QtGui import QColor
import random
import json
import math
from pathlib import Path

class GraphManager:
    def __init__(self):
        self.stars = {}
        self.connections = set()
        self.blocked_connections = set()
        self.constellation_colors = {}
        self.initial_donkey_data = {}
        # parámetros del tablero / mapeo (ahora en cm)
        self.um_min_x = 0
        self.um_min_y = 0
        self.um_range_x = 1
        self.um_range_y = 1
        self.um_scale = 1.0  # px por cm
        self.um_padding = 40
        self.um_target_w = 800
        self.um_target_h = 600

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
        self.reset()

        # Abrir y parsear JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Mapear id -> label para resolver conexiones
        id_to_label = {}
        for const in data.get("constellations", []):
            const_name = const.get("name", "SinNombre")
            if const_name not in self.constellation_colors:
                self.constellation_colors[const_name] = self._generate_random_color()
            for s in const.get("starts", []):
                sid = s.get("id")
                label = s.get("label")
                if sid is not None and label:
                    id_to_label[sid] = label

        # Recolectar posiciones crudas (cm) para normalizar/escalar
        raw_positions = []
        stars_raw = []
        for const in data.get("constellations", []):
            for s in const.get("starts", []):
                coord = s.get("coordenates", {})
                raw_x = coord.get("x", 0)
                raw_y = coord.get("y", 0)
                raw_positions.append((raw_x, raw_y))
                stars_raw.append((const.get("name", "SinNombre"), s, raw_x, raw_y))

        # Determinar rangos en cm; asegurar mínimo 200 cm en cada eje
        if raw_positions:
            xs = [p[0] for p in raw_positions]
            ys = [p[1] for p in raw_positions]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x = min_y = 0
            max_x = max_y = 1

        range_x = max_x - min_x
        range_y = max_y - min_y
        if range_x < 200:
            max_x = min_x + 200
            range_x = 200
        if range_y < 200:
            max_y = min_y + 200
            range_y = 200

        self.um_min_x = min_x
        self.um_min_y = min_y
        self.um_range_x = range_x
        self.um_range_y = range_y

        padding = self.um_padding
        target_w, target_h = self.um_target_w, self.um_target_h
        range_x = range_x if range_x != 0 else 1
        range_y = range_y if range_y != 0 else 1
        scale_x = (target_w - 2 * padding) / range_x
        scale_y = (target_h - 2 * padding) / range_y
        scale = min(scale_x, scale_y)

        # Factor deseado para separar visualmente las estrellas (gráfico solamente).
        desired_separation_factor = 1.6

        self.um_scale = scale
        self.um_padding = padding

        # Construir estrellas y conexiones
        pos_map = {}  # key -> list of labels (para detectar overlaps)

        # Centro del área util (en píxeles) para aplicar el "estiramiento" radial
        useful_w = target_w - 2 * padding
        useful_h = target_h - 2 * padding
        center_px = padding + useful_w / 2.0
        center_py = padding + useful_h / 2.0

        # Primero calcular las posiciones base (sin factor) para evaluar límites
        base_positions = []
        for _, s, raw_x, raw_y in stars_raw:
            if not s.get("label"):
                base_positions.append(None)
                continue
            norm_x = (raw_x - min_x) / (range_x if range_x != 0 else 1)
            norm_y = (raw_y - min_y) / (range_y if range_y != 0 else 1)
            base_px = padding + norm_x * useful_w
            base_py = padding + norm_y * useful_h
            base_positions.append((s.get("label"), base_px, base_py))

        # Determinar el factor máximo admisible para que ninguna estrella salga del área útil
        allowed_max = float('inf')
        for entry in base_positions:
            if entry is None:
                continue
            _, base_px, base_py = entry
            # para X: si base > center, max_f = (right - center)/(base - center)
            #         si base < center, max_f = (center - left)/(center - base)
            if base_px != center_px:
                if base_px > center_px:
                    max_fx = (padding + useful_w - center_px) / (base_px - center_px)
                else:
                    max_fx = (center_px - padding) / (center_px - base_px)
                allowed_max = min(allowed_max, max_fx)
            if base_py != center_py:
                if base_py > center_py:
                    max_fy = (padding + useful_h - center_py) / (base_py - center_py)
                else:
                    max_fy = (center_py - padding) / (center_py - base_py)
                allowed_max = min(allowed_max, max_fy)

        # Si por alguna razón allowed_max es muy pequeño o infinito, usar al menos 1.0
        if not math.isfinite(allowed_max) or allowed_max < 1.0:
            allowed_max = 1.0

        # Elegir factor final (no exceder el deseado ni allowed_max)
        separation_factor = min(desired_separation_factor, allowed_max)

        # Construir posiciones finales aplicando separation_factor y clamp de seguridad
        for const_name, s, raw_x, raw_y in stars_raw:
            label = s.get("label")
            if not label:
                continue
            # posición base en píxeles dentro del área útil (sin separación extra)
            norm_x = (raw_x - min_x) / (range_x if range_x != 0 else 1)
            norm_y = (raw_y - min_y) / (range_y if range_y != 0 else 1)
            base_px = padding + norm_x * useful_w
            base_py = padding + norm_y * useful_h

            # aplicar separación radial respecto al centro (solo visual)
            px = center_px + (base_px - center_px) * separation_factor
            py = center_py + (base_py - center_py) * separation_factor

            # clamp final para asegurar que queden dentro del área visible
            px = max(padding, min(padding + useful_w, px))
            py = max(padding, min(padding + useful_h, py))

            self.stars[label] = {
                "id": s.get("id"),
                "pos": (px, py),
                "um_pos": (raw_x, raw_y),
                "radius": s.get("radius", 0.5),
                "tiempo_para_comer": s.get("timeToEat", 1),
                "costo_energia_invest": s.get("amountOfEnergy", 1),
                "hypergiant": s.get("hypergiant", False),
                "constellation": const_name,
                "overlap": False
            }

            key = (round(raw_x, 6), round(raw_y, 6))
            pos_map.setdefault(key, []).append(label)

        # Marcar overlaps (misma coordenada cm usada por >1 estrella)
        for key, labels in pos_map.items():
            if len(labels) > 1:
                for lab in labels:
                    if lab in self.stars:
                        self.stars[lab]['overlap'] = True

        # Añadir conexiones (undirected)
        for const in data.get("constellations", []):
            for s in const.get("starts", []):
                label = s.get("label")
                if not label:
                    continue
                for link in s.get("linkedTo", []):
                    other_label = id_to_label.get(link.get("starId"))
                    if other_label:
                        a, b = tuple(sorted((label, other_label)))
                        dist = link.get("distance", 0)
                        self.connections.add((a, b, dist))

        # Datos globales para UI
        self.initial_donkey_data = {
            "burroenergiaInicial": data.get("burroenergiaInicial"),
            "estadoSalud": data.get("estadoSalud"),
            "pasto": data.get("pasto"),
            "startAge": data.get("startAge"),
            "deathAge": data.get("deathAge")
        }

    def get_distance(self, star1_label, star2_label):
        """Devuelve la distancia entre dos estrellas si existe la conexión; inf si no existe."""
        if star1_label == star2_label:
            return 0.0
        a, b = tuple(sorted((star1_label, star2_label)))
        for s1, s2, dist in self.connections:
            if s1 == a and s2 == b:
                try:
                    return float(dist)
                except Exception:
                    return float('inf')
        return float('inf')

    def get_neighbors(self, star_label):
        """Devuelve lista de tuplas (neighbor_label, distance) para la estrella dada."""
        neighbors = []
        for s1, s2, dist in self.connections:
            if s1 == star_label:
                neighbors.append((s2, float(dist)))
            elif s2 == star_label:
                neighbors.append((s1, float(dist)))
        return neighbors

    def get_star_pos(self, star_label):
        """Devuelve la posición (x,y) en pixeles de la estrella o (0,0) si no existe."""
        data = self.stars.get(star_label)
        if not data:
            return (0, 0)
        return data.get("pos", (0, 0))