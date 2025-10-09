# ui/graph_widget.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt

class GraphWidget(QWidget):
    def __init__(self, graph_manager, parent=None):
        super().__init__(parent)
        self.graph_manager = graph_manager
        self.setMinimumSize(800, 600)
        self.node_radius = 15

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- Dibujar conexiones ---
        pen = QPen(Qt.GlobalColor.white, 2)
        painter.setPen(pen)

        for star1, star2 in self.graph_manager.connections:
            if star1 in self.graph_manager.stars and star2 in self.graph_manager.stars:
                x1, y1 = self.graph_manager.stars[star1]['pos']
                x2, y2 = self.graph_manager.stars[star2]['pos']

                # Si la conexión está bloqueada, la pintamos en rojo
                if tuple(sorted((star1, star2))) in self.graph_manager.blocked_connections:
                    pen = QPen(QColor(200, 50, 50), 2, Qt.PenStyle.DashLine)
                else:
                    pen = QPen(Qt.GlobalColor.white, 2)

                painter.setPen(pen)
                painter.drawLine(x1, y1, x2, y2)

        # --- Dibujar estrellas ---
        for star_name, star_data in self.graph_manager.stars.items():
            x, y = star_data['pos']
            
            # Color distinto si es hipergigante
            if star_data.get('hipergigante', False):
                brush = QBrush(QColor(255, 150, 50))  # naranja
            else:
                brush = QBrush(QColor(100, 150, 255))  # azul

            painter.setBrush(brush)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawEllipse(x - self.node_radius, y - self.node_radius,
                                2 * self.node_radius, 2 * self.node_radius)

            # Nombre de la estrella
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(x + self.node_radius, y, star_name)
