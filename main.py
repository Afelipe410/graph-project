import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QComboBox, QLabel, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QTimer, QUrl, Qt, QDir
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from core.graph_manager import GraphManager
from ui.graph_widget import GraphWidget
from core.donkey import Donkey
from core.route_calculator import RouteCalculator


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
        self.current_donkey = None
        self.current_route_report_data = None # Para guardar datos del reporte

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

        self.constellation_combo = QComboBox()
        self.constellation_combo.currentIndexChanged.connect(lambda idx: self.on_constellation_selected(idx))
        self.constellation_combo.setEnabled(True)
        self.constellation_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.constellation_combo.setMinimumWidth(200)

        self.start_star_combo.setEnabled(True)
        self.start_star_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.start_star_combo.setMinimumWidth(200)
        self.start_star_combo.currentIndexChanged.connect(lambda idx: self.on_start_star_changed(idx))

        donkey_layout.addRow("Constelación:", self.constellation_combo)
        donkey_layout.addRow("Estrella de Inicio:", self.start_star_combo)
        donkey_layout.addRow("Salud:", self.health_combo)
        donkey_layout.addRow("Edad:", self.age_input)
        donkey_layout.addRow("Energía (%):", self.energy_input)
        donkey_layout.addRow("Pasto en Bodega (kg):", self.grass_input)

        self.create_donkey_button = QPushButton("Crear/Actualizar Burro")
        self.create_donkey_button.clicked.connect(self.create_or_update_donkey)
        donkey_layout.addRow(self.create_donkey_button)

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

        # --- Bloqueo de Caminos ---
        path_blocking_group = QGroupBox("Bloqueo de Caminos")
        path_blocking_layout = QFormLayout()

        self.block_star1_combo = QComboBox()
        self.block_star2_combo = QComboBox()
        self.block_path_button = QPushButton("Bloquear Camino")
        self.unblock_path_button = QPushButton("Desbloquear Camino")

        self.block_path_button.clicked.connect(self.block_selected_path)
        self.unblock_path_button.clicked.connect(self.unblock_selected_path)

        path_blocking_layout.addRow("Estrella 1:", self.block_star1_combo)
        path_blocking_layout.addRow("Estrella 2:", self.block_star2_combo)
        path_blocking_layout.addRow(self.block_path_button)
        path_blocking_layout.addRow(self.unblock_path_button)

        path_blocking_group.setLayout(path_blocking_layout)
        left_layout.addWidget(path_blocking_group)

        # --- Estado del Burro ---
        status_group = QGroupBox("Estado Actual del Burro")
        status_layout = QFormLayout()

        self.status_health_label = QLabel("-")
        self.status_energy_label = QLabel("-")
        self.status_grass_label = QLabel("-")
        self.status_life_label = QLabel("-")

        status_layout.addRow("Salud:", self.status_health_label)
        status_layout.addRow("Energía:", self.status_energy_label)
        status_layout.addRow("Pasto Restante:", self.status_grass_label)
        status_layout.addRow("Vida Restante (años luz):", self.status_life_label)
        status_group.setLayout(status_layout)

        left_layout.addWidget(status_group)
        left_layout.addStretch()

        # --- Widget del Grafo ---
        self.graph_widget = GraphWidget(self.graph_manager)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.graph_widget)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # --- Sonido de muerte del burro ---
        sound_path = QDir.current().absoluteFilePath("assets/donkey_death.wav")
        self.death_audio = QAudioOutput()
        self.death_player = QMediaPlayer()
        self.death_player.setAudioOutput(self.death_audio)
        self.death_player.setSource(QUrl.fromLocalFile(sound_path))
        self.death_audio.setVolume(0.9)

    # ----------------------------------------------------
    #                  FUNCIONES PRINCIPALES
    # ----------------------------------------------------

    def load_constellations(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo de constelaciones", "",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        if file_path:
            try:
                self.graph_manager.load_from_json(file_path)
                print(f"Archivo cargado exitosamente: {file_path}")
                self.update_ui_after_load()
                self.graph_widget.update()
            except Exception as e:
                print(f"Error al cargar el archivo JSON: {e}")

    def update_ui_after_load(self):
        consts = list(self.graph_manager.constellation_colors.keys())
        self.constellation_combo.clear()
        if consts:
            self.constellation_combo.addItems(consts)
            self.on_constellation_selected(0)
        else:
            self.start_star_combo.clear()

        donkey_data = self.graph_manager.initial_donkey_data
        if donkey_data:
            health_str = donkey_data.get('salud', 'excelente').lower()
            if health_str in [self.health_combo.itemText(i) for i in range(self.health_combo.count())]:
                self.health_combo.setCurrentText(health_str)
            self.age_input.setValue(donkey_data.get('edad', 10))
            self.energy_input.setValue(donkey_data.get('energia', 100))
            self.grass_input.setValue(donkey_data.get('pasto', 100))
        self.update_path_blocking_ui()

    def calculate_die_hard_route(self):
        start_star = self.start_star_combo.currentText()
        if not start_star or not self.current_donkey:
            QMessageBox.warning(self, "Advertencia", "Selecciona constelación, estrella y crea un burro.")
            return
        route, stars_visited = self.route_calculator.calculate_max_stars_route(start_star, self.current_donkey)
        self.graph_widget.set_highlighted_route(route)
        QMessageBox.information(self, "Ruta de Resistencia", f"Visitadas {stars_visited} estrellas:\n{' -> '.join(route)}")

    def calculate_economical_route(self):
        start_star = self.start_star_combo.currentText()
        if not start_star or not self.current_donkey:
            QMessageBox.warning(self, "Advertencia", "Selecciona constelación, estrella y crea un burro.")
            return
        
        route, stars_visited, food_log, research_log = self.route_calculator.calculate_economical_route(start_star, self.current_donkey)
        
        # Guardar los datos para el reporte que se mostrará al final del viaje
        self.current_route_report_data = {
            "route": route, "food_log": food_log, "research_log": research_log
        }

        self.graph_widget.set_highlighted_route(route)
        QMessageBox.information(self, "Ruta Económica", f"Visitadas {stars_visited} estrellas.\nIniciando simulación...")
        self.start_animation(route)

    def create_or_update_donkey(self):
        self.current_donkey = Donkey(
            salud=self.health_combo.currentText(),
            edad=self.age_input.value(),
            energia=self.energy_input.value(),
            pasto=self.grass_input.value()
        )
        self.update_donkey_status_ui()
        QMessageBox.information(self, "Burro Listo",
                                f"Burro creado:\nVida: {self.current_donkey.vida_restante:.1f} años luz\n"
                                f"Energía: {self.current_donkey.energia}%")

    def start_animation(self, route):
        if len(route) < 2:
            return
        self.animation_path = route
        self.animation_step_index = 0
        self.graph_widget.donkey_pos = self.graph_manager.get_star_pos(route[0])
        self.update_donkey_status_ui()
        self.animation_timer.start(30)

    def animate_step(self):
        start_idx = self.animation_step_index
        end_idx = start_idx + 1
        if end_idx >= len(self.animation_path):
            self.animation_timer.stop()
            QMessageBox.information(self, "Simulación", "¡El burro completó la ruta con éxito!")
            # Mostrar el reporte al finalizar con éxito
            if self.current_route_report_data:
                self.show_route_report(**self.current_route_report_data)
                self.current_route_report_data = None # Limpiar para la próxima
            return

        start_pos = self.graph_manager.get_star_pos(self.animation_path[start_idx])
        end_pos = self.graph_manager.get_star_pos(self.animation_path[end_idx])
        current_pos = self.graph_widget.donkey_pos
        dx, dy = end_pos[0] - current_pos[0], end_pos[1] - current_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 2:
            speed = 2
            self.graph_widget.donkey_pos = (current_pos[0] + (dx / distance) * speed,
                                            current_pos[1] + (dy / distance) * speed)
        else:
            self.graph_widget.donkey_pos = end_pos
            self.animation_step_index += 1

            if self.current_donkey:
                travel_distance = self.graph_manager.get_distance(
                    self.animation_path[start_idx], self.animation_path[end_idx])
                if travel_distance == float('inf'):
                    travel_distance = math.sqrt((start_pos[0]-end_pos[0])**2 + (start_pos[1]-end_pos[1])**2) / 4.0

                self.current_donkey.viajar(travel_distance)
                star_info = self.graph_manager.stars.get(self.animation_path[end_idx], {})
                estrella_data = {
                    'tiempo_para_comer': star_info.get('tiempo_para_comer', 1),
                    'costo_energia_invest': star_info.get('costo_energia_invest', 1)
                }
                self.current_donkey.procesar_estrella(self.animation_path[end_idx], estrella_data) # Pasar el label de la estrella

                # 💀 Muerte del burro
                if self.current_donkey.vida_restante <= 0 or self.current_donkey.energia <= 0:
                    self.animation_timer.stop()
                    self.death_player.stop()
                    self.death_player.play()
                    QTimer.singleShot(2000, lambda: QMessageBox.critical(
                        self, "El burro ha muerto",
                        "💀 El burro no pudo completar la ruta y ha muerto en el viaje."
                    ))
                    # Mostrar el reporte final aunque el burro haya muerto
                    if self.current_route_report_data:
                        self.show_route_report(**self.current_route_report_data)
                        self.current_route_report_data = None # Limpiar

                self.update_donkey_status_ui()

        self.graph_widget.update()

    def update_donkey_status_ui(self):
        if self.current_donkey:
            self.status_health_label.setText(self.current_donkey.get_salud_str())
            self.status_energy_label.setText(f"{self.current_donkey.energia:.1f} %")
            self.status_grass_label.setText(f"{self.current_donkey.pasto:.1f} kg")
            self.status_life_label.setText(f"{self.current_donkey.vida_restante:.1f}")

    def on_constellation_selected(self, index=None):
        name = self.constellation_combo.itemText(index) if isinstance(index, int) else self.constellation_combo.currentText()
        print(f"[DEBUG] Constelación seleccionada: {name}")
        self.start_star_combo.clear()
        if not name:
            return
        stars = [s for s, d in self.graph_manager.stars.items() if d.get('constellation', '') == name]
        stars.sort()
        self.start_star_combo.addItems(stars)
        if stars:
            pos = self.graph_manager.get_star_pos(stars[0])
            self.graph_widget.donkey_pos = pos
            self.graph_widget.update()

    def on_start_star_changed(self, index=None):
        name = self.start_star_combo.itemText(index) if isinstance(index, int) else self.start_star_combo.currentText()
        print(f"[DEBUG] Estrella seleccionada: {name}")
        if name:
            pos = self.graph_manager.get_star_pos(name)
            self.graph_widget.donkey_pos = pos
            self.graph_widget.update()

    def update_path_blocking_ui(self):
        """Actualiza los QComboBox para el bloqueo de caminos con todas las estrellas."""
        all_stars = self.graph_manager.get_all_star_labels()
        self.block_star1_combo.clear()
        self.block_star2_combo.clear()
        if all_stars:
            self.block_star1_combo.addItems(all_stars)
            self.block_star2_combo.addItems(all_stars)

    def block_selected_path(self):
        """Bloquea el camino seleccionado entre dos estrellas."""
        star1 = self.block_star1_combo.currentText()
        star2 = self.block_star2_combo.currentText()

        if not star1 or not star2:
            QMessageBox.warning(self, "Advertencia", "Selecciona dos estrellas para bloquear el camino.")
            return
        if star1 == star2:
            QMessageBox.warning(self, "Advertencia", "No puedes bloquear un camino de una estrella a sí misma.")
            return

        success, message = self.graph_manager.block_connection(star1, star2)
        if success:
            QMessageBox.information(self, "Camino Bloqueado", message)
            self.graph_widget.update() # Redibujar para mostrar el camino bloqueado
        else:
            QMessageBox.warning(self, "Error al Bloquear", message)

    def unblock_selected_path(self):
        """Desbloquea el camino seleccionado entre dos estrellas."""
        star1 = self.block_star1_combo.currentText()
        star2 = self.block_star2_combo.currentText()

        if not star1 or not star2:
            QMessageBox.warning(self, "Advertencia", "Selecciona dos estrellas para desbloquear el camino.")
            return

        success, message = self.graph_manager.unblock_connection(star1, star2)
        if success:
            QMessageBox.information(self, "Camino Desbloqueado", message)
            self.graph_widget.update() # Redibujar para mostrar el camino desbloqueado
        else:
            QMessageBox.warning(self, "Error al Desbloquear", message)

    def show_route_report(self, route, food_log, research_log):
        """
        Genera y muestra un reporte detallado de la ruta calculada.
        Incluye estrellas visitadas, constelaciones, consumo de pasto y tiempo de investigación.
        """
        report_text = "--- Reporte de Ruta Económica ---\n\n"
        report_text += f"Ruta visitada ({len(route)} estrellas): {' -> '.join(route)}\n\n"
        report_text += "Detalle por Estrella:\n"

        # Consolidar logs para fácil acceso, sumando si una estrella aparece múltiples veces
        food_by_star = {}
        for entry in food_log:
            star = entry['star']
            amount = entry['amount_kg']
            food_by_star[star] = food_by_star.get(star, 0) + amount

        research_by_star = {}
        for entry in research_log:
            star = entry['star']
            units = entry['units_investigated']
            research_by_star[star] = research_by_star.get(star, 0) + units

        for star_label in route:
            star_data = self.graph_manager.stars.get(star_label)
            if not star_data:
                report_text += f"\nEstrella: {star_label} (Datos no encontrados)\n"
                continue

            constellation = star_data.get('constellation', 'Desconocida')
            food_consumed = food_by_star.get(star_label, 0)
            research_units = research_by_star.get(star_label, 0)

            report_text += f"\nEstrella: {star_label}\n"
            report_text += f"  Constelación: {constellation}\n"
            report_text += f"  Consumo de Pasto: {food_consumed:.2f} kg\n"
            # Asumiendo que si se realizó investigación (research_units > 0), se invirtieron 10 unidades de tiempo.
            report_text += f"  Tiempo de Investigación: {10 if research_units > 0 else 0} unidades de tiempo\n"

        QMessageBox.information(self, "Reporte de Ruta", report_text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
