"""
Comprehensive tests for the VidPipe lexer
"""

import pytest
from vidpipe.lexer import Lexer
from vidpipe.tokens import Token, TokenType


class TestLexerBasics:
    """Test basic lexer functionality"""
    
    def test_empty_input(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_whitespace_handling(self):
        lexer = Lexer("   \t\n\r  ")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF


class TestLexerOperators:
    """Test all pipeline operators"""
    
    def test_sync_pipe(self):
        lexer = Lexer("->")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.SYNC_PIPE
        assert tokens[0].value == "->"
    
    def test_async_pipe(self):
        lexer = Lexer("~>")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ASYNC_PIPE
        assert tokens[0].value == "~>"
    
    def test_blocking_pipe(self):
        lexer = Lexer("=>")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.BLOCKING_PIPE
        assert tokens[0].value == "=>"
    
    def test_parallel_operator(self):
        lexer = Lexer("&>")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PARALLEL
        assert tokens[0].value == "&>"
    
    def test_merge_operator(self):
        lexer = Lexer("+>")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.MERGE
        assert tokens[0].value == "+>"
    
    def test_choice_operator(self):
        lexer = Lexer("|")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.CHOICE
        assert tokens[0].value == "|"


class TestLexerDelimiters:
    """Test delimiters and structural tokens"""
    
    def test_parentheses(self):
        lexer = Lexer("()")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN
    
    def test_brackets(self):
        lexer = Lexer("[]")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
    
    def test_braces(self):
        lexer = Lexer("{}")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
    
    def test_comma(self):
        lexer = Lexer(",")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.COMMA
    
    def test_colon(self):
        lexer = Lexer(":")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.COLON
    
    def test_equals(self):
        lexer = Lexer("=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EQUALS
    
    def test_at_symbol(self):
        lexer = Lexer("@")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.AT


class TestLexerIdentifiersAndKeywords:
    """Test identifier and keyword tokenization"""
    
    def test_simple_identifier(self):
        lexer = Lexer("webcam")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "webcam"
    
    def test_identifier_with_hyphens(self):
        lexer = Lexer("test-pattern")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "test-pattern"
    
    def test_identifier_with_underscores(self):
        lexer = Lexer("camera_input")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "camera_input"
    
    def test_with_keyword(self):
        lexer = Lexer("with")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.WITH
        assert tokens[0].value == "with"
    
    def test_pipeline_keyword(self):
        lexer = Lexer("pipeline")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PIPELINE
        assert tokens[0].value == "pipeline"


class TestLexerNumbers:
    """Test number tokenization"""
    
    def test_integer(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42
    
    def test_float(self):
        lexer = Lexer("3.14")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14
    
    def test_zero(self):
        lexer = Lexer("0")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 0


class TestLexerStrings:
    """Test string tokenization"""
    
    def test_double_quoted_string(self):
        lexer = Lexer('"hello world"')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
    
    def test_single_quoted_string(self):
        lexer = Lexer("'hello world'")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"
    
    def test_empty_string(self):
        lexer = Lexer('""')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""
    
    def test_string_with_escaped_quotes(self):
        lexer = Lexer(r'"She said \"hello\""')
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == 'She said "hello"'


class TestLexerComments:
    """Test comment handling"""
    
    def test_line_comment(self):
        lexer = Lexer("# This is a comment")
        tokens = lexer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_inline_comment(self):
        lexer = Lexer("webcam # This is a comment")
        tokens = lexer.tokenize()
        assert len(tokens) == 2
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "webcam"
        assert tokens[1].type == TokenType.EOF


class TestLexerComplexExpressions:
    """Test complex DSL expressions"""
    
    def test_simple_pipeline(self):
        lexer = Lexer("webcam -> grayscale -> display")
        tokens = lexer.tokenize()
        
        values = [token.value for token in tokens if token.type != TokenType.EOF]
        assert values == ["webcam", "->", "grayscale", "->", "display"]
    
    def test_pipeline_with_parameters(self):
        lexer = Lexer('blur with (kernel_size: 15, sigma: 5.0)')
        tokens = lexer.tokenize()
        
        expected_values = ["blur", "with", "(", "kernel_size", ":", 15, ",", "sigma", ":", 5.0, ")"]
        actual_values = [token.value for token in tokens if token.type != TokenType.EOF]
        assert actual_values == expected_values
    
    def test_pipeline_definition(self):
        lexer = Lexer("pipeline preprocess = webcam -> grayscale")
        tokens = lexer.tokenize()
        
        expected_values = ["pipeline", "preprocess", "=", "webcam", "->", "grayscale"]
        actual_values = [token.value for token in tokens if token.type != TokenType.EOF]
        assert actual_values == expected_values


class TestLexerErrorHandling:
    """Test lexer error handling"""
    
    def test_unterminated_string(self):
        lexer = Lexer('"unterminated string')
        with pytest.raises(SyntaxError, match="Unterminated string"):
            lexer.tokenize()
    
    def test_invalid_character(self):
        lexer = Lexer("webcam $ display")
        with pytest.raises(SyntaxError, match="Unexpected character"):
            lexer.tokenize()


class TestLexerPositioning:
    """Test line and column tracking"""
    
    def test_line_column_tracking(self):
        lexer = Lexer("webcam\n-> display")
        tokens = lexer.tokenize()
        
        # First token should be at line 1, column 1
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        
        # Second token should be at line 2, column 1
        assert tokens[1].line == 2
        assert tokens[1].column == 1
    
    def test_column_tracking_within_line(self):
        lexer = Lexer("a -> b")
        tokens = lexer.tokenize()
        
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        
        assert tokens[1].line == 1
        assert tokens[1].column == 3
        
        assert tokens[2].line == 1
        assert tokens[2].column == 6