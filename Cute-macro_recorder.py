
"""
Clone de Jitbit Macro Recorder en Python 3.12 avec PyQt6 - INTERFACE REDESIGNÉE
Interface moderne, claire et lisible avec thèmes clair/sombre
Auteur: Assistant IA - Ingénieur logiciel
"""

import sys
import json
import time
import threading
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

# Imports pour l'interface
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Imports pour l'automation
try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button as MouseButton
    from pynput.keyboard import Key
    import pyautogui

    # Configuration DPI pour Windows
    import ctypes
    try:
        PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
    except:
        pass

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
    MODULES_AVAILABLE = True

except ImportError as e:
    print(f"⚠️ Modules manquants: {e}")
    MODULES_AVAILABLE = False

# Constantes pour les thèmes
class Theme:
    LIGHT = {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'bg_accent': '#E9ECEF',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'border': '#DEE2E6',
        'success': '#28A745',
        'danger': '#DC3545',
        'warning': '#FFC107',
        'info': '#17A2B8',
        'primary': '#007BFF',
        'button_bg': '#F8F9FA',
        'button_hover': '#E9ECEF',
        'button_pressed': '#DEE2E6',
        'primary_button_bg': '#007BFF',
        'primary_button_hover': '#0056B3',
        'primary_button_pressed': '#004085',
        'group_bg': '#FFFFFF',
        'list_bg': '#FFFFFF',
        'list_item_hover': '#F8F9FA',
        'list_item_selected': '#E3F2FD'
    }

    DARK = {
        'bg_primary': '#2B2B2B',
        'bg_secondary': '#3C3C3C',
        'bg_accent': '#4D4D4D',
        'text_primary': '#FFFFFF',
        'text_secondary': '#CCCCCC',
        'border': '#5A5A5A',
        'success': '#4CAF50',
        'danger': '#F44336',
        'warning': '#FF9800',
        'info': '#2196F3',
        'primary': '#2196F3',
        'button_bg': '#404040',
        'button_hover': '#505050',
        'button_pressed': '#353535',
        'primary_button_bg': '#2196F3',
        'primary_button_hover': '#1976D2',
        'primary_button_pressed': '#1565C0',
        'group_bg': '#353535',
        'list_bg': '#353535',
        'list_item_hover': '#404040',
        'list_item_selected': '#1E88E5'
    }

@dataclass
class MacroAction:
    """Structure de données pour une action de macro"""
    action_type: str
    timestamp: float
    data: Dict[str, Any]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_display_text(self):
        """Retourne le texte d'affichage pour cette action"""
        if self.action_type == "mouse_move":
            return f"🖱️ Mouvement souris ({self.data['x']}, {self.data['y']})"
        elif self.action_type == "mouse_click":
            btn = self.data.get('button', 'left')
            action = "Clic" if self.data.get('pressed', True) else "Relâchement"
            return f"🖱️ {action} {btn} ({self.data['x']}, {self.data['y']})"
        elif self.action_type == "key_press":
            key = str(self.data['key']).replace('Key.', '').replace("'", "")
            return f"⌨️ Pression: {key}"
        elif self.action_type == "key_release":
            key = str(self.data['key']).replace('Key.', '').replace("'", "")
            return f"⌨️ Relâchement: {key}"
        elif self.action_type == "scroll":
            direction = "bas" if self.data['dy'] < 0 else "haut"
            return f"🖱️ Scroll vers le {direction} ({self.data['x']}, {self.data['y']})"
        else:
            return f"⏱️ Action: {self.action_type}"

class MacroRecorder(QObject):
    """Classe pour enregistrer les actions utilisateur avec pynput"""

    action_recorded = pyqtSignal(MacroAction)
    recording_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.actions: List[MacroAction] = []
        self.is_recording = False
        self.start_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_move_time = 0
        self.move_threshold = 0.1

    def start_recording(self):
        """Démarre l'enregistrement des actions"""
        if not MODULES_AVAILABLE:
            self.error_occurred.emit("Modules pynput/pyautogui non disponibles")
            return False

        try:
            self.actions.clear()
            self.is_recording = True
            self.start_time = time.time()
            self.last_move_time = 0

            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )

            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )

            self.mouse_listener.start()
            self.keyboard_listener.start()

            return True

        except Exception as e:
            self.error_occurred.emit(f"Erreur lors du démarrage: {str(e)}")
            return False

    def stop_recording(self):
        """Arrête l'enregistrement"""
        self.is_recording = False

        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
        except:
            pass

        self.recording_stopped.emit()

    def _get_current_time(self):
        return time.time() - self.start_time

    def _on_mouse_move(self, x, y):
        if not self.is_recording:
            return

        current_time = time.time()
        if current_time - self.last_move_time < self.move_threshold:
            return

        self.last_move_time = current_time

        action = MacroAction(
            action_type="mouse_move",
            timestamp=self._get_current_time(),
            data={"x": int(x), "y": int(y)}
        )

        self.actions.append(action)
        self.action_recorded.emit(action)

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.is_recording:
            return

        button_name = "gauche" if button == MouseButton.left else "droit"

        action = MacroAction(
            action_type="mouse_click",
            timestamp=self._get_current_time(),
            data={"x": int(x), "y": int(y), "button": button_name, "pressed": pressed}
        )

        self.actions.append(action)
        self.action_recorded.emit(action)

    def _on_mouse_scroll(self, x, y, dx, dy):
        if not self.is_recording:
            return

        action = MacroAction(
            action_type="scroll",
            timestamp=self._get_current_time(),
            data={"x": int(x), "y": int(y), "dx": int(dx), "dy": int(dy)}
        )

        self.actions.append(action)
        self.action_recorded.emit(action)

    def _on_key_press(self, key):
        if not self.is_recording:
            return

        action = MacroAction(
            action_type="key_press",
            timestamp=self._get_current_time(),
            data={"key": str(key)}
        )

        self.actions.append(action)
        self.action_recorded.emit(action)

    def _on_key_release(self, key):
        if not self.is_recording:
            return

        action = MacroAction(
            action_type="key_release",
            timestamp=self._get_current_time(),
            data={"key": str(key)}
        )

        self.actions.append(action)
        self.action_recorded.emit(action)

class MacroPlayer(QObject):
    """Classe pour rejouer les macros avec pyautogui"""

    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    action_played = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.actions: List[MacroAction] = []
        self.is_playing = False
        self.speed_multiplier = 1.0
        self.loop_count = 1
        self.playback_thread = None

    def set_actions(self, actions: List[MacroAction]):
        self.actions = actions.copy()

    def set_speed(self, speed: float):
        self.speed_multiplier = max(0.1, min(10.0, speed))

    def set_loop_count(self, count: int):
        self.loop_count = max(1, count)

    def play_macro(self):
        if not MODULES_AVAILABLE:
            self.error_occurred.emit("Modules non disponibles")
            return

        if not self.actions:
            self.error_occurred.emit("Aucune action à jouer")
            return

        self.is_playing = True
        self.playback_started.emit()

        self.playback_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.playback_thread.start()

    def stop_playback(self):
        self.is_playing = False

    def _play_loop(self):
        try:
            for loop in range(self.loop_count):
                if not self.is_playing:
                    break

                for i, action in enumerate(self.actions):
                    if not self.is_playing:
                        break

                    if i > 0:
                        delay = (action.timestamp - self.actions[i-1].timestamp) / self.speed_multiplier
                        time.sleep(max(0, delay))

                    self._execute_action(action)
                    self.action_played.emit(i)

        except Exception as e:
            self.error_occurred.emit(f"Erreur pendant la lecture: {str(e)}")
        finally:
            self.is_playing = False
            self.playback_finished.emit()

    def _execute_action(self, action: MacroAction):
        try:
            if action.action_type == "mouse_click" and action.data.get("pressed", True):
                button = "left" if action.data.get("button") == "gauche" else "right"
                pyautogui.click(action.data["x"], action.data["y"], button=button)

            elif action.action_type == "mouse_move":
                pyautogui.moveTo(action.data["x"], action.data["y"])

            elif action.action_type == "key_press":
                key_str = action.data["key"].replace("Key.", "").replace("'", "")
                key_mapping = {
                    "space": " ",
                    "enter": "enter",
                    "tab": "tab",
                    "backspace": "backspace",
                    "delete": "delete",
                    "shift": "shift",
                    "ctrl": "ctrl",
                    "alt": "alt"
                }
                key_str = key_mapping.get(key_str.lower(), key_str)
                if len(key_str) == 1 or key_str in ["enter", "tab", "backspace", "delete", "shift", "ctrl", "alt"]:
                    pyautogui.press(key_str)

            elif action.action_type == "scroll":
                x, y = action.data["x"], action.data["y"]
                dy = action.data["dy"]
                pyautogui.scroll(dy, x=x, y=y)

        except Exception as e:
            print(f"Erreur lors de l'exécution de l'action {action.action_type}: {e}")

class ModernButton(QPushButton):
    """Bouton moderne avec thèmes"""

    def __init__(self, text="", primary=False, danger=False, success=False, theme=None):
        super().__init__(text)
        self.primary = primary
        self.danger = danger
        self.success = success
        self.theme = theme or Theme.LIGHT
        self.setup_style()

    def set_theme(self, theme):
        self.theme = theme
        self.setup_style()

    def setup_style(self):
        if self.primary:
            bg_color = self.theme['primary_button_bg']
            hover_color = self.theme['primary_button_hover']
            pressed_color = self.theme['primary_button_pressed']
            text_color = '#FFFFFF'
        elif self.danger:
            bg_color = self.theme['danger']
            hover_color = '#E53E3E'
            pressed_color = '#C53030'
            text_color = '#FFFFFF'
        elif self.success:
            bg_color = self.theme['success']
            hover_color = '#48BB78'
            pressed_color = '#38A169'
            text_color = '#FFFFFF'
        else:
            bg_color = self.theme['button_bg']
            hover_color = self.theme['button_hover']
            pressed_color = self.theme['button_pressed']
            text_color = self.theme['text_primary']

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                color: {text_color};
                font-weight: 600;
                font-size: 13px;
                padding: 10px 20px;
                min-width: 80px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-color: {self.theme['primary'] if self.primary else self.theme['border']};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:disabled {{
                background-color: {self.theme['bg_accent']};
                color: {self.theme['text_secondary']};
                border-color: {self.theme['border']};
            }}
        """)

class ModernGroupBox(QGroupBox):
    """GroupBox moderne avec thème"""

    def __init__(self, title="", theme=None):
        super().__init__(title)
        self.theme = theme or Theme.LIGHT
        self.setup_style()

    def set_theme(self, theme):
        self.theme = theme
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 14px;
                border: 2px solid {self.theme['border']};
                border-radius: 10px;
                margin: 8px 0px;
                padding-top: 16px;
                background-color: {self.theme['group_bg']};
                color: {self.theme['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 4px 8px;
                background-color: {self.theme['group_bg']};
                border-radius: 4px;
            }}
        """)

class ModernListWidget(QListWidget):
    """Liste moderne avec thème"""

    def __init__(self, theme=None):
        super().__init__()
        self.theme = theme or Theme.LIGHT
        self.setup_style()

    def set_theme(self, theme):
        self.theme = theme
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme['list_bg']};
                border: 2px solid {self.theme['border']};
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 8px;
                color: {self.theme['text_primary']};
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {self.theme['border']};
                margin: 2px 0px;
                border-radius: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {self.theme['list_item_selected']};
                color: white;
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: {self.theme['list_item_hover']};
                border: 1px solid {self.theme['border']};
            }}
        """)

    def add_action(self, action: MacroAction):
        text = f"{action.timestamp:6.2f}s | {action.get_display_text()}"

        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, action)

        # Couleur selon le type d'action
        if action.action_type == "mouse_click":
            item.setForeground(QColor(self.theme['primary']))
        elif action.action_type.startswith("key_"):
            item.setForeground(QColor(self.theme['success']))
        elif action.action_type == "mouse_move":
            item.setForeground(QColor(self.theme['text_secondary']))

        self.addItem(item)
        self.scrollToBottom()

class StatusLabel(QLabel):
    """Label de statut moderne avec thème"""

    def __init__(self, theme=None):
        super().__init__("🔴 Arrêté")
        self.theme = theme or Theme.LIGHT
        self.current_status = "stopped"
        self.setup_style()

    def set_theme(self, theme):
        self.theme = theme
        self.setup_style()

    def setup_style(self):
        color = self.theme['text_secondary']
        bg_color = self.theme['bg_accent']

        if self.current_status == "recording":
            color = '#FFFFFF'
            bg_color = self.theme['danger']
        elif self.current_status == "playing":
            color = '#FFFFFF'
            bg_color = self.theme['success']

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {color};
                border-radius: 15px;
                padding: 6px 16px;
                font-weight: 600;
                font-size: 12px;
                border: 2px solid {self.theme['border']};
            }}
        """)

    def set_recording(self):
        self.current_status = "recording"
        self.setText("🔴 Enregistrement en cours...")
        self.setup_style()

    def set_playing(self):
        self.current_status = "playing"
        self.setText("▶️ Lecture en cours...")
        self.setup_style()

    def set_stopped(self):
        self.current_status = "stopped"
        self.setText("⏸️ Arrêté")
        self.setup_style()

class MacroRecorderUI(QMainWindow):
    """Interface utilisateur principale redesignée"""

    def __init__(self):
        super().__init__()
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.current_macro_file = None
        self.current_theme = Theme.LIGHT
        self.is_dark_mode = False

        self.setup_ui()
        self.setup_connections()
        self.setup_hotkeys()

        if not MODULES_AVAILABLE:
            QMessageBox.critical(self, "Modules manquants", 
                "Modules pynput et pyautogui requis.\nInstallez avec: pip install pynput pyautogui")

    def setup_ui(self):
        """Configure l'interface utilisateur moderne"""
        self.setWindowTitle("🎯 Macro Recorder Pro - Interface Redesignée")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)

        # Widget central avec layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # En-tête avec titre et contrôles
        self.setup_header(main_layout)

        # Zone des contrôles principaux
        self.setup_controls(main_layout)

        # Zone principale avec splitter
        self.setup_main_area(main_layout)

        # Barre de statut
        self.setup_status_bar()

        # Application du thème
        self.apply_theme()

    def setup_header(self, layout):
        """Configure l'en-tête"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        # Titre et icône
        title_layout = QHBoxLayout()

        # Icône
        icon_label = QLabel("🎯")
        icon_label.setStyleSheet("font-size: 32px;")

        # Titre
        title_label = QLabel("Macro Recorder Pro")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                margin-left: 8px;
            }
        """)

        subtitle_label = QLabel("Interface moderne et ergonomique")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-style: italic;
                margin-left: 8px;
                margin-top: -4px;
            }
        """)

        title_layout.addWidget(icon_label)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(0)
        title_text_layout.addWidget(title_label)
        title_text_layout.addWidget(subtitle_label)

        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()

        header_layout.addLayout(title_layout)

        # Contrôles d'en-tête
        controls_layout = QHBoxLayout()

        # Bouton thème
        self.theme_btn = ModernButton("🌙 Mode Sombre", theme=self.current_theme)
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Status
        self.status_label = StatusLabel(self.current_theme)

        controls_layout.addWidget(self.theme_btn)
        controls_layout.addWidget(self.status_label)

        header_layout.addLayout(controls_layout)

        layout.addWidget(header_widget)

    def setup_controls(self, layout):
        """Configure les contrôles principaux"""
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setSpacing(20)

        # Groupe Enregistrement
        record_group = ModernGroupBox("🎙️ Enregistrement", self.current_theme)
        record_layout = QHBoxLayout(record_group)
        record_layout.setSpacing(12)

        self.record_btn = ModernButton("🔴 Démarrer l'enregistrement", primary=True, theme=self.current_theme)
        self.stop_record_btn = ModernButton("⏹️ Arrêter", danger=True, theme=self.current_theme)
        self.stop_record_btn.setEnabled(False)

        record_layout.addWidget(self.record_btn)
        record_layout.addWidget(self.stop_record_btn)

        # Groupe Lecture
        playback_group = ModernGroupBox("▶️ Lecture", self.current_theme)
        playback_layout = QHBoxLayout(playback_group)
        playback_layout.setSpacing(12)

        self.play_btn = ModernButton("▶️ Jouer la macro", success=True, theme=self.current_theme)
        self.stop_play_btn = ModernButton("⏹️ Arrêter", danger=True, theme=self.current_theme)

        self.play_btn.setEnabled(False)
        self.stop_play_btn.setEnabled(False)

        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_play_btn)

        # Groupe Fichiers
        file_group = ModernGroupBox("📁 Fichiers", self.current_theme)
        file_layout = QHBoxLayout(file_group)
        file_layout.setSpacing(8)

        self.new_btn = ModernButton("🆕 Nouveau", theme=self.current_theme)
        self.open_btn = ModernButton("📂 Ouvrir", theme=self.current_theme)
        self.save_btn = ModernButton("💾 Sauvegarder", theme=self.current_theme)

        file_layout.addWidget(self.new_btn)
        file_layout.addWidget(self.open_btn)
        file_layout.addWidget(self.save_btn)

        controls_layout.addWidget(record_group)
        controls_layout.addWidget(playback_group)
        controls_layout.addWidget(file_group)

        layout.addWidget(controls_widget)

    def setup_main_area(self, layout):
        """Configure la zone principale"""
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Zone gauche - Liste des actions
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # En-tête de la liste
        list_header = QHBoxLayout()

        actions_title = QLabel("📋 Actions Enregistrées")
        actions_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }
        """)

        self.actions_info = QLabel("0 actions | 0.0s")
        self.actions_info.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-style: italic;
            }
        """)

        self.clear_btn = ModernButton("🗑️ Tout effacer", danger=True, theme=self.current_theme)

        list_header.addWidget(actions_title)
        list_header.addStretch()
        list_header.addWidget(self.actions_info)
        list_header.addWidget(self.clear_btn)

        left_layout.addLayout(list_header)

        # Liste des actions
        self.action_list = ModernListWidget(self.current_theme)
        self.action_list.setMinimumHeight(300)
        left_layout.addWidget(self.action_list)

        # Zone droite - Paramètres
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Paramètres de lecture
        settings_group = ModernGroupBox("⚙️ Paramètres de lecture", self.current_theme)
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(12)

        # Vitesse
        speed_label = QLabel("Vitesse de lecture:")
        speed_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        settings_layout.addWidget(speed_label, 0, 0, 1, 2)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 50)
        self.speed_slider.setValue(10)
        self.speed_slider.setMinimumWidth(200)
        settings_layout.addWidget(self.speed_slider, 1, 0)

        self.speed_display = QLabel("1.0x")
        self.speed_display.setStyleSheet("font-weight: bold; font-size: 14px; min-width: 50px;")
        self.speed_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.speed_display, 1, 1)

        # Répétitions
        repeat_label = QLabel("Nombre de répétitions:")
        repeat_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        settings_layout.addWidget(repeat_label, 2, 0)

        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 999)
        self.repeat_spin.setValue(1)
        self.repeat_spin.setMinimumWidth(100)
        self.repeat_spin.setStyleSheet("""
            QSpinBox {
                padding: 6px;
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        settings_layout.addWidget(self.repeat_spin, 2, 1)

        right_layout.addWidget(settings_group)

        # Informations et raccourcis
        info_group = ModernGroupBox("ℹ️ Informations", self.current_theme)
        info_layout = QVBoxLayout(info_group)

        shortcuts_text = QLabel("""
        <b>Raccourcis clavier:</b><br>
        • F9 - Démarrer/Arrêter l'enregistrement<br>
        • F10 - Jouer/Arrêter la macro<br>
        • Ctrl+N - Nouvelle macro<br>
        • Ctrl+O - Ouvrir un fichier<br>
        • Ctrl+S - Sauvegarder<br><br>

        <b>Fonctionnalités:</b><br>
        • Capture des clics et mouvements souris<br>
        • Enregistrement des touches clavier<br>
        • Lecture avec vitesse variable<br>
        • Sauvegarde au format JSON<br>
        • Interface responsive
        """)
        shortcuts_text.setWordWrap(True)
        shortcuts_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                line-height: 1.4;
                padding: 8px;
            }
        """)
        info_layout.addWidget(shortcuts_text)

        right_layout.addWidget(info_group)
        right_layout.addStretch()

        # Ajout au splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])

        layout.addWidget(splitter)

    def setup_status_bar(self):
        """Configure la barre de statut"""
        self.statusBar().showMessage("Prêt à enregistrer - Utilisez F9 pour démarrer")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                border-top: 1px solid #DEE2E6;
                padding: 6px;
                font-size: 12px;
            }
        """)

    def setup_connections(self):
        """Configure les connexions"""
        # Boutons d'enregistrement
        self.record_btn.clicked.connect(self.start_recording)
        self.stop_record_btn.clicked.connect(self.stop_recording)

        # Boutons de lecture
        self.play_btn.clicked.connect(self.play_macro)
        self.stop_play_btn.clicked.connect(self.stop_playback)

        # Boutons de fichier
        self.new_btn.clicked.connect(self.new_macro)
        self.open_btn.clicked.connect(self.open_macro)
        self.save_btn.clicked.connect(self.save_macro)

        # Autres boutons
        self.clear_btn.clicked.connect(self.clear_actions)

        # Slider de vitesse
        self.speed_slider.valueChanged.connect(self.update_speed_display)

        # Signaux du recorder
        self.recorder.action_recorded.connect(self.on_action_recorded)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.recorder.error_occurred.connect(self.on_error)

        # Signaux du player
        self.player.playback_started.connect(self.on_playback_started)
        self.player.playback_finished.connect(self.on_playback_finished)
        self.player.action_played.connect(self.on_action_played)
        self.player.error_occurred.connect(self.on_error)

    def setup_hotkeys(self):
        """Configure les raccourcis clavier"""
        QShortcut(QKeySequence("F9"), self, self.toggle_recording)
        QShortcut(QKeySequence("F10"), self, self.toggle_playback)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_macro)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_macro)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_macro)

    def toggle_theme(self):
        """Bascule entre thème clair et sombre"""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = Theme.DARK if self.is_dark_mode else Theme.LIGHT

        # Mise à jour du bouton thème
        self.theme_btn.setText("☀️ Mode Clair" if self.is_dark_mode else "🌙 Mode Sombre")

        self.apply_theme()

    def apply_theme(self):
        """Applique le thème à toute l'interface"""
        # Mise à jour de tous les boutons
        for btn in self.findChildren(ModernButton):
            btn.set_theme(self.current_theme)

        # Mise à jour de tous les groupes
        for group in self.findChildren(ModernGroupBox):
            group.set_theme(self.current_theme)

        # Mise à jour de la liste
        self.action_list.set_theme(self.current_theme)

        # Mise à jour du status
        self.status_label.set_theme(self.current_theme)

        # Style global de la fenêtre
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.current_theme['bg_primary']};
                color: {self.current_theme['text_primary']};
            }}
            QWidget {{
                background-color: {self.current_theme['bg_primary']};
                color: {self.current_theme['text_primary']};
            }}
            QLabel {{
                color: {self.current_theme['text_primary']};
            }}
            QSplitter::handle {{
                background-color: {self.current_theme['border']};
                width: 3px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {self.current_theme['border']};
                height: 8px;
                background: {self.current_theme['bg_secondary']};
                margin: 2px 0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.current_theme['primary']};
                border: 1px solid {self.current_theme['border']};
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: {self.current_theme['primary']};
                border-radius: 4px;
            }}
            QSpinBox {{
                background-color: {self.current_theme['bg_secondary']};
                border: 2px solid {self.current_theme['border']};
                color: {self.current_theme['text_primary']};
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }}
        """)

    # Méthodes d'enregistrement
    def start_recording(self):
        if self.recorder.start_recording():
            self.record_btn.setEnabled(False)
            self.stop_record_btn.setEnabled(True)
            self.play_btn.setEnabled(False)
            self.status_label.set_recording()
            self.statusBar().showMessage("Enregistrement en cours - F9 pour arrêter")

    def stop_recording(self):
        self.recorder.stop_recording()

    def toggle_recording(self):
        if self.recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    # Méthodes de lecture
    def play_macro(self):
        if not self.recorder.actions:
            QMessageBox.information(self, "Information", "Aucune action à jouer.\nEnregistrez d'abord une macro.")
            return

        self.player.set_actions(self.recorder.actions)
        self.player.set_speed(self.speed_slider.value() / 10.0)
        self.player.set_loop_count(self.repeat_spin.value())
        self.player.play_macro()

    def stop_playback(self):
        self.player.stop_playback()

    def toggle_playback(self):
        if self.player.is_playing:
            self.stop_playback()
        else:
            self.play_macro()

    # Méthodes de fichiers
    def new_macro(self):
        if self.recorder.actions:
            reply = QMessageBox.question(
                self, "Nouvelle macro",
                "Sauvegarder la macro actuelle avant de créer une nouvelle ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_macro():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.recorder.actions.clear()
        self.action_list.clear()
        self.current_macro_file = None
        self.update_actions_info()
        self.statusBar().showMessage("Nouvelle macro créée")

    def open_macro(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir une macro",
            "", "Fichiers macro (*.json);;Tous les fichiers (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.recorder.actions = [MacroAction.from_dict(action_data) for action_data in data['actions']]
                self.current_macro_file = file_path

                self.action_list.clear()
                for action in self.recorder.actions:
                    self.action_list.add_action(action)

                self.update_actions_info()
                self.play_btn.setEnabled(len(self.recorder.actions) > 0)
                self.statusBar().showMessage(f"Macro chargée: {Path(file_path).name}")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le fichier:\n{str(e)}")

    def save_macro(self):
        if not self.current_macro_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Sauvegarder la macro",
                "", "Fichiers macro (*.json);;Tous les fichiers (*)"
            )
            if not file_path:
                return False
            if not file_path.endswith('.json'):
                file_path += '.json'
            self.current_macro_file = file_path

        try:
            data = {
                'version': '2.1',
                'created_at': time.time(),
                'action_count': len(self.recorder.actions),
                'theme': 'dark' if self.is_dark_mode else 'light',
                'actions': [action.to_dict() for action in self.recorder.actions]
            }

            with open(self.current_macro_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.statusBar().showMessage(f"Macro sauvegardée: {Path(self.current_macro_file).name}")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder:\n{str(e)}")
            return False

    def clear_actions(self):
        if self.recorder.actions:
            reply = QMessageBox.question(
                self, "Effacer les actions",
                "Êtes-vous sûr de vouloir effacer toutes les actions ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.recorder.actions.clear()
                self.action_list.clear()
                self.update_actions_info()
                self.play_btn.setEnabled(False)
                self.statusBar().showMessage("Actions effacées")

    # Callbacks des événements
    def on_action_recorded(self, action):
        self.action_list.add_action(action)
        self.update_actions_info()

    def on_recording_stopped(self):
        self.record_btn.setEnabled(True)
        self.stop_record_btn.setEnabled(False)
        self.play_btn.setEnabled(len(self.recorder.actions) > 0)
        self.status_label.set_stopped()
        self.statusBar().showMessage("Enregistrement terminé")

    def on_playback_started(self):
        self.play_btn.setEnabled(False)
        self.stop_play_btn.setEnabled(True)
        self.status_label.set_playing()
        self.statusBar().showMessage("Lecture en cours...")

    def on_playback_finished(self):
        self.play_btn.setEnabled(True)
        self.stop_play_btn.setEnabled(False)
        self.status_label.set_stopped()
        self.statusBar().showMessage("Lecture terminée")

    def on_action_played(self, index):
        if 0 <= index < self.action_list.count():
            self.action_list.setCurrentRow(index)

    def on_error(self, message):
        QMessageBox.warning(self, "Erreur", message)
        self.statusBar().showMessage(f"Erreur: {message}")

    def update_speed_display(self, value):
        speed = value / 10.0
        self.speed_display.setText(f"{speed:.1f}x")

    def update_actions_info(self):
        count = len(self.recorder.actions)
        if count == 0:
            self.actions_info.setText("0 actions | 0.0s")
        else:
            total_time = max([action.timestamp for action in self.recorder.actions]) if self.recorder.actions else 0
            self.actions_info.setText(f"{count} actions | {total_time:.1f}s")

def run_regression_tests():
    """Tests de non-régression pour la nouvelle interface"""
    print("🧪 Tests de non-régression - Interface redesignée")
    print("=" * 60)

    test_results = []

    # Test 1: Thèmes
    try:
        light_theme = Theme.LIGHT
        dark_theme = Theme.DARK
        assert 'bg_primary' in light_theme
        assert 'bg_primary' in dark_theme
        assert light_theme['bg_primary'] != dark_theme['bg_primary']
        test_results.append("✅ Test thèmes: OK")
    except Exception as e:
        test_results.append(f"❌ Test thèmes: {e}")

    # Test 2: Structure MacroAction
    try:
        action = MacroAction("mouse_click", 1.0, {"x": 100, "y": 200, "button": "gauche"})
        display_text = action.get_display_text()
        assert "Clic gauche" in display_text
        test_results.append("✅ Test MacroAction: OK")
    except Exception as e:
        test_results.append(f"❌ Test MacroAction: {e}")

    # Test 3: Interface (création uniquement)
    try:
        app = QApplication.instance() or QApplication([])
        recorder = MacroRecorder()
        player = MacroPlayer()
        assert recorder is not None
        assert player is not None
        test_results.append("✅ Test objets core: OK")
    except Exception as e:
        test_results.append(f"❌ Test objets core: {e}")

    # Test 4: Sérialisation JSON
    try:
        action = MacroAction("key_press", 2.0, {"key": "space"})
        serialized = action.to_dict()
        deserialized = MacroAction.from_dict(serialized)
        assert deserialized.action_type == action.action_type
        test_results.append("✅ Test sérialisation: OK")
    except Exception as e:
        test_results.append(f"❌ Test sérialisation: {e}")

    # Affichage des résultats
    for result in test_results:
        print(result)

    success_count = sum(1 for r in test_results if r.startswith("✅"))
    total_count = len(test_results)

    print(f"\n🏆 Résultats: {success_count}/{total_count} tests réussis")
    print(f"📊 Taux de réussite: {success_count/total_count*100:.1f}%")

    return success_count == total_count

def main():
    """Fonction principale"""
    # Tests de régression
    run_regression_tests()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Création et affichage de la fenêtre
    window = MacroRecorderUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
