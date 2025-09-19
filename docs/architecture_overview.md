# Architecture Overview

VidPipe is composed of a compact compiler toolchain, a threaded runtime, and an optional Qt6 interface. This page condenses the
information that previously lived in multiple review documents.

## Compiler front-end

1. **Lexer (`vidpipe/lexer.py`)** — Tokenises the pipeline language, covering definitions, references, timing modifiers and
   grouped expressions. Tokens carry line and column data for clear diagnostics.
2. **Parser (`vidpipe/parser.py`)** — Recursive-descent parser that converts tokens into a typed AST. Operator precedence keeps
   sequential composition tighter than parallel branching, and timed pipelines wrap subtrees alongside duration metadata.
3. **AST nodes (`vidpipe/ast_nodes.py`)** — Data classes that describe pipeline structure. The runtime consumes these nodes when
   assembling executable graphs.

## Runtime

- **Function registry (`vidpipe/functions.py`)** — Central store for source, processor and sink definitions. Metadata such as
  human-readable descriptions and parameter hints is shared with the GUI function browser.
- **Pipeline executor (`vidpipe/pipeline.py`)** — Manages node threads, buffer queues and lifecycle hooks. Each function runs in a
  worker that pulls from upstream queues and pushes downstream frames.
- **Runtime orchestrator (`vidpipe/runtime.py`)** — Compiles AST nodes into pipeline graphs, assigns buffer sizes, and coordinates
  execution. It exposes a hook so the caller can decide who owns the OpenCV display loop.

## GUI

The Qt6 application in `gui/` layers editor ergonomics onto the runtime:

- `PipelineEditor` provides syntax-highlighting and validation timers.
- `FunctionBrowser` reflects the shared registry metadata so new functions appear automatically with their parameters.
- `PipelineRunner` executes code on a worker thread while the main window periodically pumps the display manager to keep OpenCV
  windows responsive.

## Multi-pipeline execution

`vidpipe/multi_pipeline.py` parses orchestrated pipeline files, scheduling sequential steps before optional parallel sections.
The executor owns the OpenCV display loop in CLI mode, so closing a window propagates a stop signal to all running pipelines.
