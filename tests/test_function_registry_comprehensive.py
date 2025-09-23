"""
Comprehensive tests for the VidPipe function registry
"""

import pytest
from unittest.mock import Mock, patch
import numpy as np
from vidpipe.functions import FunctionRegistry, FunctionDef, _require_cv2
from vidpipe.pipeline import Frame, FrameFormat


def dummy_source_function(**kwargs):
    """Dummy source function for testing"""
    return Frame(
        data=np.zeros((480, 640, 3), dtype=np.uint8),
        format=FrameFormat.BGR,
        width=640,
        height=480,
        timestamp=0.0
    )


def dummy_filter_function(frame: Frame, **kwargs):
    """Dummy filter function for testing"""
    return frame


def dummy_sink_function(frame: Frame, **kwargs):
    """Dummy sink function for testing"""
    pass


class TestFunctionRegistryBasics:
    """Test basic function registry functionality"""
    
    def test_registry_initialization(self):
        registry = FunctionRegistry()
        assert registry.functions is not None
        assert isinstance(registry.functions, dict)
        # Should have some built-in functions
        assert len(registry.functions) > 0
    
    def test_register_custom_function(self):
        registry = FunctionRegistry()
        initial_count = len(registry.functions)
        
        registry.register("test_func", dummy_filter_function, description="Test function")
        
        assert len(registry.functions) == initial_count + 1
        assert "test_func" in registry.functions
        
        func_def = registry.get_function("test_func")
        assert func_def is not None
        assert func_def.name == "test_func"
        assert func_def.function == dummy_filter_function
        assert func_def.description == "Test function"
    
    def test_register_source_function(self):
        registry = FunctionRegistry()
        
        registry.register("test_source", dummy_source_function, is_source=True)
        
        func_def = registry.get_function("test_source")
        assert func_def is not None
        assert func_def.is_source is True
        assert func_def.is_sink is False
    
    def test_register_sink_function(self):
        registry = FunctionRegistry()
        
        registry.register("test_sink", dummy_sink_function, is_sink=True)
        
        func_def = registry.get_function("test_sink")
        assert func_def is not None
        assert func_def.is_source is False
        assert func_def.is_sink is True
    
    def test_get_nonexistent_function(self):
        registry = FunctionRegistry()
        
        func_def = registry.get_function("nonexistent")
        assert func_def is None
    
    def test_list_functions(self):
        registry = FunctionRegistry()
        
        functions = registry.list_functions()
        assert isinstance(functions, dict)
        assert len(functions) > 0
        
        # Each item should be a FunctionDef
        for name, func_def in functions.items():
            assert isinstance(name, str)
            assert isinstance(func_def, FunctionDef)
    
    def test_register_with_parameters(self):
        registry = FunctionRegistry()
        
        params = {"param1": "int", "param2": "float"}
        registry.register("test_with_params", dummy_filter_function, parameters=params)
        
        func_def = registry.get_function("test_with_params")
        assert func_def is not None
        assert func_def.parameters == params


class TestBuiltinFunctions:
    """Test built-in functions in the registry"""
    
    def test_builtin_functions_exist(self):
        registry = FunctionRegistry()
        
        # Test some expected built-in functions
        expected_functions = [
            "test-pattern", "grayscale", "blur", "edges", "display"
        ]
        
        for func_name in expected_functions:
            func_def = registry.get_function(func_name)
            assert func_def is not None, f"Expected built-in function '{func_name}' not found"
    
    def test_builtin_functions_have_metadata(self):
        registry = FunctionRegistry()
        
        # Test that built-in functions have proper metadata
        func_def = registry.get_function("blur")
        assert func_def is not None
        assert func_def.description != ""
        assert len(func_def.parameters) > 0
    
    def test_source_functions_marked_correctly(self):
        registry = FunctionRegistry()
        
        # Test-pattern and webcam should be sources
        source_functions = ["test-pattern", "webcam"]
        
        for func_name in source_functions:
            func_def = registry.get_function(func_name)
            if func_def:  # Some might not be available in test environment
                assert func_def.is_source is True
    
    def test_sink_functions_marked_correctly(self):
        registry = FunctionRegistry()
        
        # Display and save should be sinks
        sink_functions = ["display"]
        
        for func_name in sink_functions:
            func_def = registry.get_function(func_name)
            if func_def:  # Some might not be available in test environment
                assert func_def.is_sink is True


class TestFunctionExecution:
    """Test execution of registry functions"""
    
    def test_execute_test_pattern_function(self):
        registry = FunctionRegistry()
        
        func_def = registry.get_function("test-pattern")
        assert func_def is not None
        
        # Execute the function (test-pattern is a source, so no input frame)
        frame = func_def.function(frame=None)
        assert isinstance(frame, Frame)
        assert frame.width > 0
        assert frame.height > 0
        assert frame.data is not None
    
    def test_execute_grayscale_function(self):
        registry = FunctionRegistry()
        
        func_def = registry.get_function("grayscale")
        assert func_def is not None
        
        # Create a test frame
        test_frame = Frame(
            data=np.zeros((100, 100, 3), dtype=np.uint8),
            format=FrameFormat.BGR,
            width=100,
            height=100,
            timestamp=0.0
        )
        
        # Execute the function
        result_frame = func_def.function(test_frame)
        assert isinstance(result_frame, Frame)
        assert result_frame.format == FrameFormat.GRAY
    
    def test_execute_function_with_parameters(self):
        registry = FunctionRegistry()
        
        func_def = registry.get_function("blur")
        assert func_def is not None
        
        # Create a test frame
        test_frame = Frame(
            data=np.ones((100, 100, 3), dtype=np.uint8) * 128,
            format=FrameFormat.BGR,
            width=100,
            height=100,
            timestamp=0.0
        )
        
        # Execute with parameters
        result_frame = func_def.function(test_frame, kernel_size=5, sigma=1.0)
        assert isinstance(result_frame, Frame)
        assert result_frame.width == test_frame.width
        assert result_frame.height == test_frame.height


class TestOpenCVIntegration:
    """Test OpenCV integration and requirements"""
    
    @patch('vidpipe.functions.cv2', None)
    def test_require_cv2_when_not_available(self):
        """Test that _require_cv2 raises error when OpenCV is not available"""
        with pytest.raises(RuntimeError, match="OpenCV.*is required"):
            _require_cv2()
    
    def test_cv2_dependent_functions_handle_missing_opencv(self):
        """Test that CV2-dependent functions handle missing OpenCV gracefully"""
        registry = FunctionRegistry()
        
        # These functions should exist even if OpenCV is not available
        # but might raise runtime errors when executed
        cv2_functions = ["webcam", "edges", "blur"]
        
        for func_name in cv2_functions:
            func_def = registry.get_function(func_name)
            if func_def:
                # Function should exist in registry
                assert callable(func_def.function)


class TestRegistryEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_register_duplicate_function(self):
        registry = FunctionRegistry()
        
        # Register a function
        registry.register("test_func", dummy_filter_function)
        original_func = registry.get_function("test_func")
        
        # Register again with same name
        registry.register("test_func", dummy_sink_function)
        new_func = registry.get_function("test_func")
        
        # Should replace the original
        assert new_func.function != original_func.function
        assert new_func.function == dummy_sink_function
    
    def test_register_with_none_function(self):
        registry = FunctionRegistry()
        
        # Should handle None function gracefully or raise appropriate error
        try:
            registry.register("none_func", None)
        except Exception as e:
            assert isinstance(e, (TypeError, ValueError))
    
    def test_list_functions_returns_copies(self):
        registry = FunctionRegistry()
        
        functions1 = registry.list_functions()
        functions2 = registry.list_functions()
        
        # Should return different dict objects (not the same reference)
        assert functions1 is not functions2
        # But with the same content
        assert len(functions1) == len(functions2)
    
    def test_function_def_creation(self):
        """Test FunctionDef dataclass creation"""
        func_def = FunctionDef(
            name="test",
            function=dummy_filter_function,
            is_source=True,
            is_sink=False,
            description="Test function",
            parameters={"param1": "int"}
        )
        
        assert func_def.name == "test"
        assert func_def.function == dummy_filter_function
        assert func_def.is_source is True
        assert func_def.is_sink is False
        assert func_def.description == "Test function"
        assert func_def.parameters == {"param1": "int"}
    
    def test_function_def_defaults(self):
        """Test FunctionDef with default values"""
        func_def = FunctionDef(name="test", function=dummy_filter_function)
        
        assert func_def.is_source is False
        assert func_def.is_sink is False
        assert func_def.description == ""
        assert func_def.parameters == {}


class TestRegistryFiltering:
    """Test filtering and querying registry"""
    
    def test_filter_source_functions(self):
        registry = FunctionRegistry()
        
        # Add some test functions
        registry.register("test_source1", dummy_source_function, is_source=True)
        registry.register("test_source2", dummy_source_function, is_source=True)
        registry.register("test_filter", dummy_filter_function)
        
        all_functions = registry.list_functions()
        source_functions = [f for f in all_functions.values() if f.is_source]
        
        assert len(source_functions) >= 2  # At least our test sources
        
        # Check that our test sources are included
        source_names = [f.name for f in source_functions]
        assert "test_source1" in source_names
        assert "test_source2" in source_names
        assert "test_filter" not in source_names
    
    def test_filter_sink_functions(self):
        registry = FunctionRegistry()
        
        # Add some test functions
        registry.register("test_sink1", dummy_sink_function, is_sink=True)
        registry.register("test_sink2", dummy_sink_function, is_sink=True)
        registry.register("test_filter", dummy_filter_function)
        
        all_functions = registry.list_functions()
        sink_functions = [f for f in all_functions.values() if f.is_sink]
        
        assert len(sink_functions) >= 2  # At least our test sinks
        
        # Check that our test sinks are included
        sink_names = [f.name for f in sink_functions]
        assert "test_sink1" in sink_names
        assert "test_sink2" in sink_names
        assert "test_filter" not in sink_names


class TestRegistrySearch:
    """Test search and discovery functionality"""
    
    def test_find_functions_by_description(self):
        registry = FunctionRegistry()
        
        # Add functions with specific descriptions
        registry.register("test1", dummy_filter_function, description="blur processing")
        registry.register("test2", dummy_filter_function, description="edge detection")
        registry.register("test3", dummy_filter_function, description="color processing")
        
        all_functions = registry.list_functions()
        
        # Find functions containing "processing" in description
        processing_functions = [f for f in all_functions.values() if "processing" in f.description.lower()]
        assert len(processing_functions) >= 2  # test1 and test3
        
        # Find functions containing "blur" in description
        blur_functions = [f for f in all_functions.values() if "blur" in f.description.lower()]
        assert len(blur_functions) >= 1  # test1
    
    def test_function_parameter_discovery(self):
        registry = FunctionRegistry()
        
        # Test that built-in functions have discoverable parameters
        blur_func = registry.get_function("blur")
        if blur_func:
            assert len(blur_func.parameters) > 0
            assert "kernel_size" in blur_func.parameters
        
        test_pattern_func = registry.get_function("test-pattern")
        if test_pattern_func:
            # Test pattern might have parameters like width, height
            assert isinstance(test_pattern_func.parameters, dict)