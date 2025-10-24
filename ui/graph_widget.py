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

        for star1, star2, distance in self.graph_manager.connections:
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

            num_constelaciones = len(star_data.get('constelaciones', []))

            if num_constelaciones > 1:
                # Requisito: Resaltar de color rojo si pertenece a varias constelaciones
                brush = QBrush(QColor(255, 0, 0))  # Rojo
            elif num_constelaciones == 1:
                # Requisito: Cada constelación un color diferente
                constelacion_nombre = list(star_data['constelaciones'])[0]
                color = self.graph_manager.constellation_colors.get(constelacion_nombre, QColor(100, 150, 255))
                brush = QBrush(color)
            else:
                # Caso por defecto (estrella sin constelación)
                brush = QBrush(QColor(200, 200, 200))  # Gris

            painter.setBrush(brush)
            # Borde especial para hipergigantes para no perder esa información visual
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawEllipse(x - self.node_radius, y - self.node_radius,
                                2 * self.node_radius, 2 * self.node_radius)

            # Nombre de la estrella
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(x + self.node_radius, y, star_name)
