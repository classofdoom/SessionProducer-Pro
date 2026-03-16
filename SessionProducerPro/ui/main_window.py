# Author: Tresslers Group

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QStatusBar, QMenuBar)
from PyQt6.QtCore import Qt

# Import panels (will be created next)
from .chat_panel import ChatPanel
# from .asset_browser_panel import AssetBrowserPanel 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SessionProducer Pro")
        self.resize(1200, 800)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Splitter to allow resizing
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Panels
        self.chat_panel = ChatPanel()
        self.splitter.addWidget(self.chat_panel)
        
        # Asset Panel (Created here to avoid redundancy)
        from .asset_browser_panel import AssetBrowserPanel
        self.asset_panel = AssetBrowserPanel()
        self.splitter.addWidget(self.asset_panel)
        
        # Set initial sizes (Chat: 40%, Assets: 60%)
        self.splitter.setSizes([450, 750])
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("System Ready")
        
        # Apply Premium Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f1115;
                color: #e0e0e0;
            }
            QSplitter::handle {
                background-color: #1a1d23;
                width: 1px;
            }
            QMenuBar {
                background-color: #0f1115;
                color: #a0a0a0;
                border-bottom: 1px solid #1a1d23;
            }
            QMenuBar::item:selected {
                background-color: #1a1d23;
            }
            QStatusBar {
                background-color: #0f1115;
                color: #606060;
                border-top: 1px solid #1a1d23;
                font-size: 11px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set default font
    from PyQt6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

