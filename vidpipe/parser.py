"""
Parser for VidPipe language - builds AST from tokens
"""

from typing import List, Optional, Dict, Any, Union
from .tokens import Token, TokenType
from .ast_nodes import *


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
    
    def error(self, message: str):
        if self.current_token:
            raise SyntaxError(f"Parser error at line {self.current_token.line}, "
                            f"column {self.current_token.column}: {message}")
        else:
            raise SyntaxError(f"Parser error: {message}")
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Token:
        token = self.current_token
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        if self.current_token and self.current_token.type == token_type:
            return self.advance()
        self.error(f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}")
    
    def parse(self) -> ProgramNode:
        """Parse the entire program"""
        definitions = []
        main_pipeline = None

        # Handle empty program
        if self.current_token.type == TokenType.EOF:
            return ProgramNode(definitions, main_pipeline)

        # Parse definitions and main pipeline
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.PIPELINE:
                # Parse pipeline definition
                definition = self.parse_pipeline_definition()
                if definition:
                    definitions.append(definition)
            else:
                # Parse main pipeline
                pipeline = self.parse_pipeline()
                if pipeline:
                    main_pipeline = pipeline
                break

        # Check for unexpected tokens
        if self.current_token.type != TokenType.EOF:
            self.error(f"Unexpected token: {self.current_token.value}")

        return ProgramNode(definitions, main_pipeline)
    
    def parse_pipeline(self) -> Optional[ASTNode]:
        """Parse a complete pipeline expression"""
        return self.parse_merge_expression()
    
    def parse_merge_expression(self) -> Optional[ASTNode]:
        """Parse merge operations (+>)"""
        left = self.parse_choice_expression()
        
        if not left:
            return None
        
        # Check for merge operator
        if self.current_token and self.current_token.type == TokenType.MERGE:
            inputs = [left]
            
            # Collect all inputs before merge
            while self.peek() and self.peek().type != TokenType.MERGE:
                expr = self.parse_choice_expression()
                if expr:
                    inputs.append(expr)
            
            self.expect(TokenType.MERGE)
            output = self.parse_choice_expression()
            
            if not output:
                self.error("Expected expression after merge operator")
            
            return MergeNode(inputs, output)
        
        return left
    
    def parse_choice_expression(self) -> Optional[ASTNode]:
        """Parse choice operations (|)"""
        left = self.parse_parallel_expression()
        
        if not left:
            return None
        
        options = [left]
        
        while self.current_token and self.current_token.type == TokenType.CHOICE:
            self.advance()
            right = self.parse_parallel_expression()
            if not right:
                self.error("Expected expression after choice operator")
            options.append(right)
        
        if len(options) > 1:
            return ChoiceNode(options)
        
        return left
    
    def parse_parallel_expression(self) -> Optional[ASTNode]:
        """Parse parallel operations (&>)"""
        left = self.parse_pipe_expression()
        
        if not left:
            return None
        
        branches = [left]
        
        while self.current_token and self.current_token.type == TokenType.PARALLEL:
            self.advance()
            right = self.parse_pipe_expression()
            if not right:
                self.error("Expected expression after parallel operator")
            branches.append(right)
        
        if len(branches) > 1:
            return ParallelNode(branches)
        
        return left
    
    def parse_pipe_expression(self) -> Optional[ASTNode]:
        """Parse pipe operations (->, ~>, =>, [n]->)"""
        left = self.parse_primary()
        
        if not left:
            return None
        
        while self.current_token and self.current_token.type in [
            TokenType.SYNC_PIPE, TokenType.ASYNC_PIPE, TokenType.BLOCKING_PIPE
        ]:
            pipe_type = {
                TokenType.SYNC_PIPE: PipelineType.SYNC,
                TokenType.ASYNC_PIPE: PipelineType.ASYNC,
                TokenType.BLOCKING_PIPE: PipelineType.BLOCKING
            }[self.current_token.type]
            
            self.advance()
            right = self.parse_primary()
            
            if not right:
                self.error("Expected expression after pipe operator")
            
            left = PipelineNode(left, right, pipe_type)
        
        return left
    
    def parse_primary(self) -> Optional[ASTNode]:
        """Parse primary expressions (functions, groups, loops)"""
        
        # Check for buffered pipe [n]
        if self.current_token and self.current_token.type == TokenType.LBRACKET:
            self.advance()
            
            if self.current_token.type != TokenType.NUMBER:
                self.error("Expected number for buffer size")
            
            buffer_size = int(self.current_token.value)
            self.advance()
            
            self.expect(TokenType.RBRACKET)
            
            # Must be followed by pipe operator
            if self.current_token.type != TokenType.SYNC_PIPE:
                self.error("Expected -> after buffer specification")
            
            self.advance()
            right = self.parse_primary()
            
            if not right:
                self.error("Expected expression after buffered pipe")
            
            # Create a special buffered pipeline node
            # We'll handle this by returning a partial pipeline that needs a left side
            # This is a bit tricky - we need to restructure parsing for this
            # For now, we'll handle it differently
            return right  # Simplified for now
        
        # Loop construct {pipeline}
        if self.current_token and self.current_token.type == TokenType.LBRACE:
            self.advance()
            pipeline = self.parse_pipeline()
            if not pipeline:
                self.error("Expected pipeline inside loop")
            self.expect(TokenType.RBRACE)
            return LoopNode(pipeline)
        
        # Grouped expression (pipeline)
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            pipeline = self.parse_pipeline()
            if not pipeline:
                self.error("Expected pipeline inside parentheses")
            self.expect(TokenType.RPAREN)
            return GroupNode(pipeline)
        
        # Function call or pipeline reference
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            node = self.parse_function()

            # Check for timing operator (@ duration)
            if self.current_token and self.current_token.type == TokenType.AT:
                self.advance()  # consume @
                duration = self.parse_duration()
                node = TimedPipelineNode(node, duration)

            return node

        return None
    
    def parse_function(self) -> Union[FunctionNode, PipelineReferenceNode]:
        """Parse a function call, pipeline reference, or definition reference"""
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected function name or pipeline reference")

        name = self.current_token.value
        self.advance()

        # Check if this is a function call (has parameters) or just a reference
        if self.current_token and (
            self.current_token.type == TokenType.WITH or
            self.current_token.type == TokenType.LPAREN
        ):
            # This is a function call with parameters
            params = {}

            # Check for 'with' keyword for parameters
            if self.current_token.type == TokenType.WITH:
                self.advance()
                params = self.parse_parameters()
            # Check for direct parentheses (alternative syntax)
            elif self.current_token.type == TokenType.LPAREN:
                self.advance()
                params = self.parse_parameter_list()
                self.expect(TokenType.RPAREN)

            return FunctionNode(name, params)
        else:
            # This is a pipeline reference (no parameters)
            return PipelineReferenceNode(name)
    
    def parse_parameters(self) -> Dict[str, Any]:
        """Parse function parameters"""
        params = {}

        # Support both key:value and positional parameters
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()  # consume opening parenthesis
            params = self.parse_parameter_list()
            self.expect(TokenType.RPAREN)

        return params

    def parse_pipeline_definition(self) -> Optional[PipelineDefinitionNode]:
        """Parse a pipeline definition: pipeline name = expression"""
        # Consume 'pipeline' keyword
        self.advance()

        # Expect identifier for pipeline name
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected pipeline name after 'pipeline'")

        name = self.current_token.value
        self.advance()

        # Expect '='
        if self.current_token.type != TokenType.EQUALS:
            self.error("Expected '=' after pipeline name")

        self.advance()

        # Parse the pipeline expression
        expression = self.parse_pipeline()
        if not expression:
            self.error("Expected pipeline expression after '='")

        return PipelineDefinitionNode(name, expression)

    def parse_duration(self) -> float:
        """Parse duration value (number followed by 's')"""
        if self.current_token.type != TokenType.NUMBER:
            self.error("Expected number for duration")

        duration = float(self.current_token.value)
        self.advance()

        # Check for 's' suffix (optional for now)
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER and self.current_token.value == 's':
            self.advance()

        return duration

    def parse_parameter_list(self) -> Dict[str, Any]:
        """Parse comma-separated parameter list"""
        params = {}
        param_index = 0
        
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            # Check for key:value syntax
            if self.current_token.type == TokenType.IDENTIFIER and \
               self.peek(1) and self.peek(1).type == TokenType.COLON:
                key = self.current_token.value
                self.advance()  # identifier
                self.advance()  # colon
                value = self.parse_value()
                params[key] = value
            else:
                # Positional parameter
                value = self.parse_value()
                params[f"arg{param_index}"] = value
                param_index += 1

            # Check for comma or end of list
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # consume comma, continue parsing
            elif self.current_token and self.current_token.type == TokenType.RPAREN:
                # End of parameter list, we're done
                break
            else:
                # Unexpected token
                self.error(f"Expected comma or closing parenthesis, got {self.current_token.type.name}")
        
        return params
    
    def parse_value(self) -> Any:
        """Parse a parameter value"""
        if self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return value
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return value
        elif self.current_token.type == TokenType.IDENTIFIER:
            value = self.current_token.value
            self.advance()
            return value
        else:
            self.error(f"Expected value, got {self.current_token.type.name}")