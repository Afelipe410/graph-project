import copy

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
            neighbors = []
            # Encontrar vecinos no visitados desde la estrella actual
            for star1, star2, distance in self.graph_manager.connections:
                neighbor = None
                if star1 == current_star_label and star2 not in visited_stars:
                    neighbor = star2
                elif star2 == current_star_label and star1 not in visited_stars:
                    neighbor = star1
                
                if neighbor:
                    neighbors.append((neighbor, distance))

            # Ordenar vecinos por distancia (el más cercano primero)
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
        Calcula una ruta que intenta maximizar las estrellas visitadas con un gasto eficiente.
        Es una heurística que en cada paso elige el "mejor" vecino.
        El "mejor" vecino es aquel que, tras el viaje y las acciones en la estrella,
        deja al burro en el mejor estado posible (más vida y energía).
        """
        sim_donkey = copy.deepcopy(donkey)
        current_star_label = start_star_label
        visited_stars = {current_star_label}
        route = [current_star_label]

        # Procesar la estrella inicial
        initial_star_data = self.graph_manager.stars[current_star_label]
        sim_donkey.procesar_estrella(initial_star_data)

        print(f"Iniciando cálculo 'Económico' desde '{start_star_label}'. Vida: {sim_donkey.vida_restante:.1f}, Energía: {sim_donkey.energia:.1f}%")

        while sim_donkey.vida_restante > 0 and sim_donkey.energia > 0:
            neighbors = self.graph_manager.get_neighbors(current_star_label)
            possible_next_steps = []

            for neighbor_label, distance in neighbors:
                if neighbor_label in visited_stars:
                    continue

                # Simular el viaje a este vecino
                temp_donkey = copy.deepcopy(sim_donkey)
                temp_donkey.viajar(distance)

                # Si el burro sobrevive al viaje...
                if temp_donkey.vida_restante > 0 and temp_donkey.energia > 0:
                    # Simular acciones en la estrella de destino
                    neighbor_star_data = self.graph_manager.stars[neighbor_label]
                    temp_donkey.procesar_estrella(neighbor_star_data)

                    # Calcular una "puntuación" para esta opción.
                    # Queremos maximizar vida y energía, y minimizar distancia.
                    # Un valor más alto es mejor.
                    score = (temp_donkey.vida_restante * 0.6) + (temp_donkey.energia * 0.4) - (distance * 0.2)
                    possible_next_steps.append((score, neighbor_label, distance, temp_donkey))

            if not possible_next_steps:
                print("No hay más movimientos posibles. Fin de la ruta.")
                break

            # Elegir el vecino con la mejor puntuación
            possible_next_steps.sort(key=lambda x: x[0], reverse=True)
            best_score, best_neighbor, dist, final_donkey_state = possible_next_steps[0]

            # Confirmar el movimiento
            current_star_label = best_neighbor
            visited_stars.add(current_star_label)
            route.append(current_star_label)
            sim_donkey = final_donkey_state
            print(f"-> Viajando a '{current_star_label}' (Dist: {dist}). Estado: Vida {sim_donkey.vida_restante:.1f}, Energía {sim_donkey.energia:.1f}%")

        return route, len(route)