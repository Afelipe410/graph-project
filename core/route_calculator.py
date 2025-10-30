import copy
import heapq

class RouteCalculator:
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager

    def calculate_max_stars_route(self, start_star, donkey):
        """
        Calcula la ruta que maximiza el número de estrellas visitadas antes de que el burro muera.
        Utiliza un algoritmo voraz (greedy): en cada paso, viaja a la estrella vecina más cercana
        que no ha sido visitada, siempre que el burro pueda sobrevivir al viaje.
        """
        sim_donkey = copy.deepcopy(donkey) # Usamos una copia para no alterar el original
        current_star_label = start_star
        visited_stars = {current_star_label}
        route = [current_star_label]

        print(f"Iniciando cálculo 'Die Hard' desde '{start_star}'. Vida inicial del burro: {sim_donkey.vida_restante}")

        while True:
            # Usar get_neighbors para obtener solo vecinos no bloqueados
            neighbors_with_distances = self.graph_manager.get_neighbors(current_star_label)
            
            # Encontrar vecinos no visitados desde la estrella actual
            neighbors = [(n, d) for n, d in neighbors_with_distances if n not in visited_stars]

            # Ordenar vecinos por distancia (el más cercano primero) para el algoritmo voraz
            neighbors.sort(key=lambda x: x[1])

            next_star_found = False
            for next_star_label, distance in neighbors:
                # ¿Puede el burro sobrevivir al viaje?
                if sim_donkey.vida_restante > distance:
                    sim_donkey.viajar(distance) # Viajar a la estrella
                    current_star_label = next_star_label
                    visited_stars.add(current_star_label)
                    route.append(current_star_label)
                    next_star_found = True
                    print(f"Viajando a '{next_star_label}' (distancia: {distance}). Vida restante: {sim_donkey.vida_restante}")
                    break # Salir del bucle de vecinos y empezar de nuevo desde la nueva estrella
            
            # Si no se encontró una siguiente estrella a la que se pueda viajar, terminar la ruta.
            if not next_star_found:
                print("No se pueden visitar más estrellas. Fin de la ruta.")
                break

        return route, len(route)

    def calculate_economical_route(self, start_star_label, donkey):
        """
        Ahora usa Dijkstra para encontrar caminos de coste mínimo desde la posición actual.
        Estrategia:
        - Repetidamente calcula distancias mínimas desde la estrella actual (Dijkstra).
        - Selecciona la estrella no visitada con menor coste total (ruta más corta).
        - Reconstruye el camino a esa estrella y simula el viaje paso a paso,
          aplicando sim_donkey.viajar(...) y sim_donkey.procesar_estrella(...).
        - Para mantener compatibilidad devuelve (route, len(route), food_log, research_log).
        """
        sim_donkey = copy.deepcopy(donkey)
        current = start_star_label
        visited = {current}
        route = [current]

        # Si la estrella de inicio no existe, devolver vacío compatible
        if current not in self.graph_manager.stars:
            return [], 0, sim_donkey.food_consumption_log, sim_donkey.research_log

        # Procesar la estrella inicial (como hacía la versión anterior)
        try:
            initial_star_data = self.graph_manager.stars[current]
            sim_donkey.procesar_estrella(current, initial_star_data)
        except Exception:
            pass

        print(f"Iniciando cálculo 'Económico' (Dijkstra) desde '{start_star_label}'. Vida: {getattr(sim_donkey, 'vida_restante', 0):.1f}, Energía: {getattr(sim_donkey, 'energia', 0):.1f}")

        def dijkstra(start):
            dist = {start: 0.0}
            prev = {}
            pq = [(0.0, start)]
            while pq:
                d_u, u = heapq.heappop(pq)
                if d_u > dist.get(u, float('inf')):
                    continue
                for v, w in self.graph_manager.get_neighbors(u):
                    nd = d_u + float(w)
                    if nd < dist.get(v, float('inf')):
                        dist[v] = nd
                        prev[v] = u
                        heapq.heappush(pq, (nd, v))
            return dist, prev

        def reconstruct_path(prev, src, tgt):
            if tgt not in prev and tgt != src:
                return None
            path = [tgt]
            u = tgt
            while u != src:
                u = prev.get(u)
                if u is None:
                    return None
                path.append(u)
            path.reverse()
            return path

        while True:
            # calcular distancias mínimas desde la estrella actual
            dist, prev = dijkstra(current)

            # candidatos: nodos no visitados alcanzables
            candidates = [(d, node) for node, d in dist.items() if node not in visited]
            if not candidates:
                print("No hay estrellas no visitadas alcanzables. Fin de la ruta.")
                break

            # elegir el más cercano (menor coste)
            candidates.sort(key=lambda x: x[0])
            next_node = None
            for dcost, node in candidates:
                path = reconstruct_path(prev, current, node)
                if path is None:
                    continue
                # probar simular el viaje paso a paso con una copia temporal
                temp = copy.deepcopy(sim_donkey)
                can_reach = True
                for i in range(1, len(path)):
                    a = path[i-1]; b = path[i]
                    edge_dist = self.graph_manager.get_distance(a, b)
                    if edge_dist == float('inf'):
                        # fallback: distancia euclídea/4 para no bloquear la simulación
                        pa = self.graph_manager.get_star_pos(a)
                        pb = self.graph_manager.get_star_pos(b)
                        edge_dist = (((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2) ** 0.5) / 4.0
                    temp.viajar(edge_dist)
                    if getattr(temp, 'vida_restante', 1) <= 0 or getattr(temp, 'energia', 1) <= 0:
                        can_reach = False
                        break
                if can_reach:
                    next_node = node
                    next_path = path
                    break

            if not next_node:
                print("No se puede alcanzar ninguna estrella restante sin morir. Fin de la ruta.")
                break

            # mover sim_donkey a lo largo de next_path, aplicando viajar y procesar_estrella
            for i in range(1, len(next_path)):
                a = next_path[i-1]; b = next_path[i]
                edge_dist = self.graph_manager.get_distance(a, b)
                if edge_dist == float('inf'):
                    pa = self.graph_manager.get_star_pos(a)
                    pb = self.graph_manager.get_star_pos(b)
                    edge_dist = (((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2) ** 0.5) / 4.0
                sim_donkey.viajar(edge_dist)
                if b not in route:
                    route.append(b)
                if getattr(sim_donkey, 'vida_restante', 1) <= 0 or getattr(sim_donkey, 'energia', 1) <= 0:
                    print("El burro ha muerto durante el trayecto.")
                    return route, len(route), sim_donkey.food_consumption_log, sim_donkey.research_log

            # al llegar a next_node, procesar la estrella
            try:
                star_info = self.graph_manager.stars.get(next_node, {})
                sim_donkey.procesar_estrella(next_node, star_info)
            except Exception:
                pass

            visited.add(next_node)
            current = next_node

            # condición de parada si ya visitó todas las estrellas
            if len(visited) >= len(self.graph_manager.stars):
                break

        return route, len(route), sim_donkey.food_consumption_log, sim_donkey.research_log