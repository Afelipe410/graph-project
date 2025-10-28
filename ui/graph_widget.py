# ui/graph_widget.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
import os

class GraphWidget(QWidget):
    def __init__(self, graph_manager, parent=None):
        super().__init__(parent)
        self.graph_manager = graph_manager
        self.setMinimumSize(900, 700)
        # Tamaño base de nodos y escaladores para hacerlos más grandes
        self.node_radius = 24        # radio base para estrellas (aumentado)
        self.star_scale = 1.4        # factor adicional por visibilidad
        self.donkey_pix_size = 64    # tamaño del sprite del burro en píxeles
        self.highlighted_route = []
        self.donkey_pos = None

        # Intentar cargar sprite del burro; buscar en la carpeta assets del proyecto
        assets_candidate = Path(__file__).resolve().parents[1] / "assets" / "donkey.png"
        pm = QPixmap(str(assets_candidate))
        # fallback: intentar desde el working directory (ejecución desde VSCode)
        if pm.isNull():
            wd_candidate = Path(os.getcwd()) / "assets" / "donkey.png"
            pm = QPixmap(str(wd_candidate))
            if not pm.isNull():
                print(f"donkey.png cargado desde working dir: {wd_candidate}")
        else:
            print(f"donkey.png cargado desde assets: {assets_candidate}")
        if pm.isNull():
            # Pixmap de reserva (círculo amarillo) con mayor tamaño
            pm = QPixmap(self.donkey_pix_size, self.donkey_pix_size)
            pm.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pm)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(220, 200, 50)))
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.drawEllipse(0, 0, self.donkey_pix_size, self.donkey_pix_size)
            painter.end()
        else:
            pm = pm.scaled(self.donkey_pix_size, self.donkey_pix_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.donkey_pixmap = pm

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo oscuro
        painter.fillRect(self.rect(), QColor(10, 20, 30))

        # --- Dibujar coordenadas en las laterales (izquierda y derecha) ---
        w = self.width()
        h = self.height()
        step = 50
        label_margin = 6
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        # Si el graph_manager tiene mapeo unidad->px, mostrar valores en cm;
        has_units = hasattr(self.graph_manager, 'um_scale') and self.graph_manager.um_scale > 0
        for y in range(0, h + 1, step):
            painter.drawLine(label_margin, y, label_margin + 8, y)
            if has_units:
                # convertir píxel -> unidad (ahora unidad = cm)
                unit_y = self.graph_manager.um_min_y + (y - self.graph_manager.um_padding) / self.graph_manager.um_scale
                label_text = f"{unit_y:.2f} cm"
            else:
                label_text = str(y)
            painter.drawText(label_margin + 12, y + 4, label_text)
            painter.drawLine(w - label_margin, y, w - (label_margin + 8), y)
            text_w_offset = 60
            painter.drawText(w - (label_margin + text_w_offset), y + 4, label_text)

        # --- Dibujar conexiones ---
        pen = QPen(Qt.GlobalColor.white, 2)
        painter.setPen(pen)

        for star1, star2, distance in self.graph_manager.connections:
            if star1 in self.graph_manager.stars and star2 in self.graph_manager.stars:
                x1f, y1f = self.graph_manager.stars[star1]['pos']
                x2f, y2f = self.graph_manager.stars[star2]['pos']
                x1, y1, x2, y2 = int(x1f), int(y1f), int(x2f), int(y2f)

                # Si la conexión está bloqueada, la pintamos en rojo punteado
                if tuple(sorted((star1, star2))) in self.graph_manager.blocked_connections:
                    pen = QPen(QColor(200, 50, 50), 2, Qt.PenStyle.DashLine)
                else:
                    pen = QPen(Qt.GlobalColor.white, 2)

                painter.setPen(pen)
                painter.drawLine(x1, y1, x2, y2)

        # --- Resaltar la ruta calculada ---
        if len(self.highlighted_route) > 1:
            pen = QPen(QColor(100, 220, 120), 3)
            painter.setPen(pen)
            for i in range(len(self.highlighted_route) - 1):
                a = self.highlighted_route[i]
                b = self.highlighted_route[i + 1]
                if a in self.graph_manager.stars and b in self.graph_manager.stars:
                    axf, ayf = self.graph_manager.stars[a]['pos']
                    bxf, byf = self.graph_manager.stars[b]['pos']
                    painter.drawLine(int(axf), int(ayf), int(bxf), int(byf))

        # --- Dibujar estrellas ---
        for star_name, star_data in self.graph_manager.stars.items():
            xf, yf = star_data.get('pos', (0, 0))
            x, y = int(xf), int(yf)
            # aplicar escalado adicional para que las estrellas sean más visibles
            radius = max(3, int(self.node_radius * self.star_scale * (star_data.get('radius', 0.5) or 0.5)))
            # si overlap -> rojo, sino color de la constelación
            if star_data.get('overlap'):
                color = QColor(220, 50, 50)
            else:
                color = self.graph_manager.constellation_colors.get(star_data.get('constellation'), QColor(200, 200, 200))
            if star_data.get('hypergiant'):
                painter.setBrush(QBrush(QColor(255, 200, 100)))
            else:
                painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
            # label
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(x + radius + 4, y + 4, star_name)

        # --- Dibujar al burro ---
        if self.donkey_pos:
            dx_f, dy_f = self.donkey_pos
            dx, dy = int(dx_f), int(dy_f)
            if hasattr(self, 'donkey_pixmap') and not self.donkey_pixmap.isNull():
                # centrar el sprite con el nuevo tamaño
                painter.drawPixmap(int(dx - self.donkey_pixmap.width() / 2),
                                   int(dy - self.donkey_pixmap.height() / 2),
                                   self.donkey_pixmap)
            else:
                # fallback: dibujar círculo más grande para visibilidad
                painter.setBrush(QBrush(QColor(220, 200, 50)))
                painter.setPen(QPen(Qt.GlobalColor.black))
                fallback_r = max(12, int(self.donkey_pix_size / 2))
                painter.drawEllipse(dx - fallback_r, dy - fallback_r, fallback_r * 2, fallback_r * 2)

    def set_highlighted_route(self, route):
        self.highlighted_route = route
        if route:
            self.donkey_pos = self.graph_manager.get_star_pos(route[0])
        self.update()
