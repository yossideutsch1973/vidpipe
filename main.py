#!/usr/bin/env python3
"""
Main entry point for VidPipe
"""

import sys
import argparse
from vidpipe import Lexer, Parser, Runtime, execute_multi_pipeline_file
from vidpipe.functions import _display_manager


def run_cli(args):
    """Run VidPipe from command line"""
    if args.multi:
        # Handle multi-pipeline file
        try:
            print(f"Executing multi-pipeline file: {args.multi}")
            execute_multi_pipeline_file(args.multi)
            return 0
        except FileNotFoundError:
            print(f"Error: Multi-pipeline file '{args.multi}' not found")
            return 1
        except Exception as e:
            print(f"Error executing multi-pipeline file: {e}")
            return 1

    elif args.code:
        code = args.code
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    else:
        print("Error: Either --code, --file, or --multi must be specified")
        return 1
    
    try:
        # Parse and execute
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        if args.tokens:
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
            return 0
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if args.ast:
            print("AST:")
            print(f"  {ast}")
            return 0
        
        # Execute pipeline
        runtime = Runtime()
        runtime.execute(ast, pump_display=_display_manager.process_display_queue)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def run_gui():
    """Run VidPipe GUI"""
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("VidPipe")
        app.setApplicationVersion("0.1.0")
        
        window = MainWindow()
        window.show()
        
        return app.exec()
        
    except ImportError:
        print("Error: PyQt6 is required for GUI mode")
        print("Install with: pip install PyQt6")
        return 1


def main():
    parser = argparse.ArgumentParser(description='VidPipe - Functional Pipeline Language for Video Processing')
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--gui', action='store_true', help='Launch GUI mode')
    mode_group.add_argument('--cli', action='store_true', help='Run in CLI mode (default)')
    
    # CLI options
    parser.add_argument('-c', '--code', type=str, help='Pipeline code to execute')
    parser.add_argument('-f', '--file', type=str, help='Pipeline file to execute')
    parser.add_argument('-m', '--multi', type=str, help='Multi-pipeline file to execute')
    
    # Debug options
    parser.add_argument('--tokens', action='store_true', help='Show tokens and exit')
    parser.add_argument('--ast', action='store_true', help='Show AST and exit')
    
    args = parser.parse_args()
    
    # Default to CLI if no mode specified and code/file/multi provided
    if not args.gui and not args.cli and (args.code or args.file or args.multi):
        args.cli = True
    
    # Default to GUI if no mode specified and no code/file
    if not args.gui and not args.cli:
        args.gui = True
    
    if args.gui:
        return run_gui()
    else:
        return run_cli(args)


if __name__ == '__main__':
    sys.exit(main())