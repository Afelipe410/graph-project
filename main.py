import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QComboBox, QLabel, QSpinBox, QMessageBox
from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtMultimedia import QSoundEffect
from core.graph_manager import GraphManager
from ui.graph_widget import GraphWidget
from core.graph_manager import GraphManager
from core.donkey import Donkey
from core.route_calculator import RouteCalculator
import math

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NASA: Misión Burro Espacial")
        self.setGeometry(100, 100, 1200, 800)

        self.graph_manager = GraphManager()
        self.route_calculator = RouteCalculator(self.graph_manager)
        
        # --- Animación ---
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_step)
        self.animation_path = []
        self.animation_step_index = 0
        self.donkey_death_sound = QSoundEffect()
        self.donkey_death_sound.setSource(QUrl.fromLocalFile("assets/donkey_death.wav"))
        self.current_donkey = None

        # --- Layout Principal ---
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # --- Panel Izquierdo (Controles) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        
        # --- Carga de Archivo ---
        self.load_button = QPushButton("Cargar Constelaciones (JSON)")
        self.load_button.clicked.connect(self.load_constellations)
        left_layout.addWidget(self.load_button)

        # --- Configuración del Burro ---
        donkey_group = QGroupBox("Configuración del Burro")
        donkey_layout = QFormLayout()

        self.start_star_combo = QComboBox()
        self.health_combo = QComboBox()
        self.health_combo.addItems(["excelente", "buena", "regular", "mala", "moribundo"])
        self.age_input = QSpinBox()
        self.age_input.setRange(1, 100)
        self.energy_input = QSpinBox()
        self.energy_input.setRange(0, 100)
        self.grass_input = QSpinBox()
        self.grass_input.setRange(0, 1000)

        # crear combo para seleccionar constelación
        self.constellation_combo = QComboBox()
        # conectar explícitamente pasando el índice para evitar ambigüedades de sobrecarga
        self.constellation_combo.currentIndexChanged.connect(lambda idx: self.on_constellation_selected(idx))
        # asegurar que sean interactuables y visibles
        self.constellation_combo.setEnabled(True)
        self.constellation_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.constellation_combo.setMinimumWidth(200)

        self.start_star_combo.setEnabled(True)
        self.start_star_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.start_star_combo.setMinimumWidth(200)
        # conectar cambio en estrella para depuración y acción (centrar burro) — pasar índice explícito
        self.start_star_combo.currentIndexChanged.connect(lambda idx: self.on_start_star_changed(idx))

        donkey_layout.addRow("Constelacion:", self.constellation_combo)
        donkey_layout.addRow("Estrella de Inicio:", self.start_star_combo)
        donkey_layout.addRow("Salud:", self.health_combo)
        donkey_layout.addRow("Edad:", self.age_input)
        donkey_layout.addRow("BurroEnergía (%):", self.energy_input)
        donkey_layout.addRow("Pasto en Bodega (kg):", self.grass_input)

        donkey_group.setLayout(donkey_layout)
        left_layout.addWidget(donkey_group)

        # --- Controles de Simulación ---
        sim_group = QGroupBox("Calcular Rutas")
        sim_layout = QVBoxLayout()

        self.calc_die_hard_button = QPushButton("Calcular Ruta de Resistencia")
        self.calc_die_hard_button.clicked.connect(self.calculate_die_hard_route)
        self.calc_economical_button = QPushButton("Calcular Ruta Económica")
        self.calc_economical_button.clicked.connect(self.calculate_economical_route)

        sim_layout.addWidget(self.calc_die_hard_button)
        sim_layout.addWidget(self.calc_economical_button)
        sim_group.setLayout(sim_layout)
        left_layout.addWidget(sim_group)

        left_layout.addStretch() # Empuja todo hacia arriba

        # --- Widget del Grafo (Panel Derecho) ---
        self.graph_widget = GraphWidget(self.graph_manager)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.graph_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def load_constellations(self):
        """Abre un diálogo para seleccionar y cargar un archivo JSON."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de constelaciones",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        if file_path:
            try:
                self.graph_manager.load_from_json(file_path)
                print(f"Archivo cargado exitosamente: {file_path}")
                self.update_ui_after_load()
                # Forzar al widget del grafo a redibujarse con los nuevos datos
                self.graph_widget.update()
            except Exception as e:
                print(f"Error al cargar o procesar el archivo JSON: {e}")

    def update_ui_after_load(self):
        """Actualiza los componentes de la UI que dependen de los datos del grafo."""
        # poblar combo de constelaciones (manteniendo el orden cargado)
        consts = list(self.graph_manager.constellation_colors.keys())
        self.constellation_combo.clear()
        if consts:
            self.constellation_combo.addItems(consts)
            # seleccionar la primera y poblar estrellas según la constelación
            self.constellation_combo.setCurrentIndex(0)
            # seleccionar la primera y poblar estrellas según la constelación
            self.constellation_combo.setCurrentIndex(0)
            print(f"[DEBUG] update_ui_after_load: consts={consts}")
            # llamar explícito con índice 0 para forzar la actualización del combo de estrellas
            self.on_constellation_selected(0)
        else:
            self.start_star_combo.clear()
        
        # Pre-llenar la UI con los datos del burro del JSON
        donkey_data = self.graph_manager.initial_donkey_data
        if donkey_data:
            health_str = donkey_data.get('salud', 'excelente').lower()
            if health_str in [self.health_combo.itemText(i) for i in range(self.health_combo.count())]:
                self.health_combo.setCurrentText(health_str)
            
            self.age_input.setValue(donkey_data.get('edad', 10))
            self.energy_input.setValue(donkey_data.get('energia', 100))
            self.grass_input.setValue(donkey_data.get('pasto', 100))

    def calculate_die_hard_route(self):
        """Crea un burro con los datos de la UI y calcula la ruta 'Die Hard'."""
        start_star = self.start_star_combo.currentText()
        if not start_star:
            QMessageBox.warning(self, "Advertencia", "Por favor, carga un archivo de constelaciones y selecciona una estrella de inicio.")
            return

        # Crear instancia del burro desde la UI
        donkey = Donkey(
            salud=self.health_combo.currentText(),
            edad=self.age_input.value(),
            energia=self.energy_input.value(),
            pasto=self.grass_input.value()
        )

        # Guardar burro actual para la animación/simulación
        self.current_donkey = donkey

        # Calcular la ruta
        route, stars_visited_count = self.route_calculator.calculate_max_stars_route(start_star, donkey)

        # Mostrar resultados (puedes mejorar esto, por ejemplo, en un diálogo)
        self.graph_widget.set_highlighted_route(route)
        QMessageBox.information(self, "Ruta de Resistencia Calculada", 
                                f"Se visitaron {stars_visited_count} estrellas.\n"
                                f"Ruta: {' -> '.join(route)}")

    def calculate_economical_route(self):
        """Crea un burro y calcula la ruta económica, luego inicia la animación."""
        start_star = self.start_star_combo.currentText()
        if not start_star:
            QMessageBox.warning(self, "Advertencia", "Por favor, carga un archivo y selecciona una estrella de inicio.")
            return

        donkey = Donkey(
            salud=self.health_combo.currentText(),
            edad=self.age_input.value(),
            energia=self.energy_input.value(),
            pasto=self.grass_input.value()
        )

        # Guardar burro actual para la animación/simulación
        self.current_donkey = donkey

        route, stars_visited_count = self.route_calculator.calculate_economical_route(start_star, donkey)

        self.graph_widget.set_highlighted_route(route)
        QMessageBox.information(self, "Ruta Económica Calculada",
                                f"Se visitarán {stars_visited_count} estrellas.\n"
                                f"Ruta: {' -> '.join(route)}\n\n"
                                "Iniciando simulación del recorrido...")
        
        self.start_animation(route)

    def start_animation(self, route):
        if len(route) < 2:
            return

        self.animation_path = route
        self.animation_step_index = 0
        # Asegurar que la posición inicial del burro esté establecida en el widget
        if route:
            self.graph_widget.donkey_pos = self.graph_manager.get_star_pos(route[0])
        self.animation_timer.start(30) # Actualizar cada 30 ms para una animación fluida

    def animate_step(self):
        # Índices de la estrella de origen y destino para el segmento actual
        start_node_idx = self.animation_step_index
        end_node_idx = self.animation_step_index + 1

        if end_node_idx >= len(self.animation_path):
            self.animation_timer.stop()
            # Si la ruta se completó, el burro no murió
            QMessageBox.information(self, "Simulación Terminada", "¡El burro completó la ruta con éxito!")
            return

        start_pos = self.graph_manager.get_star_pos(self.animation_path[start_node_idx])
        end_pos = self.graph_manager.get_star_pos(self.animation_path[end_node_idx])
        current_pos = self.graph_widget.donkey_pos

        dx = end_pos[0] - current_pos[0]
        dy = end_pos[1] - current_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)

        # Mover el burro un pequeño paso hacia el destino
        if distance > 2: # Si no hemos llegado aún
            speed = 2 # Píxeles por paso
            self.graph_widget.donkey_pos = (current_pos[0] + (dx / distance) * speed,
                                            current_pos[1] + (dy / distance) * speed)
        else: # Llegamos a la estrella
            self.graph_widget.donkey_pos = end_pos
            self.animation_step_index += 1 # Preparar para el siguiente segmento

            # Simulación: aplicar coste del viaje y acciones en la estrella
            if self.current_donkey:
                # Usar la distancia real entre estrellas (valor del JSON)
                travel_distance = self.graph_manager.get_distance(self.animation_path[start_node_idx], self.animation_path[end_node_idx])
                # Si no hay distancia almacenada, estimar por píxeles (fallback)
                if travel_distance == float('inf'):
                    travel_distance = math.sqrt((start_pos[0]-end_pos[0])**2 + (start_pos[1]-end_pos[1])**2) / 4.0

                # Burro viaja (consume vida y energía)
                self.current_donkey.viajar(travel_distance)

                # Procesar la estrella destino (comer/investigar)
                star_info = self.graph_manager.stars.get(self.animation_path[end_node_idx], {})
                estrella_data = {
                    'tiempo_para_comer': star_info.get('tiempo_para_comer', 1),
                    'costo_energia_invest': star_info.get('costo_energia_invest', 1)
                }
                self.current_donkey.procesar_estrella(estrella_data)

                # Si el burro murió o se quedó sin energía, detener y reproducir sonido
                if getattr(self.current_donkey, 'vida_restante', 1) <= 0 or getattr(self.current_donkey, 'energia', 1) <= 0:
                    self.animation_timer.stop()
                    try:
                        self.donkey_death_sound.play()
                    except Exception:
                        pass
                    QMessageBox.critical(self, "El burro ha muerto", "El burro no pudo completar la ruta y ha muerto en el viaje.")
                    return

        self.graph_widget.update()

    def on_constellation_selected(self, index=None):
        # obtener nombre de la constelación desde el índice (si se pasó) o desde el texto actual
        if isinstance(index, int):
            name = self.constellation_combo.itemText(index)
        else:
            name = self.constellation_combo.currentText()

        # depuración mínima: imprime en consola lo seleccionado
        print(f"[DEBUG] Constelación seleccionada: {repr(name)}")

        # limpiar y rellenar combo de estrellas
        self.start_star_combo.clear()
        if not name:
            return

        # coincidir exacto quitando posibles espacios
        name = str(name).strip()
        stars = [label for label, data in self.graph_manager.stars.items() if str(data.get('constellation', '')).strip() == name]
        stars.sort()
        print(f"[DEBUG] Estrellas encontradas para '{name}': {stars}")
        if stars:
            self.start_star_combo.addItems(stars)
            self.start_star_combo.setCurrentIndex(0)
            # si quieres centrar burro en la primer estrella seleccionada
            first = self.start_star_combo.currentText()
            if first:
                pos = self.graph_manager.get_star_pos(first)
                self.graph_widget.donkey_pos = pos
                self.graph_widget.update()

    def on_start_star_changed(self, index=None):
        """Slot al cambiar la estrella de inicio: centra el burro y muestra debug."""
        if isinstance(index, int):
            name = self.start_star_combo.itemText(index)
        else:
            name = self.start_star_combo.currentText()
        print(f"[DEBUG] Estrella de inicio seleccionada: {repr(name)}")
        if name:
            pos = self.graph_manager.get_star_pos(name)
            self.graph_widget.donkey_pos = pos
            self.graph_widget.update()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()