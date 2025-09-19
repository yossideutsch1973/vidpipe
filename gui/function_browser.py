"""
Function browser widget for VidPipe GUI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
                            QLabel, QTextEdit, QSplitter, QLineEdit, QPushButton,
                            QHBoxLayout, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from vidpipe.functions import FunctionRegistry


class FunctionBrowser(QWidget):
    """Widget for browsing and inserting functions"""
    
    function_selected = pyqtSignal(str, dict)
    
    def __init__(self):
        super().__init__()
        self.registry = FunctionRegistry()
        self.init_ui()
        self.populate_functions()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Functions")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search functions...")
        self.search_box.textChanged.connect(self.filter_functions)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)
        
        # Splitter for function list and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Function tree
        self.function_tree = QTreeWidget()
        self.function_tree.setHeaderLabel("Available Functions")
        self.function_tree.itemSelectionChanged.connect(self.on_function_selected)
        self.function_tree.itemDoubleClicked.connect(self.on_function_double_clicked)
        splitter.addWidget(self.function_tree)
        
        # Function details
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_layout.addWidget(QLabel("Function Details:"))
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        self.details_text.setFont(QFont("Consolas", 9))
        details_layout.addWidget(self.details_text)
        
        # Insert button
        self.insert_button = QPushButton("Insert Function")
        self.insert_button.setEnabled(False)
        self.insert_button.clicked.connect(self.insert_function)
        details_layout.addWidget(self.insert_button)
        
        splitter.addWidget(details_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 200])
    
    def populate_functions(self):
        """Populate the function tree"""
        functions = self.registry.list_functions()
        
        # Group functions by category
        categories = {
            "Sources": [],
            "Processors": [],
            "Sinks": []
        }
        
        for name, func_def in functions.items():
            if func_def.is_source:
                categories["Sources"].append((name, func_def))
            elif func_def.is_sink:
                categories["Sinks"].append((name, func_def))
            else:
                categories["Processors"].append((name, func_def))
        
        # Add categories to tree
        for category, func_list in categories.items():
            if not func_list:
                continue
            
            category_item = QTreeWidgetItem(self.function_tree)
            category_item.setText(0, category)
            category_item.setExpanded(True)
            
            for name, func_def in sorted(func_list):
                func_item = QTreeWidgetItem(category_item)
                func_item.setText(0, name)
                func_item.setData(0, Qt.ItemDataRole.UserRole, func_def)
        
        # Expand all by default
        self.function_tree.expandAll()
    
    def filter_functions(self, text: str):
        """Filter functions based on search text"""
        text = text.lower()
        
        def filter_item(item: QTreeWidgetItem):
            """Recursively filter items"""
            visible = False
            
            # Check children first
            for i in range(item.childCount()):
                child = item.child(i)
                if filter_item(child):
                    visible = True
            
            # Check this item
            if text in item.text(0).lower():
                visible = True
            
            item.setHidden(not visible)
            return visible
        
        # Filter all root items
        for i in range(self.function_tree.topLevelItemCount()):
            root_item = self.function_tree.topLevelItem(i)
            filter_item(root_item)
    
    def on_function_selected(self):
        """Handle function selection"""
        items = self.function_tree.selectedItems()
        if not items:
            self.details_text.clear()
            self.insert_button.setEnabled(False)
            return
        
        item = items[0]
        func_def = item.data(0, Qt.ItemDataRole.UserRole)
        
        if func_def:
            self.show_function_details(func_def)
            self.insert_button.setEnabled(True)
        else:
            self.details_text.clear()
            self.insert_button.setEnabled(False)
    
    def show_function_details(self, func_def):
        """Show details for the selected function"""
        details = f"Name: {func_def.name}\n"
        details += f"Type: {'Source' if func_def.is_source else 'Sink' if func_def.is_sink else 'Processor'}\n"
        
        if func_def.description:
            details += f"Description: {func_def.description}\n"
        
        details += "\nUsage:\n"
        
        if func_def.is_source:
            details += f"  {func_def.name} -> next-function\n"
        elif func_def.is_sink:
            details += f"  previous-function -> {func_def.name}\n"
        else:
            details += f"  previous-function -> {func_def.name} -> next-function\n"
        
        params = func_def.parameters if hasattr(func_def, 'parameters') else {}
        if params:
            details += "\nParameters:\n"
            for param, description in params.items():
                details += f"  {param}: {description}\n"

            details += f"\nWith parameters:\n"
            details += f"  {func_def.name} with ({', '.join(f'{k}: value' for k in params.keys())})\n"

        self.details_text.setPlainText(details)
    
    def on_function_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on function"""
        self.insert_function()
    
    def insert_function(self):
        """Insert the selected function"""
        items = self.function_tree.selectedItems()
        if not items:
            return
        
        item = items[0]
        func_def = item.data(0, Qt.ItemDataRole.UserRole)
        
        if func_def:
            params = func_def.parameters if hasattr(func_def, 'parameters') else {}
            self.function_selected.emit(func_def.name, params)