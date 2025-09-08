# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VidPipe is a functional pipeline language for realtime video processing implemented in C. It provides a concise, intuitive syntax for building complex video processing pipelines with automatic parallelization and buffering.

## Common Commands

```bash
# Build the project
make

# Run interactive mode
make interactive

# Run examples
make run-simple      # Basic edge detection
make run-parallel    # Parallel processing
make run-buffered    # Buffered async processing
make run-camera      # Camera capture demo
make run-webcam      # Live webcam feed

# Clean build files
make clean

# Run from command line
./vidpipe -c "capture -> grayscale -> edges -> display"
./vidpipe -c "webcam -> window"                          # Live camera feed
./vidpipe -c "webcam -> grayscale -> edges -> window"    # Live edge detection

# Run from file
./vidpipe examples/simple.vp
./vidpipe examples/camera_demo.vp
```

## Architecture

### Language Design
- **Pure functional**: Each processing function is side-effect free
- **Pipeline operators**:
  - `->` : Synchronous pipeline
  - `~>` : Asynchronous pipeline
  - `=>` : Explicit synchronous (blocking)
  - `&>` : Parallel branching
  - `+>` : Stream merging
  - `|` : Choice/selection
  - `[n]->` : Buffered connection with n frames
  - `{}` : Loop construct (continuous execution)

### Core Components

1. **Lexer** (`lexer.c`): Tokenizes VidPipe source code into tokens
2. **Parser** (`parser.c`): Builds Abstract Syntax Tree (AST) from tokens
3. **Runtime** (`runtime.c`): 
   - Thread-based execution model
   - Lock-free queues for inter-function communication
   - Automatic thread pool management
4. **Functions** (`functions.c`): Built-in video processing functions
5. **Main** (`main.c`): CLI interface and pipeline executor

### Execution Model
- Each function runs in its own thread
- Frames flow through queues between functions
- Automatic buffering and backpressure handling
- Support for multiple execution units (CPU, GPU planned)

### Frame Structure
```c
typedef struct {
    uint8_t* data;       // Raw pixel data
    int width, height;   // Dimensions
    int channels;        // 1 (grayscale) or 3 (RGB)
    uint64_t timestamp;  // Frame timestamp
    void* metadata;      // Optional metadata
} Frame;
```

## Adding New Functions

To add a new video processing function:

1. Implement the function in `functions.c`:
```c
Frame* my_function(Frame* input, void* params) {
    // Process input frame
    // Return output frame (or NULL for sinks)
}
```

2. Register it in `register_builtin_functions()`:
```c
registry_add(registry, "my-func", my_function, NULL, false, false);
```

Parameters: name, function, params, is_source, is_sink

## Language Examples

```
# Simple pipeline
capture -> grayscale -> edges -> display

# Live camera feed
webcam -> window

# Live camera with processing
webcam -> grayscale -> edges -> window

# Continuous loops (keeps running)
{webcam -> window}
{webcam -> grayscale -> edges -> window}

# Parallel processing
capture -> grayscale &> blur &> edges

# Buffered async
capture [20]-> heavy-process ~> display

# Complex with merge
capture -> (edges | blur) +> overlay -> display
```