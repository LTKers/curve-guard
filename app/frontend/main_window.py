from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget, QSizePolicy, QPushButton, QLineEdit, QCheckBox
from PyQt5.QtGui import QPixmap, QImage, QFontDatabase, QFont, QIcon
from PyQt5.QtCore import Qt
import cv2 as cv
import math
import os

class MainWindow(QMainWindow):
    def __init__(self, analyzer):
        # Window Set Up
        super().__init__()
        self.setWindowTitle("Curve Guard")
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        window_icon=os.path.join(self.base_dir, "assets", "logo.png")
        self.setWindowIcon(QIcon(window_icon))

        font_path = os.path.join(self.base_dir, "assets","Orbitron", "static","Orbitron-Regular.ttf")
        self.font_id = QFontDatabase.addApplicationFont(font_path)
        self.families = QFontDatabase.applicationFontFamilies(self.font_id)
        self.orbitron = QFont(self.families[0], 12)
        self.analyzer=analyzer
        self.analyzer.frame_ready.connect(self.update_image)

        # Calculate window size (80% of width & 70% of height)
        screen = QDesktopWidget().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.7)

        # Calculate position to center window
        pos_x = (screen_width - window_width) // 2
        pos_y = (screen_height - window_height) // 2
        self.setGeometry(pos_x, pos_y, window_width, window_height)

        self.initUI()

    def initUI(self):
        # Set up central widget
        central_widget=QWidget()
        self.setCentralWidget(central_widget)
        
        #Processed Video feed
        self.video_label=QLabel(self)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setMinimumSize(320, 240)       

        # Top bar
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(50)
        self.top_bar_layout = QHBoxLayout()
        self.top_bar.setLayout(self.top_bar_layout)
        self.top_bar.setObjectName("top_bar")
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0) 
        self.top_bar_layout.setSpacing(0)

        # Logo
        self.logo=QLabel(self)
        logo_path=os.path.join(self.base_dir, "assets", "logo.png")
        self.logo_pixmap=QPixmap(logo_path)
        self.scaled_pixmap = self.logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo.setPixmap(self.scaled_pixmap)
        self.top_bar_layout.addWidget(self.logo, 0, Qt.AlignLeft)
        self.logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.logo.setObjectName("logo")
        self.logo.setScaledContents(False)

        # Curve Guard Text (App name)
        self.curve_guard_name=QLabel("Curve Guard", self)
        self.curve_guard_name.setObjectName("curve_guard")
        self.curve_guard_name.setFont(self.orbitron)
        self.curve_guard_name.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.top_bar_layout.addWidget(self.curve_guard_name, 0, Qt.AlignLeft)
        self.top_bar_layout.addStretch(3)


        # Side bar
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.sidebar.setMinimumSize(0, 0)    
        self.sidebar.setFixedWidth(300)   
        

        # Control_Panel Text
        self.control_panel=QLabel("Control Panel", self)
        self.control_panel.setFont(self.orbitron)
        self.sidebar_layout.addWidget(self.control_panel, 0, Qt.AlignLeft)
        self.control_panel.setObjectName("control_panel")

        # Height Monitor
        self.height_monitor=QWidget()
        self.sidebar_layout.addWidget(self.height_monitor)
        self.height_monitor_layout= QGridLayout()
        self.height_monitor.setLayout(self.height_monitor_layout)
        self.height_monitor.setObjectName("height_monitor")
        self.height_monitor.setFixedSize(280, 200);
        self.sidebar_layout.addStretch()

        # Height Monitor Text
        self.height_monitor_text=QLabel("Posture Height Monitor", self)
        self.height_monitor_text.setFont(self.orbitron)
        self.height_monitor_text.setObjectName("height_monitor_text")
        self.height_monitor_layout.addWidget(self.height_monitor_text, 0, 0)

        # Calibrate Height Line Button
        self.calibrate_height = QPushButton("Calibrate Default Eye Level", self)
        self.calibrate_height.setFont(self.orbitron)
        self.calibrate_height.setIcon(QIcon()) 
        self.height_monitor_layout.addWidget(self.calibrate_height, 1, 0, 1, 2, alignment=Qt.AlignCenter)
        self.calibrate_height.setFixedSize(260, 30)
        self.calibrate_height.setObjectName("calibrate")
        self.calibrate_height.clicked.connect(self.analyzer.calibrate_height_line)

        # Height Leniency
        self.height_leniency_text=QLabel("Height Leniency (0-100%)", self)
        self.height_monitor_layout.addWidget(self.height_leniency_text, 2, 0)
        self.height_leniency_text.setObjectName("blue_settings_text")
        self.height_leniency_entry=QLineEdit(self)
        self.height_monitor_layout.addWidget(self.height_leniency_entry, 2, 1)
        self.height_leniency_entry.editingFinished.connect(self.validate_height_leniency)

        # Time Leniency
        self.time_leniency_text=QLabel("Time Leniency (s)", self)
        self.height_monitor_layout.addWidget(self.time_leniency_text, 3, 0)
        self.time_leniency_text.setObjectName("blue_settings_text")
        self.time_leniency_entry=QLineEdit(self)
        self.height_monitor_layout.addWidget(self.time_leniency_entry, 3, 1)
        self.height_monitor_layout.setRowStretch(self.height_monitor_layout.rowCount(), 1)

        # Line Visibility
        self.line_visibility_text=QLabel("Line Visibility", self)
        self.height_monitor_layout.addWidget(self.line_visibility_text, 4, 0)
        self.line_visibility_text.setObjectName("blue_settings_text")
        self.line_visibility_checkbox=QCheckBox(self)
        self.line_visibility_checkbox.setChecked(True)
        self.height_monitor_layout.addWidget(self.line_visibility_checkbox, 4, 1)
        

        self.height_monitor_layout.setRowStretch(self.height_monitor_layout.rowCount(), 1)

        # Main area
        self.main_area = QWidget()
        self.main_area_layout = QHBoxLayout()
        self.main_area_layout.addWidget(self.video_label)
        self.main_area.setLayout(self.main_area_layout)
        self.main_area.setObjectName("main_area")
        
        # Body area
        self.body_area = QWidget()
        self.body_area_layout = QHBoxLayout()
        self.body_area_layout.addWidget(self.main_area, 3)
        self.body_area_layout.addWidget(self.sidebar, 1)
        self.body_area.setLayout(self.body_area_layout)
        self.body_area_layout.setContentsMargins(0, 0, 0, 0)
        self.body_area_layout.setSpacing(0)
        self.body_area.setObjectName("body_area")


        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.top_bar)
        self.main_layout.addWidget(self.body_area)

        central_widget.setLayout(self.main_layout)
        
        
        

    def update_image(self, cv_img):
        # Get target size from QLabel
        target_width = self.video_label.width()
        target_height = self.video_label.height()

        # Resize + Center Crop
        img = self.center_crop_resize(cv_img, target_width, target_height)

        # Convert to QImage and display
        h, w, ch = img.shape

        bytes_per_line = ch * w
        camera_image = QImage(img.tobytes(), w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(camera_image))


    def center_crop_resize(self, frame, target_width, target_height):
        h, w, _ = frame.shape

        # Scale so the image covers the whole label area, rounding up to avoid smaller size
        scale = max(target_width / w, target_height / h)
        new_w, new_h = math.ceil(w * scale), math.ceil(h * scale)
        resized = cv.resize(frame, (new_w, new_h), interpolation=cv.INTER_AREA)

        x_start = (new_w - target_width) // 2
        y_start = (new_h - target_height) // 2

        cropped = resized[y_start:y_start + target_height, x_start:x_start + target_width]

        return cropped

    def closeEvent(self, event):
        self.analyzer.stop()
        event.accept()

    def validate_height_leniency(self):
        value = self.leniency_entry.text()
        if not value.isdigit():
            self.leniency_entry.setText("0")
        else:
            value = int(value)
            if value < 0:
                self.leniency_entry.setText("0")
            elif value > 100:
                self.leniency_entry.setText("100")
