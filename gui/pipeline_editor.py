"""
Pipeline code editor with syntax highlighting
"""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import (QSyntaxHighlighter, QTextCharFormat, QFont, 
                        QColor, QPalette, QTextCursor)


class VidPipeSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for VidPipe language"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Define colors
        keyword_color = QColor(0, 0, 255)        # Blue
        function_color = QColor(128, 0, 128)     # Purple
        operator_color = QColor(255, 0, 0)       # Red
        comment_color = QColor(0, 128, 0)        # Green
        string_color = QColor(163, 21, 21)       # Dark red
        number_color = QColor(0, 0, 139)         # Dark blue
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(keyword_color)
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = ["with"]
        for keyword in keywords:
            pattern = QRegularExpression(f"\\b{keyword}\\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(function_color)
        function_format.setFontWeight(QFont.Weight.Bold)
        
        functions = [
            "webcam", "camera", "capture", "test-pattern",
            "grayscale", "gray", "blur", "edges", "threshold",
            "resize", "flip", "rotate", "crop", "brightness",
            "contrast", "hue", "saturation", "gamma", "histogram-eq",
            "morphology", "contours", "corners", "optical-flow",
            "display", "window", "save", "record"
        ]
        for function in functions:
            pattern = QRegularExpression(f"\\b{function}\\b")
            self.highlighting_rules.append((pattern, function_format))
        
        # Pipeline operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(operator_color)
        operator_format.setFontWeight(QFont.Weight.Bold)
        
        operators = [r"->", r"~>", r"=>", r"&>", r"\+>", r"\|"]
        for op in operators:
            pattern = QRegularExpression(op)
            self.highlighting_rules.append((pattern, operator_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(number_color)
        
        number_pattern = QRegularExpression(r"\\b\\d+(\\.\\d+)?\\b")
        self.highlighting_rules.append((number_pattern, number_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(string_color)
        
        string_pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((string_pattern, string_format))
        
        string_pattern2 = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((string_pattern2, string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(comment_color)
        comment_format.setFontItalic(True)
        
        comment_pattern = QRegularExpression(r"#.*")
        self.highlighting_rules.append((comment_pattern, comment_format))
    
    def highlightBlock(self, text):
        """Highlight a block of text"""
        for pattern, format_obj in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_obj)


class PipelineEditor(QTextEdit):
    """Enhanced text editor for VidPipe code"""
    
    text_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_editor()
        self.setup_syntax_highlighter()
        
        # Connect signals
        self.textChanged.connect(self.text_changed.emit)
    
    def setup_editor(self):
        """Set up editor appearance and behavior"""
        # Font
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Monaco", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tab settings
        tab_width = 4
        metrics = self.fontMetrics()
        self.setTabStopDistance(tab_width * metrics.horizontalAdvance(' '))
        
        # Line wrap
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Colors
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(248, 248, 248))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def setup_syntax_highlighter(self):
        """Set up syntax highlighting"""
        self.highlighter = VidPipeSyntaxHighlighter(self.document())
    
    def set_text(self, text: str):
        """Set editor text"""
        self.setPlainText(text)
    
    def get_text(self) -> str:
        """Get editor text"""
        return self.toPlainText()
    
    def insert_text(self, text: str):
        """Insert text at cursor position"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def keyPressEvent(self, event):
        """Handle key press events for auto-completion and indentation"""
        if event.key() == Qt.Key.Key_Tab:
            # Handle tab indentation
            cursor = self.textCursor()
            if cursor.hasSelection():
                # Indent selected lines
                self.indent_selection()
            else:
                # Insert tab
                cursor.insertText("    ")  # 4 spaces
            event.accept()
            return
        
        elif event.key() == Qt.Key.Key_Return:
            # Auto-indent on new line
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Count leading whitespace
            indent = 0
            for char in text:
                if char == ' ':
                    indent += 1
                elif char == '\t':
                    indent += 4
                else:
                    break
            
            # Insert newline and indentation
            cursor.insertText('\n' + ' ' * indent)
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def indent_selection(self):
        """Indent selected lines"""
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        
        while cursor.position() <= end:
            cursor.insertText("    ")  # 4 spaces
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
            end += 4  # Adjust for inserted spaces
    
    def get_current_line(self) -> str:
        """Get the current line text"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        return cursor.selectedText()
    
    def get_cursor_position(self) -> tuple:
        """Get cursor line and column position"""
        cursor = self.textCursor()
        block = cursor.block()
        line = block.blockNumber() + 1
        column = cursor.positionInBlock() + 1
        return line, column