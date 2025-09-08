"""
Lexer for VidPipe language
"""

import re
from typing import List, Optional
from .tokens import Token, TokenType


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        if self.position < len(self.source):
            char = self.source[self.position]
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None
    
    def skip_whitespace(self):
        while self.peek() and self.peek() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        if self.peek() == '#':
            while self.peek() and self.peek() != '\n':
                self.advance()
            return True
        return False
    
    def read_number(self) -> Token:
        start_line = self.line
        start_column = self.column
        num_str = ''
        
        while self.peek() and (self.peek().isdigit() or self.peek() == '.'):
            num_str += self.advance()
        
        try:
            value = float(num_str) if '.' in num_str else int(num_str)
        except ValueError:
            self.error(f"Invalid number: {num_str}")
        
        return Token(TokenType.NUMBER, value, start_line, start_column)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_column = self.column
        quote_char = self.advance()  # Skip opening quote
        string_val = ''
        
        while self.peek() and self.peek() != quote_char:
            char = self.advance()
            if char == '\\' and self.peek():
                next_char = self.advance()
                if next_char == 'n':
                    string_val += '\n'
                elif next_char == 't':
                    string_val += '\t'
                elif next_char == '\\':
                    string_val += '\\'
                elif next_char in '"\'':
                    string_val += next_char
                else:
                    string_val += next_char
            else:
                string_val += char
        
        if not self.peek():
            self.error(f"Unterminated string")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, string_val, start_line, start_column)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_column = self.column
        ident = ''
        
        while self.peek() and (self.peek().isalnum() or self.peek() in '-_'):
            ident += self.advance()
        
        # Check for keywords
        if ident == 'with':
            return Token(TokenType.WITH, ident, start_line, start_column)
        elif ident == 'pipeline':
            return Token(TokenType.PIPELINE, ident, start_line, start_column)
        
        return Token(TokenType.IDENTIFIER, ident, start_line, start_column)
    
    def read_operator(self) -> Optional[Token]:
        start_line = self.line
        start_column = self.column
        
        # Check two-character operators first
        two_char = self.source[self.position:self.position+2] if self.position + 1 < len(self.source) else ''
        
        if two_char == '->':
            self.advance()
            self.advance()
            return Token(TokenType.SYNC_PIPE, '->', start_line, start_column)
        elif two_char == '~>':
            self.advance()
            self.advance()
            return Token(TokenType.ASYNC_PIPE, '~>', start_line, start_column)
        elif two_char == '=>':
            self.advance()
            self.advance()
            return Token(TokenType.BLOCKING_PIPE, '=>', start_line, start_column)
        elif two_char == '&>':
            self.advance()
            self.advance()
            return Token(TokenType.PARALLEL, '&>', start_line, start_column)
        elif two_char == '+>':
            self.advance()
            self.advance()
            return Token(TokenType.MERGE, '+>', start_line, start_column)
        
        # Single character operators and delimiters
        char = self.peek()
        if char == '|':
            self.advance()
            return Token(TokenType.CHOICE, '|', start_line, start_column)
        elif char == '(':
            self.advance()
            return Token(TokenType.LPAREN, '(', start_line, start_column)
        elif char == ')':
            self.advance()
            return Token(TokenType.RPAREN, ')', start_line, start_column)
        elif char == '[':
            self.advance()
            return Token(TokenType.LBRACKET, '[', start_line, start_column)
        elif char == ']':
            self.advance()
            return Token(TokenType.RBRACKET, ']', start_line, start_column)
        elif char == '{':
            self.advance()
            return Token(TokenType.LBRACE, '{', start_line, start_column)
        elif char == '}':
            self.advance()
            return Token(TokenType.RBRACE, '}', start_line, start_column)
        elif char == ',':
            self.advance()
            return Token(TokenType.COMMA, ',', start_line, start_column)
        elif char == ':':
            self.advance()
            return Token(TokenType.COLON, ':', start_line, start_column)
        elif char == '@':
            self.advance()
            return Token(TokenType.AT, '@', start_line, start_column)
        elif char == '=':
            self.advance()
            return Token(TokenType.EQUALS, '=', start_line, start_column)
        
        # Handle unexpected characters that are part of operators
        return None
    
    def tokenize(self) -> List[Token]:
        self.tokens = []
        
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if self.position >= len(self.source):
                break
            
            if self.skip_comment():
                continue
            
            char = self.peek()
            
            if char and char.isdigit():
                self.tokens.append(self.read_number())
            elif char and (char == '"' or char == "'"):
                self.tokens.append(self.read_string())
            elif char and (char.isalpha() or char == '_'):
                self.tokens.append(self.read_identifier())
            elif char and char == '-':
                # Check if this is an identifier starting with '-' or an operator
                if self.position + 1 < len(self.source) and self.source[self.position + 1].isalpha():
                    self.tokens.append(self.read_identifier())
                else:
                    token = self.read_operator()
                    if token:
                        self.tokens.append(token)
                    else:
                        self.error(f"Unexpected character: {char}")
            elif char and char in '~=&+|()[]{},:>@':
                token = self.read_operator()
                if token:
                    self.tokens.append(token)
                else:
                    self.error(f"Unexpected character: {char}")
            else:
                self.error(f"Unexpected character: {char}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens