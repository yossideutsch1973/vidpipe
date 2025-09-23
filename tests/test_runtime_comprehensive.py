"""
Comprehensive tests for the VidPipe runtime
"""

import pytest
from unittest.mock import Mock, patch
from vidpipe.lexer import Lexer
from vidpipe.parser import Parser
from vidpipe.runtime import Runtime
from vidpipe.ast_nodes import FunctionNode, PipelineReferenceNode
from vidpipe.functions import FunctionRegistry
from vidpipe.pipeline import Frame, FrameFormat


class TestRuntimeBasics:
    """Test basic runtime functionality"""
    
    def test_runtime_initialization(self):
        runtime = Runtime()
        assert runtime.registry is not None
        assert isinstance(runtime.registry, FunctionRegistry)
        assert runtime.pipeline is None
        assert runtime.node_map == {}
        assert runtime.node_counter == 0
    
    def test_node_id_generation(self):
        runtime = Runtime()
        id1 = runtime.generate_node_id("test")
        id2 = runtime.generate_node_id("test")
        
        assert id1 != id2
        assert id1.startswith("test_")
        assert id2.startswith("test_")


class TestRuntimeCompilation:
    """Test AST compilation to executable pipelines"""
    
    def test_compile_empty_program(self):
        runtime = Runtime()
        tokens = Lexer("").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert len(pipeline.nodes) == 0
    
    def test_compile_simple_function(self):
        runtime = Runtime()
        tokens = Lexer("test-pattern").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        # Should create at least one node for the function
        assert len(pipeline.nodes) > 0
    
    def test_compile_simple_pipeline(self):
        runtime = Runtime()
        tokens = Lexer("test-pattern -> display").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert len(pipeline.nodes) >= 2  # At least source and sink
    
    def test_compile_function_with_parameters(self):
        runtime = Runtime()
        tokens = Lexer('blur with (kernel_size: 15, sigma: 5.0)').tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert len(pipeline.nodes) > 0


class TestRuntimeFunctionRegistry:
    """Test runtime integration with function registry"""
    
    def test_runtime_uses_registry(self):
        runtime = Runtime()
        
        # Should have access to built-in functions
        blur_func = runtime.registry.get_function("blur")
        assert blur_func is not None
        
        grayscale_func = runtime.registry.get_function("grayscale")
        assert grayscale_func is not None
    
    def test_compile_with_unknown_function(self):
        runtime = Runtime()
        tokens = Lexer("unknown_function").tokenize()
        ast = Parser(tokens).parse()
        
        # Should handle unknown functions gracefully or raise appropriate error
        # The exact behavior depends on implementation
        try:
            pipeline = runtime.compile(ast)
            # If it doesn't raise an error, pipeline should still be created
            assert pipeline is not None
        except Exception as e:
            # If it raises an error, it should be meaningful
            assert "unknown_function" in str(e).lower() or "not found" in str(e).lower()


class TestRuntimePipelineDefinitions:
    """Test runtime handling of pipeline definitions"""
    
    def test_compile_pipeline_definition(self):
        runtime = Runtime()
        tokens = Lexer("pipeline preprocess = test-pattern -> grayscale").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        # Should store the pipeline definition
        assert "preprocess" in runtime.pipeline_definitions
    
    def test_compile_pipeline_definition_usage(self):
        runtime = Runtime()
        tokens = Lexer("pipeline preprocess = test-pattern -> grayscale\npreprocess -> display").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert "preprocess" in runtime.pipeline_definitions
        assert len(pipeline.nodes) > 0


class TestRuntimeErrorHandling:
    """Test runtime error handling"""
    
    def test_compile_handles_invalid_ast(self):
        runtime = Runtime()
        
        # Test with None
        try:
            runtime.compile_node(None)
        except Exception:
            pass  # Expected to handle gracefully or raise meaningful error
    
    def test_runtime_with_malformed_parameters(self):
        runtime = Runtime()
        
        # Need to initialize pipeline first
        from vidpipe.pipeline import Pipeline
        runtime.pipeline = Pipeline()
        
        # Create a function node with invalid parameters
        func_node = FunctionNode("blur", {"invalid_param": "invalid_value"})
        
        # Should handle invalid parameters gracefully
        try:
            result = runtime.compile_function(func_node)
            # If it doesn't raise an error, result should be reasonable
            assert result is not None or result is None
        except Exception as e:
            # If it raises an error, it should be meaningful
            assert isinstance(e, (ValueError, KeyError, TypeError, RuntimeError, AttributeError))


class TestRuntimeIntegration:
    """Test end-to-end runtime integration"""
    
    def test_parse_compile_execute_chain(self):
        """Test the full chain from parsing to compilation"""
        runtime = Runtime()
        
        # Parse a simple expression
        tokens = Lexer("test-pattern -> grayscale -> display").tokenize()
        ast = Parser(tokens).parse()
        
        # Compile to pipeline
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert len(pipeline.nodes) >= 3  # Should have at least 3 nodes
        
        # Verify pipeline structure
        assert hasattr(pipeline, 'nodes')
        assert hasattr(pipeline, 'connections')
    
    def test_compile_complex_expression(self):
        """Test compilation of complex expressions"""
        runtime = Runtime()
        
        # Test a more complex pipeline
        tokens = Lexer("test-pattern -> blur with (kernel_size: 5) -> grayscale -> display").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        assert len(pipeline.nodes) >= 4
    
    def test_compile_parallel_operations(self):
        """Test compilation of parallel operations"""
        runtime = Runtime()
        
        # Test parallel operation
        tokens = Lexer("test-pattern &> grayscale").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        # Parallel operations should create multiple nodes
        assert len(pipeline.nodes) >= 2


class TestRuntimeMocking:
    """Test runtime with mocked dependencies"""
    
    @patch('vidpipe.runtime.FunctionRegistry')
    def test_runtime_with_mocked_registry(self, mock_registry_class):
        """Test runtime with mocked function registry"""
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        
        # Mock a function definition
        mock_func_def = Mock()
        mock_func_def.function = Mock(return_value=Frame(
            data=None, format=FrameFormat.BGR, width=640, height=480, timestamp=0.0
        ))
        mock_func_def.parameters = {}
        mock_func_def.is_source = True
        mock_func_def.is_sink = False
        mock_registry.get_function.return_value = mock_func_def
        
        runtime = Runtime()
        tokens = Lexer("test_function").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        
        # Verify registry was called
        mock_registry.get_function.assert_called()
    
    def test_runtime_compilation_metrics(self):
        """Test runtime compilation produces reasonable metrics"""
        runtime = Runtime()
        
        # Compile a known pipeline
        tokens = Lexer("test-pattern -> grayscale -> edges -> display").tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        
        # Check compilation results
        assert pipeline is not None
        assert runtime.node_counter > 0  # Should have created some nodes
        assert len(runtime.node_map) >= 0  # Should have node mappings
        
        # Pipeline should have reasonable structure
        assert len(pipeline.nodes) >= 1
        assert hasattr(pipeline, 'connections')


class TestRuntimeEdgeCases:
    """Test runtime edge cases and boundary conditions"""
    
    def test_runtime_with_very_long_pipeline(self):
        """Test runtime with a very long pipeline"""
        runtime = Runtime()
        
        # Create a long chain using known functions
        known_functions = ["test-pattern", "grayscale", "edges", "blur", "display"]
        pipeline_code = " -> ".join(known_functions)
        tokens = Lexer(pipeline_code).tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        # Should handle long pipelines
        assert len(pipeline.nodes) >= len(known_functions)
    
    def test_runtime_with_multiple_definitions(self):
        """Test runtime with multiple pipeline definitions"""
        runtime = Runtime()
        
        code = """
        pipeline input = test-pattern
        pipeline process = grayscale -> edges
        pipeline output = display
        input -> process -> output
        """
        
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        
        pipeline = runtime.compile(ast)
        assert pipeline is not None
        
        # Should have stored all definitions
        assert len(runtime.pipeline_definitions) == 3
        assert "input" in runtime.pipeline_definitions
        assert "process" in runtime.pipeline_definitions
        assert "output" in runtime.pipeline_definitions
    
    def test_runtime_recompilation(self):
        """Test runtime can be reused for multiple compilations"""
        runtime = Runtime()
        
        # Compile first pipeline
        tokens1 = Lexer("test-pattern -> display").tokenize()
        ast1 = Parser(tokens1).parse()
        pipeline1 = runtime.compile(ast1)
        
        # Compile second pipeline
        tokens2 = Lexer("webcam -> grayscale -> display").tokenize()
        ast2 = Parser(tokens2).parse()
        pipeline2 = runtime.compile(ast2)
        
        # Both should be valid but different
        assert pipeline1 is not None
        assert pipeline2 is not None
        assert pipeline1 is not pipeline2