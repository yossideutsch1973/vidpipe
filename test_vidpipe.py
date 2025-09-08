#!/usr/bin/env python3
"""
Test script for VidPipe functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vidpipe import Lexer, Parser, Runtime
from vidpipe.functions import FunctionRegistry


def test_lexer():
    """Test the lexer with various inputs"""
    print("=== Testing Lexer ===")
    
    test_cases = [
        "webcam -> display",
        "webcam -> grayscale -> edges -> display",
        "test-pattern with (width: 640, height: 480) -> display",
        "webcam -> (edges | blur) -> display",
        "{webcam -> display}",
        "webcam [10]-> heavy-processing ~> display"
    ]
    
    for i, code in enumerate(test_cases):
        print(f"\nTest {i+1}: {code}")
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            print("Tokens:")
            for token in tokens:
                if token.type.name != 'EOF':
                    print(f"  {token.type.name}: {token.value}")
        except Exception as e:
            print(f"  Error: {e}")


def test_parser():
    """Test the parser with various inputs"""
    print("\n\n=== Testing Parser ===")
    
    test_cases = [
        "webcam -> display",
        "webcam -> grayscale -> edges -> display",
        "test-pattern -> display",
        "webcam -> (edges | blur) -> display"
    ]
    
    for i, code in enumerate(test_cases):
        print(f"\nTest {i+1}: {code}")
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            print(f"AST: {ast}")
        except Exception as e:
            print(f"  Error: {e}")


def test_functions():
    """Test function registry"""
    print("\n\n=== Testing Function Registry ===")
    
    registry = FunctionRegistry()
    functions = registry.list_functions()
    
    print("Available functions:")
    for name, func_def in functions.items():
        func_type = "Source" if func_def.is_source else "Sink" if func_def.is_sink else "Processor"
        print(f"  {name}: {func_type} - {func_def.description}")


def test_simple_execution():
    """Test simple pipeline execution (without actual video)"""
    print("\n\n=== Testing Simple Execution ===")
    
    # Test with test pattern (doesn't require camera)
    code = "test-pattern -> grayscale -> display"
    
    try:
        print(f"Testing: {code}")
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        runtime = Runtime()
        pipeline = runtime.compile(ast)
        
        print("Pipeline compiled successfully!")
        print(f"Number of nodes: {len(pipeline.nodes)}")
        
        # Don't actually run it to avoid opening windows
        # runtime.execute(ast)
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all tests"""
    print("VidPipe Test Suite")
    print("==================")
    
    test_lexer()
    test_parser()
    test_functions()
    test_simple_execution()
    
    print("\n\nAll tests completed!")


if __name__ == '__main__':
    main()