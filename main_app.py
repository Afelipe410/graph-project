import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QComboBox, QLabel, QSpinBox
from core.graph_manager import GraphManager
from ui.graph_widget import GraphWidget
from core.graph_manager import GraphManager
from core.donkey import Donkey
from core.route_calculator import RouteCalculator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NASA: Misión Burro Espacial")
        self.setGeometry(100, 100, 1200, 800)

        self.graph_manager = GraphManager()
        self.route_calculator = RouteCalculator(self.graph_manager)

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

        self.calc_die_hard_button = QPushButton("Calcular Ruta 'Die Hard'")
        self.calc_economical_button = QPushButton("Calcular Ruta Económica")

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
        self.start_star_combo.clear()
        self.start_star_combo.addItems(sorted(self.graph_manager.stars.keys()))
        
        # Pre-llenar la UI con los datos del burro del JSON
        donkey_data = self.graph_manager.initial_donkey_data
        if donkey_data:
            health_str = donkey_data.get('salud', 'excelente').lower()
            if health_str in [self.health_combo.itemText(i) for i in range(self.health_combo.count())]:
                self.health_combo.setCurrentText(health_str)
            
            self.age_input.setValue(donkey_data.get('edad', 10))
            self.energy_input.setValue(donkey_data.get('energia', 100))
            self.grass_input.setValue(donkey_data.get('pasto', 100))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()