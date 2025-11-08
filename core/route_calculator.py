import copy
import collections
import math
import heapq

class RouteCalculator:
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager

    def calculate_max_stars_route(self, start_star, donkey, step_callback=None):
        """
        Versión que genera la ruta (usando Ford-Fulkerson como antes) y luego
        simula el movimiento exactamente igual que hace calculate_economical_route:
        - simula los desplazamientos usando caminos mínimos (Dijkstra) entre pares
          consecutivos de la ruta,
        - llama a step_callback después de cada llegada para que la UI se actualice,
        - actualiza vida/energía del sim_donkey usando viajar/procesar_estrella.
        Devuelve (route, visited_count, food_log, research_log, sim_donkey).
        """
        # --- Construir la ruta objetivo usando el mismo Ford-Fulkerson previo ---
        sim_donkey = copy.deepcopy(donkey)
        if start_star not in self.graph_manager.stars:
            return [], 0, [], [], sim_donkey

        labels = list(self.graph_manager.stars.keys())
        def in_node(u): return f"{u}::in"
        def out_node(u): return f"{u}::out"
        source = out_node(start_star)
        sink = "__SINK__"

        cap = collections.defaultdict(lambda: collections.defaultdict(int))
        for u in labels:
            cap[in_node(u)][out_node(u)] = (max(1, len(labels)) if u == start_star else 1)
        for a, b, _ in self.graph_manager.connections:
            cap[out_node(a)][in_node(b)] = 1
            cap[out_node(b)][in_node(a)] = 1
        for u in labels:
            if u != start_star:
                cap[out_node(u)][sink] = 1

        # BFS para Edmonds-Karp
        def bfs_ff(res):
            parent = {}
            q = collections.deque([source])
            parent[source] = None
            while q:
                u = q.popleft()
                for v in res[u]:
                    if v not in parent and res[u][v] > 0:
                        parent[v] = u
                        if v == sink:
                            path = []
                            cur = sink
                            while cur is not None:
                                path.append(cur)
                                cur = parent[cur]
                            return list(reversed(path))
                        q.append(v)
            return None

        residual = collections.defaultdict(lambda: collections.defaultdict(int))
        for u in list(cap.keys()):
            for v, c in cap[u].items():
                residual[u][v] += c
                _ = residual[v][u]

        flows = collections.defaultdict(lambda: collections.defaultdict(int))
        while True:
            path = bfs_ff(residual)
            if not path:
                break
            bottleneck = min(residual[path[i]][path[i+1]] for i in range(len(path)-1))
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                residual[u][v] -= bottleneck
                residual[v][u] += bottleneck
                flows[u][v] += bottleneck

        # extraer paths unitarios
        def extract_one():
            stack = [source]; parent = {source: None}
            while stack:
                u = stack.pop()
                if u == sink:
                    p = []; cur = sink
                    while cur is not None:
                        p.append(cur); cur = parent[cur]
                    return list(reversed(p))
                for v in list(flows[u].keys()):
                    if flows[u][v] > 0 and v not in parent:
                        parent[v] = u; stack.append(v)
            return None

        used = []
        while True:
            p = extract_one()
            if not p: break
            for i in range(len(p)-1):
                u, v = p[i], p[i+1]; flows[u][v] -= 1
            used.append(p)

        visit_sequences = []
        for p in used:
            seq = []
            for node in p:
                if node in (source, sink): continue
                if node.endswith("::in") or node.endswith("::out"):
                    lbl = node.split("::")[0]
                    if lbl != start_star and (not seq or seq[-1] != lbl):
                        seq.append(lbl)
            if seq: visit_sequences.append(seq)

        route = [start_star]
        for seq in visit_sequences:
            for node in seq:
                if node not in route:
                    route.append(node)

        # --- Simulación del movimiento EXACTA a la de calculate_economical_route ---
        def dijkstra(start):
            dist = {start: 0.0}; prev = {}; pq = [(0.0, start)]
            while pq:
                d_u, u = heapq.heappop(pq)
                if d_u > dist.get(u, float('inf')): continue
                for v, w in self.graph_manager.get_neighbors(u):
                    nd = d_u + float(w)
                    if nd < dist.get(v, float('inf')):
                        dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
            return dist, prev

        def reconstruct(prev, src, tgt):
            if tgt not in prev and tgt != src: return None
            path = [tgt]; u = tgt
            while u != src:
                u = prev.get(u)
                if u is None: return None
                path.append(u)
            path.reverse(); return path

        # proceso inicial
        try:
            sim_donkey.procesar_estrella(start_star, self.graph_manager.stars.get(start_star, {}))
        except Exception:
            pass
        visited = {start_star}

        food_log = []
        research_log = []

        for i in range(1, len(route)):
            a = route[i-1]; b = route[i]
            dist_map, prev = dijkstra(a)
            path = reconstruct(prev, a, b)
            if path is None:
                path = [a, b]
            for j in range(1, len(path)):
                u = path[j-1]; v = path[j]
                edge_dist = self.graph_manager.get_distance(u, v)
                if edge_dist == float('inf'):
                    pa = self.graph_manager.get_star_pos(u); pb = self.graph_manager.get_star_pos(v)
                    edge_dist = math.hypot(pa[0]-pb[0], pa[1]-pb[1]) / 4.0
                try:
                    sim_donkey.viajar(edge_dist)
                except Exception:
                    pass
                try:
                    sim_donkey.procesar_estrella(v, self.graph_manager.stars.get(v, {}))
                except Exception:
                    pass
                visited.add(v)
                if step_callback:
                    try:
                        step_callback(v, sim_donkey)
                    except Exception:
                        pass
                if getattr(sim_donkey, 'vida_restante', 1) <= 0 or getattr(sim_donkey, 'energia', 1) <= 0:
                    break
            if getattr(sim_donkey, 'vida_restante', 1) <= 0 or getattr(sim_donkey, 'energia', 1) <= 0:
                break

        food_log = getattr(sim_donkey, 'food_consumption_log', []) or food_log
        research_log = getattr(sim_donkey, 'research_log', []) or research_log

        # devolver mismo formato que la ruta económica (incluye sim_donkey final)
        return route, len(visited), food_log, research_log, sim_donkey

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