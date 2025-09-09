import pytest
from vidpipe.functions import FunctionRegistry
from vidpipe.pipeline import Frame, FrameFormat


def dummy_filter(frame: Frame, **kwargs) -> Frame:
    return frame


def test_register_custom_function():
    registry = FunctionRegistry()
    registry.register("dummy", dummy_filter)
    func_def = registry.get_function("dummy")
    assert func_def is not None
    assert callable(func_def.function)
