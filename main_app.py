import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QGroupBox, QFormLayout, QLineEdit, QComboBox, QLabel
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

        self.load_button = QPushButton("Cargar Constelaciones (JSON)")
        self.load_button.clicked.connect(self.load_constellations)
        left_layout.addWidget(self.load_button)

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
                # Forzar al widget del grafo a redibujarse con los nuevos datos
                self.graph_widget.update()
            except Exception as e:
                print(f"Error al cargar o procesar el archivo JSON: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()