"""
Runtime engine for executing VidPipe pipelines
"""

from typing import Dict, Any, Callable, Optional
from .ast_nodes import *
from .pipeline import Pipeline, PipelineNode as ExecNode, Queue
from .functions import FunctionRegistry, _display_manager


class Runtime:
    """Runtime engine that executes AST"""

    def __init__(self):
        self.registry = FunctionRegistry()
        self.pipeline = None
        self.node_map: Dict[str, ExecNode] = {}
        self.node_counter = 0
        self.pipeline_definitions: Dict[str, ASTNode] = {}
        self.timing_info: Dict[str, float] = {}
    
    def generate_node_id(self, base_name: str) -> str:
        """Generate unique node ID"""
        self.node_counter += 1
        return f"{base_name}_{self.node_counter}"
    
    def compile(self, ast: ProgramNode) -> Pipeline:
        """Compile AST into executable pipeline"""
        self.pipeline = Pipeline()
        self.node_map = {}
        self.node_counter = 0
        self.pipeline_definitions = {}
        self.timing_info = {}

        # Process pipeline definitions first
        for definition in ast.definitions:
            self.pipeline_definitions[definition.name] = definition.expression

        # Process main pipeline if it exists
        if ast.main_pipeline:
            self.compile_node(ast.main_pipeline)

        return self.pipeline
    
    def compile_node(self, node: ASTNode) -> Optional[ExecNode]:
        """Compile an AST node into executable pipeline nodes"""
        
        if isinstance(node, FunctionNode):
            return self.compile_function(node)

        elif isinstance(node, PipelineNode):
            return self.compile_pipeline(node)

        elif isinstance(node, ParallelNode):
            return self.compile_parallel(node)

        elif isinstance(node, MergeNode):
            return self.compile_merge(node)

        elif isinstance(node, ChoiceNode):
            return self.compile_choice(node)

        elif isinstance(node, GroupNode):
            return self.compile_node(node.content)

        elif isinstance(node, LoopNode):
            return self.compile_loop(node)

        elif isinstance(node, PipelineReferenceNode):
            return self.compile_pipeline_reference(node)

        elif isinstance(node, TimedPipelineNode):
            return self.compile_timed_pipeline(node)

        elif isinstance(node, PipelineDefinitionNode):
            # Pipeline definitions are handled separately
            return None

        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")
    
    def compile_function(self, node: FunctionNode) -> ExecNode:
        """Compile a function node"""
        func_def = self.registry.get_function(node.name)
        if not func_def:
            raise RuntimeError(f"Unknown function: {node.name}")
        
        exec_node = ExecNode(
            name=self.generate_node_id(node.name),
            function=func_def.function,
            params=node.params
        )
        exec_node.is_source = func_def.is_source
        exec_node.is_sink = func_def.is_sink
        
        self.pipeline.add_node(exec_node)
        return exec_node
    
    def compile_pipeline(self, node: PipelineNode) -> Optional[ExecNode]:
        """Compile a pipeline connection"""
        left_exec = self.compile_node(node.left)
        right_exec = self.compile_node(node.right)
        
        if left_exec and right_exec:
            # Determine buffer size and async mode
            buffer_size = node.buffer_size if node.buffer_size else 10
            async_mode = node.pipe_type == PipelineType.ASYNC
            
            # Handle different connection types
            if isinstance(left_exec, list):
                # Multiple outputs to single input
                for left_node in left_exec:
                    self.pipeline.connect(left_node, right_exec, buffer_size, async_mode)
            elif isinstance(right_exec, list):
                # Single output to multiple inputs (fan-out)
                for right_node in right_exec:
                    self.pipeline.connect(left_exec, right_node, buffer_size, async_mode)
            else:
                # Simple connection
                self.pipeline.connect(left_exec, right_exec, buffer_size, async_mode)
        
        return right_exec
    
    def compile_parallel(self, node: ParallelNode) -> list:
        """Compile parallel branches"""
        branches = []
        for branch in node.branches:
            exec_node = self.compile_node(branch)
            if exec_node:
                branches.append(exec_node)
        return branches
    
    def compile_merge(self, node: MergeNode) -> ExecNode:
        """Compile merge operation"""
        # Create a merge function node
        merge_func = self.registry.get_function("merge")
        if not merge_func:
            # Create default merge function if not registered
            def default_merge(*frames, **kwargs):
                # Simple merge: return the first non-None frame
                for frame in frames:
                    if frame is not None:
                        return frame
                return None
            
            merge_exec = ExecNode(
                name=self.generate_node_id("merge"),
                function=default_merge,
                params={}
            )
        else:
            merge_exec = ExecNode(
                name=self.generate_node_id("merge"),
                function=merge_func.function,
                params={}
            )
        
        self.pipeline.add_node(merge_exec)
        
        # Connect inputs to merge
        for input_node in node.inputs:
            input_exec = self.compile_node(input_node)
            if input_exec:
                if isinstance(input_exec, list):
                    for exec_n in input_exec:
                        self.pipeline.connect(exec_n, merge_exec, 10, False)
                else:
                    self.pipeline.connect(input_exec, merge_exec, 10, False)
        
        # Connect merge to output
        output_exec = self.compile_node(node.output)
        if output_exec:
            self.pipeline.connect(merge_exec, output_exec, 10, False)
        
        return output_exec
    
    def compile_choice(self, node: ChoiceNode) -> ExecNode:
        """Compile choice operation"""
        # For now, just compile the first option
        # In a full implementation, this would involve runtime selection
        if node.options:
            return self.compile_node(node.options[0])
        return None
    
    def compile_loop(self, node: LoopNode) -> ExecNode:
        """Compile loop construct"""
        # Create a loop wrapper that continuously executes the pipeline
        pipeline_exec = self.compile_node(node.pipeline)

        # In a real implementation, we'd need to handle loop feedback
        # For now, just return the pipeline
        return pipeline_exec

    def compile_pipeline_reference(self, node: PipelineReferenceNode) -> Optional[ExecNode]:
        """Compile a pipeline reference - could be a defined pipeline or a function"""
        if node.name in self.pipeline_definitions:
            # This is a defined pipeline
            return self.compile_node(self.pipeline_definitions[node.name])
        else:
            # This might be a function call without parameters
            # Convert it to a FunctionNode and compile
            func_node = FunctionNode(node.name, {})
            return self.compile_function(func_node)

    def compile_timed_pipeline(self, node: TimedPipelineNode) -> Optional[ExecNode]:
        """Compile a timed pipeline"""
        # Compile the pipeline
        pipeline_exec = self.compile_node(node.pipeline)

        # Store timing information for execution
        if pipeline_exec:
            self.timing_info[pipeline_exec.name] = node.duration

        return pipeline_exec
    
    def execute(self, ast: ProgramNode):
        """Execute the compiled pipeline"""
        pipeline = self.compile(ast)
        pipeline.start()

        try:
            # Wait for pipeline to complete or user interrupt
            while pipeline.is_alive():
                import time
                time.sleep(0.1)

                # Process display queue in main thread (only if not in GUI mode)
                # GUI mode will handle display queue processing separately
                try:
                    # Check if we're likely in GUI mode by looking for Qt imports
                    gui_mode = False
                    try:
                        import sys
                        for module_name in sys.modules:
                            if 'PyQt6' in module_name or 'PySide6' in module_name:
                                gui_mode = True
                                break
                    except:
                        pass

                    if not gui_mode:
                        result = _display_manager.process_display_queue()
                        if result is False:  # User pressed 'q' or ESC
                            print("\nStopping pipeline (user pressed quit)...")
                            break

                except Exception as e:
                    print(f"Display processing error: {e}")

        except KeyboardInterrupt:
            print("\nStopping pipeline...")
        finally:
            pipeline.stop()
            pipeline.wait()
            # Clean up display windows
            import cv2
            cv2.destroyAllWindows()