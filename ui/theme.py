# Warm/Neutral theme colors and styles
BG_COLOR = "#F7F4EF"
SURFACE_COLOR = "#EDE9E0"
SURFACE_HOVER = "#E2DCD0"
SURFACE_PRESSED = "#D6CEBE"
PRIMARY_COLOR = "#C96442"
PRIMARY_HOVER = "#D47756"
ON_PRIMARY = "#FFFFFF"
TEXT_COLOR = "#2D2A26"
TEXT_MUTED = "#5C564D"
BORDER_COLOR = "#D6CEBE"

GLOBAL_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_COLOR};
    color: {TEXT_COLOR};
}}
QWidget {{
    background-color: {BG_COLOR};
    color: {TEXT_COLOR};
    font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
    font-size: 14px;
}}
QFrame#MenuFrame {{
    background-color: {SURFACE_COLOR};
    border-right: 1px solid {BORDER_COLOR};
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}}
QPushButton {{
    background-color: {SURFACE_COLOR};
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_COLOR};
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {SURFACE_HOVER};
    border: 1px solid #4d4d4d;
}}
QPushButton:pressed {{
    background-color: {SURFACE_PRESSED};
}}
QPushButton#MenuButton {{
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 12px 20px;
    margin: 2px 10px;
    border-radius: 8px;
    font-size: 15px;
}}
QPushButton#MenuButton:hover {{
    background-color: {SURFACE_HOVER};
}}
QPushButton#MenuButton:checked {{
    background-color: {PRIMARY_COLOR};
    color: {ON_PRIMARY};
    font-weight: bold;
}}
QLabel {{
    background-color: transparent;
}}
QStackedWidget {{
    background-color: {BG_COLOR};
}}
QLineEdit, QSpinBox, QComboBox {{
    background-color: {SURFACE_COLOR};
    border: 1px solid {BORDER_COLOR};
    color: {TEXT_COLOR};
    padding: 6px 12px;
    border-radius: 4px;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {PRIMARY_COLOR};
}}
QListWidget {{
    background-color: {SURFACE_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    padding: 4px;
}}
QListWidget::item:selected {{
    background-color: {PRIMARY_COLOR};
    color: {ON_PRIMARY};
    border-radius: 4px;
}}
QFrame#DropZone {{
    border: 2px dashed {BORDER_COLOR};
    border-radius: 8px;
    background-color: {SURFACE_COLOR};
}}
QFrame#DropZone:hover {{
    border: 2px dashed {PRIMARY_COLOR};
    background-color: {SURFACE_HOVER};
}}
"""
