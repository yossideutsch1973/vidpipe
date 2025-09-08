"""
Visual pipeline editor widget
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView,
                            QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                            QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
                            QPushButton, QLabel, QToolBar)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QFont, QPainter, QColor


class PipelineNodeItem(QGraphicsRectItem):
    """Visual representation of a pipeline node"""
    
    def __init__(self, name: str, node_type: str = "processor"):
        super().__init__()
        
        self.name = name
        self.node_type = node_type
        
        # Set up appearance
        self.setRect(0, 0, 120, 60)
        self.setup_style()
        
        # Add text
        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setPos(10, 20)
        font = QFont("Arial", 10)
        self.text_item.setFont(font)
        
        # Make it movable and selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
    
    def setup_style(self):
        """Set up node appearance based on type"""
        if self.node_type == "source":
            # Green for sources
            self.setBrush(QBrush(QColor(144, 238, 144)))
            self.setPen(QPen(QColor(0, 128, 0), 2))
        elif self.node_type == "sink":
            # Red for sinks
            self.setBrush(QBrush(QColor(255, 182, 193)))
            self.setPen(QPen(QColor(139, 0, 0), 2))
        else:
            # Blue for processors
            self.setBrush(QBrush(QColor(173, 216, 230)))
            self.setPen(QPen(QColor(0, 0, 139), 2))
    
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # Update connections when moved
            scene = self.scene()
            if scene and hasattr(scene, 'update_connections'):
                scene.update_connections()
        
        return super().itemChange(change, value)


class PipelineConnectionItem(QGraphicsLineItem):
    """Visual representation of a pipeline connection"""
    
    def __init__(self, source_node, target_node, connection_type: str = "sync"):
        super().__init__()
        
        self.source_node = source_node
        self.target_node = target_node
        self.connection_type = connection_type
        
        self.setup_style()
        self.update_line()
    
    def setup_style(self):
        """Set up connection appearance"""
        if self.connection_type == "async":
            # Dashed line for async
            pen = QPen(QColor(255, 165, 0), 2, Qt.PenStyle.DashLine)
        elif self.connection_type == "parallel":
            # Thick line for parallel
            pen = QPen(QColor(128, 0, 128), 3)
        else:
            # Solid line for sync
            pen = QPen(QColor(0, 0, 0), 2)
        
        self.setPen(pen)
    
    def update_line(self):
        """Update line position based on node positions"""
        if self.source_node and self.target_node:
            source_rect = self.source_node.sceneBoundingRect()
            target_rect = self.target_node.sceneBoundingRect()
            
            # Connect from right side of source to left side of target
            source_point = QPointF(source_rect.right(), source_rect.center().y())
            target_point = QPointF(target_rect.left(), target_rect.center().y())
            
            self.setLine(source_point.x(), source_point.y(),
                        target_point.x(), target_point.y())


class PipelineScene(QGraphicsScene):
    """Custom graphics scene for pipeline editing"""
    
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.connections = []
    
    def add_pipeline_node(self, name: str, node_type: str = "processor", 
                         position: QPointF = None):
        """Add a pipeline node to the scene"""
        node = PipelineNodeItem(name, node_type)
        
        if position:
            node.setPos(position)
        else:
            # Auto-position
            x = len(self.nodes) * 150 + 50
            y = 100
            node.setPos(x, y)
        
        self.addItem(node)
        self.nodes.append(node)
        return node
    
    def add_pipeline_connection(self, source_node, target_node, 
                              connection_type: str = "sync"):
        """Add a connection between two nodes"""
        connection = PipelineConnectionItem(source_node, target_node, connection_type)
        self.addItem(connection)
        self.connections.append(connection)
        return connection
    
    def update_connections(self):
        """Update all connection positions"""
        for connection in self.connections:
            connection.update_line()
    
    def clear_pipeline(self):
        """Clear all nodes and connections"""
        self.clear()
        self.nodes = []
        self.connections = []
    
    def get_pipeline_code(self) -> str:
        """Generate VidPipe code from the visual pipeline"""
        if not self.nodes:
            return ""
        
        # Simple linear pipeline for now
        # In a full implementation, this would handle complex topologies
        code_parts = []
        
        for i, node in enumerate(self.nodes):
            code_parts.append(node.name)
            if i < len(self.nodes) - 1:
                code_parts.append(" -> ")
        
        return "".join(code_parts)


class PipelineVisualizer(QWidget):
    """Visual pipeline editor widget"""
    
    code_generated = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.add_source_btn = QPushButton("Add Source")
        self.add_source_btn.clicked.connect(lambda: self.add_node("webcam", "source"))
        toolbar_layout.addWidget(self.add_source_btn)
        
        self.add_processor_btn = QPushButton("Add Processor")
        self.add_processor_btn.clicked.connect(lambda: self.add_node("grayscale", "processor"))
        toolbar_layout.addWidget(self.add_processor_btn)
        
        self.add_sink_btn = QPushButton("Add Sink")
        self.add_sink_btn.clicked.connect(lambda: self.add_node("display", "sink"))
        toolbar_layout.addWidget(self.add_sink_btn)
        
        toolbar_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_pipeline)
        toolbar_layout.addWidget(self.clear_btn)
        
        self.generate_code_btn = QPushButton("Generate Code")
        self.generate_code_btn.clicked.connect(self.generate_code)
        toolbar_layout.addWidget(self.generate_code_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Graphics view
        self.scene = PipelineScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        layout.addWidget(self.view)
        
        # Status
        self.status_label = QLabel("Drop functions here to build your pipeline")
        layout.addWidget(self.status_label)
        
        # Load example
        self.load_example_pipeline()
    
    def add_node(self, name: str, node_type: str, position: QPointF = None):
        """Add a node to the pipeline"""
        node = self.scene.add_pipeline_node(name, node_type, position)
        self.status_label.setText(f"Added {node_type}: {name}")
        return node
    
    def clear_pipeline(self):
        """Clear the pipeline"""
        self.scene.clear_pipeline()
        self.status_label.setText("Pipeline cleared")
    
    def generate_code(self):
        """Generate VidPipe code from visual pipeline"""
        code = self.scene.get_pipeline_code()
        if code:
            self.code_generated.emit(code)
            self.status_label.setText("Code generated")
        else:
            self.status_label.setText("No pipeline to generate")
    
    def load_example_pipeline(self):
        """Load an example visual pipeline"""
        # Create a simple example: webcam -> grayscale -> edges -> display
        webcam = self.add_node("webcam", "source", QPointF(50, 100))
        grayscale = self.add_node("grayscale", "processor", QPointF(200, 100))
        edges = self.add_node("edges", "processor", QPointF(350, 100))
        display = self.add_node("display", "sink", QPointF(500, 100))
        
        # Connect them
        self.scene.add_pipeline_connection(webcam, grayscale)
        self.scene.add_pipeline_connection(grayscale, edges)
        self.scene.add_pipeline_connection(edges, display)
        
        self.status_label.setText("Example pipeline loaded")
    
    def set_pipeline_from_code(self, code: str):
        """Set visual pipeline from code (future feature)"""
        # This would parse the code and create visual nodes
        # For now, just a placeholder
        self.status_label.setText(f"Code import not yet implemented: {code[:50]}...")
    
    def mousePressEvent(self, event):
        """Handle mouse press for adding nodes"""
        if event.button() == Qt.MouseButton.RightButton:
            # Right-click context menu (future feature)
            pass
        
        super().mousePressEvent(event)