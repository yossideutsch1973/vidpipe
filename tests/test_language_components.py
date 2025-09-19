import pytest

from vidpipe import Lexer, Parser, Runtime
from vidpipe.functions import FunctionRegistry


def test_lexer_emits_expected_tokens():
    code = "webcam -> grayscale -> display"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    values = [token.value for token in tokens if token.type.name != "EOF"]
    assert values[:3] == ["webcam", "->", "grayscale"]


def test_parser_builds_main_pipeline():
    code = "pipeline preprocess = webcam -> grayscale\npreprocess -> display"
    parser = Parser(Lexer(code).tokenize())
    ast = parser.parse()

    assert ast.main_pipeline is not None
    assert len(ast.definitions) == 1


def test_runtime_compile_creates_nodes():
    code = "test-pattern -> grayscale -> display"
    runtime = Runtime()
    ast = Parser(Lexer(code).tokenize()).parse()
    pipeline = runtime.compile(ast)

    assert pipeline.nodes, "Compiled pipeline should contain execution nodes"


def test_registry_provides_shared_parameters():
    registry = FunctionRegistry()
    blur = registry.get_function("blur")
    assert blur is not None
    assert "kernel_size" in blur.parameters
    assert "sigma" in blur.parameters
