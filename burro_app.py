import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient, QPolygonF


class BurroWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 500)
        self.setWindowTitle("Burro de Shrek - PyQt6")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fondo con gradiente (pantano de Shrek)
        bg_gradient = QLinearGradient(0, 0, 0, 500)
        bg_gradient.setColorAt(0, QColor(100, 149, 237))  # Azul cielo
        bg_gradient.setColorAt(0.7, QColor(34, 139, 34))  # Verde hierba
        bg_gradient.setColorAt(1, QColor(0, 100, 0))      # Verde oscuro pantano
        painter.fillRect(self.rect(), bg_gradient)
        
        # Sombra del burro en el suelo
        shadow_brush = QBrush(QColor(0, 0, 0, 40))
        painter.setBrush(shadow_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(200, 400, 200, 30)
        
        # Cuerpo del burro de Shrek (más redondo y pequeño)
        body_gradient = QRadialGradient(300, 280, 80)
        body_gradient.setColorAt(0, QColor(255, 218, 185))  # Marrón muy claro (como Shrek)
        body_gradient.setColorAt(1, QColor(210, 180, 140))  # Marrón medio
        painter.setBrush(QBrush(body_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        painter.drawEllipse(200, 250, 200, 150)
        
        # Cuello más corto y grueso (estilo Shrek)
        neck_gradient = QLinearGradient(220, 220, 280, 250)
        neck_gradient.setColorAt(0, QColor(255, 218, 185))
        neck_gradient.setColorAt(1, QColor(210, 180, 140))
        painter.setBrush(QBrush(neck_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        painter.drawEllipse(220, 220, 60, 80)
        
        # Cabeza del burro de Shrek (más redonda y expresiva)
        head_gradient = QRadialGradient(250, 200, 70)
        head_gradient.setColorAt(0, QColor(255, 228, 196))  # Marrón muy claro
        head_gradient.setColorAt(1, QColor(210, 180, 140))  # Marrón medio
        painter.setBrush(QBrush(head_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        painter.drawEllipse(180, 150, 140, 120)
        
        # Orejas GIGANTES como el burro de Shrek
        ear_gradient = QLinearGradient(150, 100, 200, 150)
        ear_gradient.setColorAt(0, QColor(255, 218, 185))
        ear_gradient.setColorAt(1, QColor(210, 180, 140))
        painter.setBrush(QBrush(ear_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        
        # Oreja izquierda (MUY grande)
        left_ear = QPolygonF([
            QPointF(150, 100),
            QPointF(160, 80),
            QPointF(180, 100),
            QPointF(175, 180),
            QPointF(155, 180)
        ])
        painter.drawPolygon(left_ear)
        
        # Oreja derecha (MUY grande)
        right_ear = QPolygonF([
            QPointF(320, 100),
            QPointF(330, 80),
            QPointF(350, 100),
            QPointF(345, 180),
            QPointF(325, 180)
        ])
        painter.drawPolygon(right_ear)
        
        # Interior de las orejas (rosa más vibrante)
        inner_ear_brush = QBrush(QColor(255, 192, 203))
        painter.setBrush(inner_ear_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(160, 120, 12, 40)  # Interior oreja izquierda
        painter.drawEllipse(328, 120, 12, 40)  # Interior oreja derecha
        
        # Ojos del burro de Shrek (más grandes y expresivos)
        # Ojo izquierdo
        eye_white_brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(eye_white_brush)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(200, 180, 20, 16)
        
        # Iris izquierdo (marrón más claro)
        iris_brush = QBrush(QColor(160, 82, 45))
        painter.setBrush(iris_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(204, 184, 12, 8)
        
        # Pupila izquierda
        pupil_brush = QBrush(QColor(0, 0, 0))
        painter.setBrush(pupil_brush)
        painter.drawEllipse(207, 186, 6, 4)
        
        # Brillo en el ojo (más grande)
        highlight_brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(highlight_brush)
        painter.drawEllipse(208, 187, 3, 2)
        
        # Ojo derecho
        painter.setBrush(eye_white_brush)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(280, 180, 20, 16)
        
        painter.setBrush(iris_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(284, 184, 12, 8)
        
        painter.setBrush(pupil_brush)
        painter.drawEllipse(287, 186, 6, 4)
        
        painter.setBrush(highlight_brush)
        painter.drawEllipse(288, 187, 3, 2)
        
        # Hocico del burro de Shrek (más pequeño y redondo)
        snout_gradient = QRadialGradient(250, 230, 25)
        snout_gradient.setColorAt(0, QColor(255, 228, 196))
        snout_gradient.setColorAt(1, QColor(210, 180, 140))
        painter.setBrush(QBrush(snout_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        painter.drawEllipse(230, 220, 40, 30)
        
        # Nariz (más pequeña y redonda)
        nose_gradient = QRadialGradient(250, 235, 12)
        nose_gradient.setColorAt(0, QColor(210, 180, 140))
        nose_gradient.setColorAt(1, QColor(160, 82, 45))
        painter.setBrush(QBrush(nose_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 1))
        painter.drawEllipse(240, 230, 20, 15)
        
        # Fosas nasales (más pequeñas)
        nostril_brush = QBrush(QColor(0, 0, 0))
        painter.setBrush(nostril_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(244, 234, 2, 3)  # Fosa izquierda
        painter.drawEllipse(254, 234, 2, 3)  # Fosa derecha
        
        # Patas más cortas y gorditas (estilo Shrek)
        leg_gradient = QLinearGradient(0, 0, 0, 1)
        leg_gradient.setColorAt(0, QColor(255, 218, 185))
        leg_gradient.setColorAt(1, QColor(210, 180, 140))
        painter.setBrush(QBrush(leg_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        
        # Pata delantera izquierda (más gorda)
        painter.drawRect(220, 400, 20, 40)
        # Pata delantera derecha
        painter.drawRect(260, 400, 20, 40)
        # Pata trasera izquierda
        painter.drawRect(340, 400, 20, 40)
        # Pata trasera derecha
        painter.drawRect(380, 400, 20, 40)
        
        # Articulaciones más gorditas
        joint_brush = QBrush(QColor(210, 180, 140))
        painter.setBrush(joint_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(220, 410, 20, 15)  # Articulación delantera izquierda
        painter.drawEllipse(260, 410, 20, 15)  # Articulación delantera derecha
        painter.drawEllipse(340, 410, 20, 15)  # Articulación trasera izquierda
        painter.drawEllipse(380, 410, 20, 15)  # Articulación trasera derecha
        
        # Cola más corta y con mechón (estilo Shrek)
        tail_gradient = QLinearGradient(400, 300, 450, 250)
        tail_gradient.setColorAt(0, QColor(255, 218, 185))
        tail_gradient.setColorAt(1, QColor(210, 180, 140))
        painter.setBrush(QBrush(tail_gradient))
        painter.setPen(QPen(QColor(160, 82, 45), 4))
        painter.drawLine(400, 320, 450, 280)
        
        # Mechón de pelo en la cola
        tail_tip_brush = QBrush(QColor(160, 82, 45))
        painter.setBrush(tail_tip_brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(445, 275, 12, 18)
        
        # Crin (pelo en la cabeza) más despeinado
        mane_pen = QPen(QColor(160, 82, 45), 5)
        painter.setPen(mane_pen)
        painter.drawLine(180, 160, 190, 140)
        painter.drawLine(200, 165, 210, 145)
        painter.drawLine(220, 165, 230, 145)
        painter.drawLine(240, 165, 250, 145)
        painter.drawLine(260, 160, 270, 140)
        painter.drawLine(280, 160, 290, 140)
        
        # Pezuñas más pequeñas y redondas
        hoof_gradient = QLinearGradient(0, 0, 0, 1)
        hoof_gradient.setColorAt(0, QColor(105, 105, 105))
        hoof_gradient.setColorAt(1, QColor(0, 0, 0))
        painter.setBrush(QBrush(hoof_gradient))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawEllipse(220, 435, 20, 8)  # Pezuña delantera izquierda
        painter.drawEllipse(260, 435, 20, 8)  # Pezuña delantera derecha
        painter.drawEllipse(340, 435, 20, 8)  # Pezuña trasera izquierda
        painter.drawEllipse(380, 435, 20, 8)  # Pezuña trasera derecha
        
        # Expresión facial del burro de Shrek (más amigable)
        expression_pen = QPen(QColor(160, 82, 45), 2)
        painter.setPen(expression_pen)
        painter.drawLine(190, 210, 200, 220)  # Línea de expresión izquierda
        painter.drawLine(310, 210, 300, 220)  # Línea de expresión derecha
        
        # Boca sonriente (característica del burro de Shrek)
        mouth_pen = QPen(QColor(160, 82, 45), 3)
        painter.setPen(mouth_pen)
        painter.drawArc(240, 240, 20, 15, 0, 180)  # Sonrisa más amplia
        
        # Dientes visibles (como el burro de Shrek)
        teeth_brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(teeth_brush)
        painter.setPen(QPen(QColor(160, 82, 45), 1))
        painter.drawEllipse(245, 245, 4, 6)  # Diente izquierdo
        painter.drawEllipse(251, 245, 4, 6)  # Diente derecho


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Burro de Shrek - Aplicación PyQt6")
        self.setGeometry(100, 100, 650, 550)
        
        # Crear el widget del burro
        self.burro_widget = BurroWidget()
        self.setCentralWidget(self.burro_widget)


def main():
    app = QApplication(sys.argv)
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
