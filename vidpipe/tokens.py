"""
Token definitions for VidPipe language
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    # Pipeline operators
    SYNC_PIPE = auto()        # ->
    ASYNC_PIPE = auto()       # ~>
    BLOCKING_PIPE = auto()    # =>
    PARALLEL = auto()         # &>
    MERGE = auto()           # +>
    CHOICE = auto()          # |
    
    # Structural
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    
    # Other
    IDENTIFIER = auto()      # function names
    NUMBER = auto()          # buffer sizes, parameters
    STRING = auto()          # string parameters
    COMMA = auto()           # ,
    COLON = auto()           # :
    EOF = auto()             # End of file
    
    # Keywords
    WITH = auto()            # with keyword for parameters
    PIPELINE = auto()        # pipeline keyword for definitions
    AT = auto()              # @ timing operator
    EQUALS = auto()          # = assignment operator


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line},{self.column})"