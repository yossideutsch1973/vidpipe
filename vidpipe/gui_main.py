#!/usr/bin/env python3
"""
GUI entry point for VidPipe
"""

import sys


def run_gui(args):
    """Run VidPipe GUI"""
    try:
        # Import GUI components
        from gui.main_window import VidPipeMainWindow
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # Set up QApplication
        app = QApplication(sys.argv)
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        
        # Create and show main window
        window = VidPipeMainWindow()
        window.show()
        
        # Run the application
        return app.exec()
        
    except ImportError as e:
        print(f"Error: GUI dependencies not available: {e}")
        print("Install with: pip install vidpipe[gui]")
        return 1
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1


def main():
    """GUI-only entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VidPipe GUI - Visual Pipeline Editor"
    )
    args = parser.parse_args()
    
    return run_gui(args)


if __name__ == "__main__":
    sys.exit(main())