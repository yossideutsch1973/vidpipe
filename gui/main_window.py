"""
Main window for VidPipe GUI
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QSplitter, QTextEdit, QPushButton, QLabel,
                            QMenuBar, QMenu, QFileDialog, QMessageBox, QStatusBar,
                            QToolBar, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon

from vidpipe import Lexer, Parser, Runtime, execute_multi_pipeline_file
from vidpipe.functions import _display_manager
from .pipeline_editor import PipelineEditor
from .function_browser import FunctionBrowser
from .pipeline_visualizer import PipelineVisualizer


class PipelineRunner(QThread):
    """Thread for running pipelines"""
    
    output_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, code: str):
        super().__init__()
        self.code = code
        self.should_stop = False
    
    def run(self):
        try:
            # Parse and execute the pipeline
            lexer = Lexer(self.code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            runtime = Runtime()

            self.output_signal.emit("Starting pipeline execution...")

            # Store runtime reference for stopping
            self.runtime = runtime
            runtime.execute(ast)

        except Exception as e:
            self.error_signal.emit(f"Error: {str(e)}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        self.should_stop = True
        # Try to stop the runtime if it exists
        if hasattr(self, 'runtime'):
            try:
                # Force stop the runtime
                self.runtime.pipeline.stop()
            except Exception:
                pass  # Ignore errors during emergency stop


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pipeline_runner = None
        self.current_file = None

        self.init_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        # Set up display queue processing timer
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.process_display_queue)
        self.display_timer.start(30)  # Process every 30ms

        # Load example pipeline
        self.load_example()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("VidPipe - Visual Pipeline Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel - Function browser
        self.function_browser = FunctionBrowser()
        main_splitter.addWidget(self.function_browser)
        
        # Center panel - Editor and visualizer
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Tab widget for editor modes
        self.tab_widget = QTabWidget()
        
        # Text editor tab
        self.pipeline_editor = PipelineEditor()
        self.tab_widget.addTab(self.pipeline_editor, "Code Editor")
        
        # Visual editor tab (placeholder for now)
        self.pipeline_visualizer = PipelineVisualizer()
        self.tab_widget.addTab(self.pipeline_visualizer, "Visual Editor")
        
        center_layout.addWidget(self.tab_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Pipeline")
        self.run_button.clicked.connect(self.run_pipeline)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.stop_button = QPushButton("Stop Pipeline")
        self.stop_button.clicked.connect(self.stop_pipeline)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.validate_button = QPushButton("Validate Syntax")
        self.validate_button.clicked.connect(self.validate_syntax)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.validate_button)
        button_layout.addStretch()
        
        center_layout.addLayout(button_layout)
        main_splitter.addWidget(center_widget)
        
        # Right panel - Output and status
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Output console
        right_layout.addWidget(QLabel("Output:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        self.output_text.setFont(QFont("Consolas", 9))
        right_layout.addWidget(self.output_text)
        
        # Error console
        right_layout.addWidget(QLabel("Errors:"))
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumHeight(150)
        self.error_text.setFont(QFont("Consolas", 9))
        self.error_text.setStyleSheet("QTextEdit { background-color: #ffe6e6; }")
        right_layout.addWidget(self.error_text)
        
        right_layout.addStretch()
        main_splitter.addWidget(right_widget)
        
        # Set splitter proportions
        main_splitter.setSizes([250, 600, 350])
        
        # Connect editor signals
        self.pipeline_editor.text_changed.connect(self.on_code_changed)
    
    def create_menus(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        open_multi_action = QAction('Open &Multi-Pipeline...', self)
        open_multi_action.setShortcut('Ctrl+Shift+O')
        open_multi_action.triggered.connect(self.open_multi_pipeline)
        file_menu.addAction(open_multi_action)
        
        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Save &As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.pipeline_editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('&Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.pipeline_editor.redo)
        edit_menu.addAction(redo_action)
        
        # Pipeline menu
        pipeline_menu = menubar.addMenu('&Pipeline')
        
        run_action = QAction('&Run', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_pipeline)
        pipeline_menu.addAction(run_action)
        
        stop_action = QAction('&Stop', self)
        stop_action.setShortcut('Ctrl+C')
        stop_action.triggered.connect(self.stop_pipeline)
        pipeline_menu.addAction(stop_action)
        
        validate_action = QAction('&Validate', self)
        validate_action.setShortcut('F7')
        validate_action.triggered.connect(self.validate_syntax)
        pipeline_menu.addAction(validate_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # File menu - add exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = self.addToolBar('Main')
        
        # File actions
        toolbar.addAction('New', self.new_file)
        toolbar.addAction('Open', self.open_file)
        toolbar.addAction('Save', self.save_file)
        toolbar.addSeparator()
        
        # Pipeline actions
        toolbar.addAction('Run', self.run_pipeline)
        toolbar.addAction('Stop', self.stop_pipeline)
        toolbar.addAction('Validate', self.validate_syntax)
    
    def create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage('Ready')
    
    def load_example(self):
        """Load an example pipeline"""
        example_code = """# Simple webcam edge detection
webcam -> grayscale -> edges -> display

# Alternative syntax with parameters
# webcam with (device: 0) -> blur with (kernel_size: 5) -> display with (window_name: "Blurred")"""
        
        self.pipeline_editor.set_text(example_code)
    
    def new_file(self):
        """Create new file"""
        self.pipeline_editor.clear()
        self.current_file = None
        self.setWindowTitle("VidPipe - Visual Pipeline Editor")
    
    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Pipeline File', '',
            'VidPipe Files (*.vp);;All Files (*)'
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.pipeline_editor.set_text(content)
                self.current_file = file_path
                self.setWindowTitle(f"VidPipe - {file_path}")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not open file:\n{str(e)}')

    def open_multi_pipeline(self):
        """Open multi-pipeline file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Multi-Pipeline File', '',
            'VidPipe Multi Files (*.vp);;All Files (*)'
        )

        if file_path:
            try:
                # Execute the multi-pipeline file
                self.statusBar().showMessage(f'Executing multi-pipeline: {file_path}')
                self.output_text.clear()
                self.error_text.clear()

                # Run in a separate thread to avoid blocking the GUI
                from PyQt6.QtCore import QThread, pyqtSignal

                class MultiPipelineRunner(QThread):
                    output_signal = pyqtSignal(str)
                    error_signal = pyqtSignal(str)
                    finished_signal = pyqtSignal()

                    def __init__(self, file_path):
                        super().__init__()
                        self.file_path = file_path

                    def run(self):
                        try:
                            self.output_signal.emit(f"Executing multi-pipeline file: {self.file_path}")
                            execute_multi_pipeline_file(self.file_path)
                            self.output_signal.emit("Multi-pipeline execution completed!")
                        except Exception as e:
                            self.error_signal.emit(f"Multi-pipeline error: {str(e)}")
                        finally:
                            self.finished_signal.emit()

                # Create and start the runner
                self.multi_runner = MultiPipelineRunner(file_path)
                self.multi_runner.output_signal.connect(self.output_text.append)
                self.multi_runner.error_signal.connect(self.error_text.append)
                self.multi_runner.finished_signal.connect(self.on_multi_pipeline_finished)
                self.multi_runner.start()

                self.run_button.setEnabled(False)
                self.stop_button.setEnabled(True)

            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not execute multi-pipeline file:\n{str(e)}')
    
    def save_file(self):
        """Save current file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save as dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Pipeline File', '', 
            'VidPipe Files (*.vp);;All Files (*)'
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.setWindowTitle(f"VidPipe - {file_path}")
    
    def save_to_file(self, file_path: str):
        """Save content to file"""
        try:
            with open(file_path, 'w') as f:
                f.write(self.pipeline_editor.get_text())
            self.statusBar().showMessage(f'Saved {file_path}', 2000)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not save file:\n{str(e)}')
    
    def run_pipeline(self):
        """Run the current pipeline"""
        code = self.pipeline_editor.get_text().strip()
        if not code:
            self.error_text.append("No pipeline code to run")
            return
        
        # Clear outputs
        self.output_text.clear()
        self.error_text.clear()
        
        # Start pipeline runner
        self.pipeline_runner = PipelineRunner(code)
        self.pipeline_runner.output_signal.connect(self.output_text.append)
        self.pipeline_runner.error_signal.connect(self.error_text.append)
        self.pipeline_runner.finished_signal.connect(self.on_pipeline_finished)
        
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.statusBar().showMessage('Running pipeline...')
        
        self.pipeline_runner.start()
    
    def stop_pipeline(self):
        """Stop the current pipeline"""
        if self.pipeline_runner:
            # First try graceful stop
            self.pipeline_runner.stop()

            # Wait for thread to finish
            if self.pipeline_runner.isRunning():
                self.pipeline_runner.wait(2000)  # Wait up to 2 seconds

                # If still running, force terminate
                if self.pipeline_runner.isRunning():
                    self.pipeline_runner.terminate()
                    self.pipeline_runner.wait(1000)  # Wait 1 more second

        self.on_pipeline_finished()
    
    def on_pipeline_finished(self):
        """Handle pipeline finished"""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage('Pipeline finished - ready for next run', 2000)

    def on_multi_pipeline_finished(self):
        """Handle multi-pipeline finished"""
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.statusBar().showMessage('Multi-pipeline finished - ready for next run', 2000)
        if hasattr(self, 'multi_runner'):
            delattr(self, 'multi_runner')
    
    def validate_syntax(self):
        """Validate pipeline syntax"""
        code = self.pipeline_editor.get_text().strip()
        if not code:
            self.error_text.append("No code to validate")
            return
        
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            self.output_text.append("✓ Syntax is valid")
            self.error_text.clear()
            self.statusBar().showMessage('Syntax valid', 2000)
            
        except Exception as e:
            self.error_text.clear()
            self.error_text.append(f"Syntax error: {str(e)}")
            self.statusBar().showMessage('Syntax error', 2000)
    
    def on_code_changed(self):
        """Handle code changes"""
        # Auto-validate on change (with delay)
        if not hasattr(self, 'validation_timer'):
            self.validation_timer = QTimer()
            self.validation_timer.timeout.connect(self.validate_syntax)
            self.validation_timer.setSingleShot(True)
        
        self.validation_timer.stop()
        self.validation_timer.start(1000)  # Validate after 1 second of inactivity

    def process_display_queue(self):
        """Process the display queue in the main GUI thread"""
        try:
            result = _display_manager.process_display_queue()
            if result is False:
                # User pressed 'q' or ESC in display window
                self.statusBar().showMessage('Display window closed - pipeline stopped')
                if self.pipeline_runner and self.pipeline_runner.isRunning():
                    # Stop the pipeline but keep GUI open
                    self.stop_pipeline()
                    self.statusBar().showMessage('Pipeline stopped - ready for next run')
        except Exception as e:
            self.error_text.append(f"Display error: {e}")
            self.statusBar().showMessage('Display error occurred')

    def closeEvent(self, event):
        """Clean up when window is closed"""
        self.statusBar().showMessage('Closing application...')

        # Stop the display timer
        if hasattr(self, 'display_timer'):
            self.display_timer.stop()

        # Stop any running pipeline
        if self.pipeline_runner and self.pipeline_runner.isRunning():
            self.statusBar().showMessage('Stopping pipeline...')
            self.stop_pipeline()

        # Clean up OpenCV windows
        import cv2
        cv2.destroyAllWindows()

        # Accept the close event to allow the window to close
        event.accept()

        # Force quit the Qt application after a short delay
        # This ensures the application terminates even if there are hanging threads
        from PyQt6.QtCore import QTimer, QCoreApplication
        QTimer.singleShot(200, QCoreApplication.quit)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, 'About VidPipe',
            """VidPipe - Visual Pipeline Editor
            
A functional pipeline language for real-time video processing.

Features:
• Intuitive pipeline syntax
• Real-time video processing
• Parallel execution
• Extensible function library

Version 0.1.0""")