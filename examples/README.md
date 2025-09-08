# VidPipe Examples

This directory contains comprehensive examples demonstrating various features and use cases of the VidPipe video processing pipeline language.

## Example Files Overview

### Core Examples
- **`simple.vp`** - Basic webcam edge detection pipeline
- **`with_parameters.vp`** - Using function parameters
- **`multi_processing.vp`** - Parallel processing with choice operator
- **`recording.vp`** - Video recording capabilities
- **`test_pattern.vp`** - Synthetic test pattern generation

### Multi-Pipeline Examples
- **`multi_pipeline_demo.vp`** - Sequential and parallel pipeline execution
- **`comprehensive_demo.vp`** - Complete showcase with timing and multiple streams
- **`modular_pipelines.vp`** - New language features: pipeline definitions, timing, composition
- **`language_features.vp`** - Showcase of all new VidPipe language capabilities

### Advanced Examples
- **`basic_filters.vp`** - Fundamental image processing operations
- **`advanced_processing.vp`** - Sophisticated computer vision techniques
- **`input_sources.vp`** - Different video input methods
- **`output_recording.vp`** - Display and recording options
- **`pipeline_patterns.vp`** - Advanced pipeline architectures
- **`real_world_apps.vp`** - Practical application examples
- **`debugging_testing.vp`** - Testing and debugging techniques
- **`creative_fun.vp`** - Artistic and experimental effects
- **`showcase.vp`** - Comprehensive feature demonstrations

## How to Run Examples

### Command Line
```bash
# Run a specific example
python3 main.py --cli -f examples/simple.vp

# Run with custom pipeline
python3 main.py --cli -c "webcam -> grayscale -> display"

# Run multi-pipeline file
python3 main.py --multi examples/comprehensive_demo.vp
```

### GUI Mode
```bash
python3 main.py --gui
```
Then:
- Copy and paste any example pipeline into the editor and click "Run Pipeline"
- Or use File → Open Multi-Pipeline... to load multi-pipeline files

## Multi-Pipeline Format

Multi-pipeline files allow you to execute multiple pipelines with timing and parallel execution:

### Sequential Execution with Timing
```python
--pipeline 5s
webcam -> display

--pipeline 10s
webcam -> edges -> display
```

### Parallel Execution
```python
--parallel

--pipeline stream1
webcam -> display with (window_name: "Stream 1")

--pipeline stream2
webcam -> edges -> display with (window_name: "Stream 2")

--end
```

### Syntax Elements
- **`--pipeline [duration]s [name]`** - Define a pipeline with optional duration
- **`--parallel`** - Start parallel execution section
- **`--end`** - End parallel section
- **Duration format**: `5s` (seconds), `10s`, `30s`, etc.
- **Pipeline names**: Optional identifiers for organization

## New Language Features (v0.2.0+)

VidPipe now supports advanced language features for pipeline composition and modularity:

### Pipeline Definitions
Define reusable pipeline components:
```python
pipeline preprocess = webcam -> brightness with (brightness: 20)
pipeline analyze = grayscale -> edges -> contours
```

### Pipeline References
Use defined pipelines as building blocks:
```python
preprocess -> analyze -> display
```

### Timing Control
Execute pipelines for specific durations:
```python
webcam -> display @ 5s          # Run for 5 seconds
preprocess -> analyze @ 10s     # Run analysis for 10 seconds
```

### Parallel Execution
Run multiple pipelines simultaneously:
```python
webcam | edges -> display       # Parallel processing
(preprocess | analyze) -> display  # Parallel with composition
```

### Complex Composition
Combine all features for sophisticated workflows:
```python
# Define components
pipeline prep = webcam -> brightness with (brightness: 20)
pipeline detect = grayscale -> edges
pipeline show = display with (window_name: "Analysis")

# Sequential with timing
prep @ 3s -> detect @ 5s -> show

# Parallel execution
prep | detect -> show

# Nested composition
pipeline full_analysis = prep -> detect
full_analysis @ 8s -> show
```

## Pipeline Syntax Reference

### Basic Operators
- **`->`** - Sequential processing (pipe)
- **`|`** - Choice between parallel branches
- **`( )`** - Grouping for complex expressions

### Function Parameters
```python
function_name with (param1: value1, param2: value2)
```

### Available Functions

#### Input Sources
- `webcam` / `camera` - Capture from camera device
- `capture` - Read from video file
- `test-pattern` - Generate synthetic test patterns

#### Processing Functions
- `grayscale` / `gray` - Convert to grayscale
- `blur` - Gaussian blur
- `edges` - Canny edge detection
- `threshold` - Binary thresholding
- `brightness` - Adjust brightness (-100 to 100)
- `contrast` - Adjust contrast (-100 to 100)
- `hue` - Adjust hue (degrees)
- `saturation` - Adjust saturation (-100 to 100)
- `gamma` - Gamma correction (0.1 to 3.0)
- `histogram-eq` - Histogram equalization
- `morphology` - Morphological operations
- `contours` - Contour detection
- `corners` - Harris corner detection
- `crop` - Crop region of interest
- `resize` - Resize frames
- `flip` - Flip horizontally/vertically
- `rotate` - Rotate frames

#### Output Functions
- `display` / `window` - Show in window
- `save` - Save frames to files
- `record` - Record to video file

## Example Categories

### 1. Basic Filters (`basic_filters.vp`)
Demonstrates fundamental image processing operations like brightness, contrast, color adjustments, and gamma correction.

### 2. Advanced Processing (`advanced_processing.vp`)
Shows sophisticated computer vision techniques including morphological operations, contour detection, corner detection, and cropping.

### 3. Input Sources (`input_sources.vp`)
Illustrates different ways to capture or generate video input, including webcam selection and test pattern generation.

### 4. Output & Recording (`output_recording.vp`)
Demonstrates various output methods including display, recording, and simultaneous display + recording.

### 5. Pipeline Patterns (`pipeline_patterns.vp`)
Shows advanced pipeline architectures using parallel processing, choice operators, and complex branching.

### 6. Real-World Applications (`real_world_apps.vp`)
Practical examples for security, document processing, artistic effects, medical imaging, sports analysis, and quality control.

### 7. Debugging & Testing (`debugging_testing.vp`)
Techniques for testing pipelines, validating parameters, and debugging video processing applications.

### 8. Creative & Fun (`creative_fun.vp`)
Artistic and experimental video effects including vintage looks, neon glows, and cinematic styles.

### 9. Showcase (`showcase.vp`)
Comprehensive demonstrations of VidPipe's full capabilities with complex, real-world pipelines.

## Tips for Using Examples

1. **Start Simple**: Begin with `simple.vp` to understand basic pipeline structure
2. **Test Incrementally**: Add one function at a time to understand each processing step
3. **Experiment**: Modify parameters in examples to see how they affect results
4. **Combine**: Mix elements from different examples to create custom pipelines
5. **Debug**: Use test patterns when webcam isn't available for testing

## Common Patterns

### Real-time Processing
```python
webcam -> blur -> edges -> display
```

### Multi-output Processing
```python
webcam -> edges -> (display | record)
```

### Parameterized Processing
```python
webcam -> brightness with (brightness: 30) -> contrast with (contrast: 20) -> display
```

### Parallel Processing
```python
webcam -> (grayscale -> edges | blur | threshold) -> display
```

## Troubleshooting

- **No video display**: Check that camera permissions are granted
- **Performance issues**: Reduce resolution or simplify processing pipeline
- **Parameter errors**: Verify parameter names and value ranges in documentation
- **Recording fails**: Ensure output directory is writable

## Contributing

Add your own examples by creating new `.vp` files with descriptive comments explaining what each pipeline does and why it's useful.
