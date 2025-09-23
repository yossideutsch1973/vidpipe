#!/usr/bin/env python3
"""
CLI entry point for VidPipe
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
            print(f"Error: Pipeline file '{args.file}' not found")
            return 1
        except Exception as e:
            print(f"Error reading pipeline file: {e}")
            return 1
    else:
        print("Error: No pipeline code or file specified")
        return 1

    try:
        # Tokenize
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        if args.tokens:
            print("Tokens:")
            for token in tokens:
                if token.type.name != "EOF":
                    print(f"  {token.type.name}: {token.value}")
            return 0
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        if args.ast:
            print("AST:")
            print(f"  Main pipeline: {ast.main_pipeline}")
            print(f"  Definitions: {len(ast.definitions)}")
            for definition in ast.definitions:
                print(f"    {definition.name}: {definition.expression}")
            return 0
        
        # Execute
        runtime = Runtime()
        pipeline = runtime.compile(ast)
        
        if pipeline:
            print(f"Running pipeline with {len(pipeline.nodes)} nodes...")
            pipeline.start()
            
            # Wait for completion or user interrupt
            try:
                pipeline.wait_for_completion()
            except KeyboardInterrupt:
                print("\nStopping pipeline...")
                pipeline.stop()
            finally:
                _display_manager.cleanup()
        else:
            print("Error: Failed to compile pipeline")
            return 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="VidPipe - Functional Pipeline Language for Video Processing"
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--gui", action="store_true", help="Launch GUI mode")
    mode_group.add_argument("--cli", action="store_true", help="Run in CLI mode (default)")
    
    # Input options
    parser.add_argument("-c", "--code", help="Pipeline code to execute")
    parser.add_argument("-f", "--file", help="Pipeline file to execute")
    parser.add_argument("-m", "--multi", help="Multi-pipeline file to execute")
    
    # Output options
    parser.add_argument("--tokens", action="store_true", help="Show tokens and exit")
    parser.add_argument("--ast", action="store_true", help="Show AST and exit")
    
    args = parser.parse_args()
    
    # Default to CLI mode if no mode specified
    if not args.gui and not args.cli:
        args.cli = True
    
    if args.gui:
        try:
            from vidpipe.gui_main import run_gui
            return run_gui(args)
        except ImportError:
            print("Error: GUI dependencies not available. Install with: pip install vidpipe[gui]")
            return 1
    else:
        return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())