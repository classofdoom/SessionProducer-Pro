# Author: Tresslers Group

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
                             QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal

class ChatPanel(QWidget):
    message_sent = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0f12;
            }
        """)
        
        # Header
        self.header = QLabel("SESSION ASSISTANT")
        self.header.setStyleSheet("""
            font-weight: 900; 
            font-size: 11px; 
            letter-spacing: 3px;
            color: #4a9eff; 
            padding-bottom: 8px;
            border-bottom: 1px solid #1a1d23;
        """)
        self.layout.addWidget(self.header)
        
        # Chat History Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #090b0e;
                color: #b0b0b0;
                border: 1px solid #1a1d23;
                border-radius: 4px;
                padding: 12px;
                font-size: 13px;
            }
        """)
        self.layout.addWidget(self.chat_display)
        
        # Input Area (Horizontal layout for Input + Mic)
        self.input_container = QWidget()
        self.input_layout = QVBoxLayout(self.input_container) # Vertical wrapper
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.h_input_layout = QHBoxLayout()
        self.h_input_layout.setSpacing(5)
        
        self.msg_input = QLineEdit()
        self.msg_input.setPlaceholderText("Direct your session...")
        self.msg_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1d23;
                color: #ffffff;
                border: 1px solid #2a2d33;
                padding: 10px;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
            }
        """)
        self.msg_input.returnPressed.connect(self.send_message)
        self.h_input_layout.addWidget(self.msg_input)
        
        self.mic_btn = QPushButton("ðŸŽ¤")
        self.mic_btn.setFixedWidth(40)
        self.mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1d23;
                border: 1px solid #2a2d33;
                font-size: 18px;
                padding: 5px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2a2d33;
                border: 1px solid #4a9eff;
            }
        """)
        self.mic_btn.clicked.connect(lambda: self.mic_requested.emit())
        self.h_input_layout.addWidget(self.mic_btn)
        
        self.input_layout.addLayout(self.h_input_layout)
        
        self.send_btn = QPushButton("EXECUTE COMMAND")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: #0f1115;
                font-weight: bold;
                border: none;
                padding: 10px;
                border-radius: 6px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #6ab0ff;
            }
            QPushButton:pressed {
                background-color: #3a7ecd;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.send_btn)
        
        self.layout.addWidget(self.input_container)

    mic_requested = pyqtSignal()

    def set_recording_state(self, active: bool):
        if active:
            self.mic_btn.setText("ðŸ”´") # Recording indicator
            self.mic_btn.setStyleSheet(self.mic_btn.styleSheet() + "border: 1px solid #ff4a4a;")
            self.msg_input.setPlaceholderText("Listening...")
        else:
            self.mic_btn.setText("ðŸŽ¤")
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1a1d23;
                    border: 1px solid #2a2d33;
                    font-size: 18px;
                    padding: 5px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #2a2d33;
                    border: 1px solid #4a9eff;
                }
            """)
            self.msg_input.setPlaceholderText("Direct your session...")

    def send_message(self):
        text = self.msg_input.text().strip()
        if text:
            self.append_message("User", text)
            self.message_sent.emit(text)
            self.msg_input.clear()

    def append_message(self, sender: str, text: str):
        color = "#4ec9b0" if sender == "System" else "#ce9178"
        formatted = f'<div style="margin-bottom: 5px;"><b style="color:{color};">{sender}:</b> {text}</div>'
        self.chat_display.append(formatted)

