# VidPipe - Pipeline Language for Realtime Video Processing

VidPipe is a functional pipeline language designed for rapid computer vision software implementation. It provides a concise, intuitive syntax for building complex video processing pipelines.

## Language Features

### Basic Pipeline
```
capture-frame -> grayscale -> edges -> display
```

### Parallel Execution
```
capture-frame -> grayscale &> blur &> sharpen
```

### Merging Streams
```
capture-frame -> (grayscale | detect-faces) +> overlay -> display
```

### Buffering and Async
```
capture-frame [10]-> process -> display    # Buffer of 10 frames
capture-frame ~> heavy-process -> display  # Async processing
capture-frame => process -> display        # Sync/blocking
```

## Building

```bash
make
```

## Running

```bash
./vidpipe examples/simple.vp
```

## Examples

See the `examples/` directory for sample pipelines.