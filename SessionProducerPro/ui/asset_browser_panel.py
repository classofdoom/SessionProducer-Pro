# Author: Tresslers Group

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QLineEdit, QPushButton, QHBoxLayout, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal

class AssetBrowserPanel(QWidget):
    scan_requested = pyqtSignal()
    
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
        
        # Search Bar
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("FILTER LIBRARY...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1d23;
                color: #ffffff;
                border: 1px solid #2a2d33;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QLineEdit:focus {
                border: 1px solid #4a9eff;
            }
        """)
        self.search_layout.addWidget(self.search_input)
        
        self.refresh_btn = QPushButton("SCAN")
        self.refresh_btn.clicked.connect(lambda: self.scan_requested.emit())
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2d33;
                color: #e0e0e0;
                border: 1px solid #3a3d43;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3d43;
                border: 1px solid #4a4d53;
            }
        """)
        self.search_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(self.search_layout)
        
        # Asset Tree/List
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ASSET NAME", "BPM", "KEY", "CLASS"])
        self.tree.setIndentation(0)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #0f1115;
                color: #b0b0b0;
                border: 1px solid #1a1d23;
                border-radius: 6px;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1a1d23;
            }
            QTreeWidget::item:selected {
                background-color: #1a1d23;
                color: #4a9eff;
            }
            QHeaderView::section {
                background-color: #16191e;
                color: #606060;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #1a1d23;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setColumnWidth(1, 60)
        self.tree.setColumnWidth(2, 60)
        self.tree.setColumnWidth(3, 80)
        
        self.layout.addWidget(self.tree)
        
        # Dummy Data for Visualization
        self.populate_dummy_data()

    def populate_dummy_data(self):
        # In real app, this comes from SQLite
        items = [
            ("Funky Drum Loop", "120", "Am", "Loop"),
            ("Deep Bass One Shot", "-", "C", "OneShot"),
            ("Analog Pad", "120", "G", "Patch"),
            ("Rock Guitar Riff", "110", "E", "Loop"),
        ]
        
        for name, bpm, key, cat in items:
            item = QTreeWidgetItem([name, bpm, key, cat])
            self.tree.addTopLevelItem(item)

    def add_asset(self, asset_data):
        item = QTreeWidgetItem([
            asset_data.get("filename", "Unknown"),
            str(asset_data.get("bpm", "-")),
            str(asset_data.get("key", "-")),
            asset_data.get("category", "-")
        ])
        self.tree.addTopLevelItem(item)

