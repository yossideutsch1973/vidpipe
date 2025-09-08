"""
Abstract Syntax Tree node definitions for VidPipe
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from enum import Enum


class PipelineType(Enum):
    SYNC = "sync"           # ->
    ASYNC = "async"         # ~>
    BLOCKING = "blocking"   # =>
    BUFFERED = "buffered"   # [n]->


@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    pass


@dataclass
class FunctionNode(ASTNode):
    """Represents a function call in the pipeline"""
    name: str
    params: Dict[str, Any]
    
    def __repr__(self):
        if self.params:
            return f"Function({self.name}, params={self.params})"
        return f"Function({self.name})"


@dataclass
class PipelineNode(ASTNode):
    """Represents a pipeline connection between nodes"""
    left: ASTNode
    right: ASTNode
    pipe_type: PipelineType
    buffer_size: Optional[int] = None
    
    def __repr__(self):
        op = {
            PipelineType.SYNC: "->",
            PipelineType.ASYNC: "~>",
            PipelineType.BLOCKING: "=>",
            PipelineType.BUFFERED: f"[{self.buffer_size}]->"
        }.get(self.pipe_type, "->")
        return f"Pipeline({self.left} {op} {self.right})"


@dataclass
class ParallelNode(ASTNode):
    """Represents parallel execution branches"""
    branches: List[ASTNode]
    
    def __repr__(self):
        return f"Parallel({' &> '.join(str(b) for b in self.branches)})"


@dataclass
class MergeNode(ASTNode):
    """Represents merging of multiple streams"""
    inputs: List[ASTNode]
    output: ASTNode
    
    def __repr__(self):
        inputs_str = ', '.join(str(i) for i in self.inputs)
        return f"Merge([{inputs_str}] +> {self.output})"


@dataclass
class ChoiceNode(ASTNode):
    """Represents a choice between pipelines"""
    options: List[ASTNode]
    
    def __repr__(self):
        return f"Choice({' | '.join(str(o) for o in self.options)})"


@dataclass
class GroupNode(ASTNode):
    """Represents a grouped expression (parentheses)"""
    content: ASTNode
    
    def __repr__(self):
        return f"Group({self.content})"


@dataclass
class LoopNode(ASTNode):
    """Represents a continuous loop (curly braces)"""
    pipeline: ASTNode
    
    def __repr__(self):
        return f"Loop({{{self.pipeline}}})"


@dataclass
class PipelineDefinitionNode(ASTNode):
    """Represents a pipeline definition: pipeline name = expression"""
    name: str
    expression: ASTNode

    def __repr__(self):
        return f"PipelineDef({self.name} = {self.expression})"


@dataclass
class TimedPipelineNode(ASTNode):
    """Represents a pipeline with timing: pipeline @ duration"""
    pipeline: ASTNode
    duration: float

    def __repr__(self):
        return f"Timed({self.pipeline} @ {self.duration}s)"


@dataclass
class PipelineReferenceNode(ASTNode):
    """Represents a reference to a defined pipeline: pipeline_name"""
    name: str

    def __repr__(self):
        return f"PipelineRef({self.name})"


@dataclass
class ProgramNode(ASTNode):
    """Root node representing the entire program"""
    definitions: List[PipelineDefinitionNode]
    main_pipeline: Optional[ASTNode]

    def __repr__(self):
        if self.definitions:
            defs_str = ", ".join(str(d) for d in self.definitions)
            if self.main_pipeline:
                return f"Program([{defs_str}], main={self.main_pipeline})"
            return f"Program([{defs_str}])"
        return f"Program({self.main_pipeline})"