"""
Multi-pipeline execution support for VidPipe
Supports sequential and parallel pipeline execution with timing
"""

import time
import threading
from typing import List, Dict, Any, Optional
from . import Lexer, Parser, Runtime


class PipelineStep:
    """Represents a single pipeline step with timing"""

    def __init__(self, code: str, duration: Optional[float] = None, name: str = ""):
        self.code = code.strip()
        self.duration = duration  # in seconds, None means run until stopped
        self.name = name or f"Pipeline_{id(self)}"


class MultiPipelineExecutor:
    """Executes multiple pipelines with timing and parallel support"""

    def __init__(self):
        self.sequential_pipelines: List[PipelineStep] = []
        self.parallel_pipelines: List[PipelineStep] = []
        self.running_pipelines: List[Dict] = []
        self.stop_flag = False

    def parse_multi_pipeline_file(self, file_path: str):
        """Parse a multi-pipeline file"""
        with open(file_path, 'r') as f:
            content = f.read()

        lines = content.split('\n')
        current_pipeline = None
        is_parallel_section = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('--pipeline'):
                # Parse pipeline header
                parts = line.split()
                if len(parts) >= 2:
                    pipeline_name = parts[1]
                    duration = None

                    # Check if first part is a duration (ends with 's')
                    if parts[1].endswith('s'):
                        try:
                            duration = float(parts[1][:-1])  # Remove 's' suffix
                            pipeline_name = parts[2] if len(parts) >= 3 else f"Pipeline_{len(self.sequential_pipelines) + len(self.parallel_pipelines) + 1}"
                        except ValueError:
                            pass
                    # Check if second part is a duration
                    elif len(parts) >= 3 and parts[2].endswith('s'):
                        try:
                            duration = float(parts[2][:-1])  # Remove 's' suffix
                        except ValueError:
                            pass

                    current_pipeline = PipelineStep("", duration, pipeline_name)
                    if is_parallel_section:
                        self.parallel_pipelines.append(current_pipeline)
                    else:
                        self.sequential_pipelines.append(current_pipeline)

            elif line.startswith('--parallel'):
                is_parallel_section = True
                current_pipeline = None

            elif line.startswith('--end'):
                break

            elif current_pipeline is not None:
                # Add line to current pipeline
                if current_pipeline.code:
                    current_pipeline.code += '\n'
                current_pipeline.code += line

        # Clean up any empty pipelines
        self.sequential_pipelines = [p for p in self.sequential_pipelines if p.code.strip()]
        self.parallel_pipelines = [p for p in self.parallel_pipelines if p.code.strip()]

    def execute_sequential(self):
        """Execute pipelines sequentially with timing"""
        print(f"Executing {len(self.sequential_pipelines)} sequential pipelines...")

        for i, pipeline in enumerate(self.sequential_pipelines):
            if self.stop_flag:
                break

            print(f"\n--- Pipeline {i+1}/{len(self.sequential_pipelines)}: {pipeline.name} ---")
            if pipeline.duration:
                print(f"Running for {pipeline.duration} seconds...")
            else:
                print("Running until stopped...")

            # Execute the pipeline
            pipeline_thread = threading.Thread(target=self._execute_single_pipeline, args=(pipeline,))
            pipeline_thread.start()

            # Wait for duration or until stopped
            if pipeline.duration:
                start_time = time.time()
                while time.time() - start_time < pipeline.duration and not self.stop_flag:
                    time.sleep(0.1)
            else:
                # Wait until stopped
                while pipeline_thread.is_alive() and not self.stop_flag:
                    time.sleep(0.1)

            # Stop the pipeline
            if pipeline_thread.is_alive():
                print(f"Stopping pipeline: {pipeline.name}")
                # Note: In a real implementation, we'd need a way to stop individual pipelines

        print("\nSequential execution completed!")

    def execute_parallel(self):
        """Execute pipelines in parallel"""
        print(f"Executing {len(self.parallel_pipelines)} parallel pipelines...")

        threads = []
        for pipeline in self.parallel_pipelines:
            if self.stop_flag:
                break

            print(f"Starting parallel pipeline: {pipeline.name}")
            thread = threading.Thread(target=self._execute_single_pipeline, args=(pipeline,))
            thread.start()
            threads.append(thread)

        # Wait for all pipelines to complete or stop signal
        for thread in threads:
            thread.join()

        print("Parallel execution completed!")

    def execute_all(self):
        """Execute all pipelines (sequential first, then parallel)"""
        self.stop_flag = False

        if self.sequential_pipelines:
            self.execute_sequential()

        if self.parallel_pipelines:
            self.execute_parallel()

    def stop(self):
        """Stop all pipeline execution"""
        print("Stopping all pipelines...")
        self.stop_flag = True

    def _execute_single_pipeline(self, pipeline: PipelineStep):
        """Execute a single pipeline"""
        try:
            print(f"Executing pipeline: {pipeline.name}")
            print(f"Code: {pipeline.code[:50]}...")

            # Parse and execute the pipeline
            lexer = Lexer(pipeline.code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            runtime = Runtime()
            runtime.execute(ast)

        except Exception as e:
            print(f"Error in pipeline {pipeline.name}: {e}")
            import traceback
            traceback.print_exc()


def execute_multi_pipeline_file(file_path: str):
    """Convenience function to execute a multi-pipeline file"""
    executor = MultiPipelineExecutor()
    executor.parse_multi_pipeline_file(file_path)
    executor.execute_all()


if __name__ == "__main__":
    # Test the multi-pipeline executor
    import sys
    if len(sys.argv) > 1:
        execute_multi_pipeline_file(sys.argv[1])
    else:
        print("Usage: python multi_pipeline.py <pipeline_file>")
