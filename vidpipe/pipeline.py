"""
Pipeline execution model with async support
"""

import asyncio
import numpy as np
from typing import Any, Optional, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum
import time
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor


class FrameFormat(Enum):
    RGB = "rgb"
    BGR = "bgr"
    GRAY = "gray"
    RGBA = "rgba"


@dataclass
class Frame:
    """Represents a video frame"""
    data: np.ndarray
    format: FrameFormat
    width: int
    height: int
    timestamp: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def copy(self) -> 'Frame':
        """Create a deep copy of the frame"""
        return Frame(
            data=self.data.copy(),
            format=self.format,
            width=self.width,
            height=self.height,
            timestamp=self.timestamp,
            metadata=self.metadata.copy()
        )
    
    @property
    def channels(self) -> int:
        if self.format == FrameFormat.GRAY:
            return 1
        elif self.format == FrameFormat.RGB or self.format == FrameFormat.BGR:
            return 3
        elif self.format == FrameFormat.RGBA:
            return 4
        return 3


class Queue:
    """Thread-safe queue for frame passing"""
    
    def __init__(self, maxsize: int = 0):
        self.queue = deque()
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.closed = False
    
    def put(self, item: Any, timeout: Optional[float] = None):
        """Put an item in the queue"""
        with self.lock:
            if self.closed:
                raise RuntimeError("Queue is closed")
            
            while self.maxsize > 0 and len(self.queue) >= self.maxsize:
                if not self.not_full.wait(timeout):
                    raise TimeoutError("Queue put timed out")
            
            self.queue.append(item)
            self.not_empty.notify()
    
    def get(self, timeout: Optional[float] = None):
        """Get an item from the queue"""
        with self.lock:
            while not self.queue and not self.closed:
                if not self.not_empty.wait(timeout):
                    raise TimeoutError("Queue get timed out")
            
            if self.closed and not self.queue:
                return None
            
            item = self.queue.popleft()
            self.not_full.notify()
            return item
    
    def close(self):
        """Close the queue"""
        with self.lock:
            self.closed = True
            self.not_empty.notify_all()
            self.not_full.notify_all()
    
    def qsize(self) -> int:
        """Get queue size"""
        with self.lock:
            return len(self.queue)


class PipelineNode:
    """Base class for pipeline nodes"""
    
    def __init__(self, name: str, function: Callable, params: Dict[str, Any] = None):
        self.name = name
        self.function = function
        self.params = params or {}
        self.input_queue: Optional[Queue] = None
        self.output_queues: List[Queue] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.is_source = False
        self.is_sink = False
    
    def add_output(self, queue: Queue):
        """Add an output queue"""
        self.output_queues.append(queue)
    
    def set_input(self, queue: Queue):
        """Set the input queue"""
        self.input_queue = queue
    
    def run(self):
        """Main execution loop for the node"""
        self.running = True
        
        try:
            if self.is_source:
                # Source node - generates frames
                while self.running:
                    frame = self.function(None, **self.params)
                    if frame is None:
                        break
                    
                    for queue in self.output_queues:
                        queue.put(frame.copy() if len(self.output_queues) > 1 else frame)
            
            elif self.is_sink:
                # Sink node - consumes frames
                while self.running:
                    frame = self.input_queue.get(timeout=1.0)
                    if frame is None:
                        break

                    result = self.function(frame, **self.params)
                    # Check if sink wants to stop (e.g., user pressed 'q')
                    if result is False:
                        self.running = False
                        break
            
            else:
                # Processing node - transforms frames
                while self.running:
                    frame = self.input_queue.get(timeout=1.0)
                    if frame is None:
                        break
                    
                    result = self.function(frame, **self.params)
                    
                    if result is not None:
                        for queue in self.output_queues:
                            queue.put(result.copy() if len(self.output_queues) > 1 else result)
        
        except Exception as e:
            print(f"Error in node {self.name}: {e}")
        
        finally:
            # Signal downstream nodes that we're done
            for queue in self.output_queues:
                queue.close()
    
    def start(self):
        """Start the node execution in a separate thread"""
        self.thread = threading.Thread(target=self.run, name=f"Node-{self.name}")
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop the node execution"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)


class Pipeline:
    """Manages the execution of a complete pipeline"""
    
    def __init__(self):
        self.nodes: List[PipelineNode] = []
        self.connections: List[tuple] = []
        self.running = False
    
    def add_node(self, node: PipelineNode):
        """Add a node to the pipeline"""
        self.nodes.append(node)
    
    def connect(self, source: PipelineNode, target: PipelineNode, 
                buffer_size: int = 10, async_mode: bool = False):
        """Connect two nodes with a queue"""
        queue = Queue(maxsize=buffer_size)
        source.add_output(queue)
        target.set_input(queue)
        self.connections.append((source, target, queue))
    
    def start(self):
        """Start all nodes in the pipeline"""
        self.running = True
        for node in self.nodes:
            node.start()
    
    def stop(self):
        """Stop all nodes in the pipeline"""
        self.running = False
        for node in self.nodes:
            node.stop()
    
    def wait(self):
        """Wait for all nodes to finish"""
        for node in self.nodes:
            if node.thread:
                node.thread.join()
    
    def is_alive(self) -> bool:
        """Check if pipeline is still running"""
        return any(node.thread and node.thread.is_alive() for node in self.nodes)