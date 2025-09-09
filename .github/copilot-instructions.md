# VidPipe - Functional Pipeline Language for Video Processing

VidPipe is a Python-based video processing application with a functional pipeline language, featuring both GUI and CLI modes. The application processes real-time video streams using OpenCV with a modular, composable syntax.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup and Dependencies
- Python 3.8+ is required (Python 3.12.3 verified working)
- Install dependencies: `pip install -r requirements.txt`
  - **Timing**: Dependency installation takes ~10 seconds
  - **Core deps**: opencv-python>=4.5.0, numpy>=1.20.0, PyQt6>=6.2.0
  - **Test deps**: pytest>=6.0.0, pytest-qt>=4.0.0

### Build and Test Process
- **No build step required** - VidPipe is a pure Python application
- **Run tests**: `python test_vidpipe.py` - takes <1 second
- **Run pytest**: `pytest test_vidpipe.py -p no:qt -v` - takes <1 second
  - **Note**: pytest-qt may fail in headless environments due to missing display libraries (libEGL.so.1)
  - **Workaround**: Use `-p no:qt` flag to disable Qt plugin
- **Dependencies validation**: All core functionality works without display in CLI mode

### Application Execution
- **CLI Mode**: `python main.py --cli -c "pipeline_code_here"`
- **CLI from file**: `python main.py --cli -f examples/simple.vp`
- **GUI Mode**: `python main.py --gui` (requires display environment with Qt6 support)
- **Debug options**: 
  - `--tokens` - Show tokenization output
  - `--ast` - Show Abstract Syntax Tree
- **Multi-pipeline files**: `python main.py --cli -m examples/multi_pipeline_demo.vp`

### Timing Expectations
- **NEVER CANCEL**: All build and test commands complete in under 30 seconds
- Dependency installation: ~10 seconds (set timeout to 60+ seconds)
- Tests (python test_vidpipe.py): <1 second (set timeout to 30 seconds)
- CLI pipeline parsing: <1 second (set timeout to 30 seconds)
- Multi-pipeline execution: Duration depends on pipeline timing specifications (can be 15+ seconds)

## Validation Scenarios

### Always Test These Scenarios After Changes
1. **Core functionality validation**:
   ```bash
   python test_vidpipe.py
   ```
   
2. **CLI pipeline parsing**:
   ```bash
   python main.py --cli -c "test-pattern -> grayscale -> display" --ast
   ```
   
3. **File-based pipeline execution**:
   ```bash
   python main.py --cli -f examples/simple.vp --tokens
   ```
   
4. **Multi-pipeline functionality**:
   ```bash
   python main.py --cli -m examples/multi_pipeline_demo.vp
   ```

5. **Modular pipeline syntax**:
   ```bash
   echo "pipeline test_pipe = test-pattern -> grayscale
   test_pipe -> display" > /tmp/test_modular.vp
   python main.py --cli -f /tmp/test_modular.vp --ast
   ```

### Manual Testing Guidelines
- **Test pattern pipelines work without camera**: Use `test-pattern` source for testing without hardware
- **GUI testing limitations**: GUI mode requires display libraries (Qt6/libEGL) not available in headless environments
- **Real video processing**: Camera-based pipelines will fail with "Could not open camera 0" in CI environments
- **File output testing**: Use `save` and `record` functions to test pipeline execution without display

## Repository Structure

### Key Directories and Files
```
/home/runner/work/vidpipe/vidpipe/
├── main.py              # Entry point (CLI/GUI modes)
├── requirements.txt     # Dependencies 
├── test_vidpipe.py     # Test suite (4 test functions)
├── vidpipe/            # Core package
│   ├── __init__.py     # Package exports
│   ├── lexer.py        # Tokenization
│   ├── parser.py       # AST generation  
│   ├── runtime.py      # Pipeline execution
│   ├── functions.py    # 23+ video processing functions
│   ├── pipeline.py     # Pipeline data structures
│   └── multi_pipeline.py # Multi-pipeline execution
├── gui/                # PyQt6 GUI components
│   ├── main_window.py  # Main GUI window
│   ├── pipeline_editor.py # Code editor with syntax highlighting
│   └── function_browser.py # Function library browser
├── examples/           # Pipeline example files (.vp extension)
│   ├── simple.vp       # Basic edge detection
│   ├── language_features.vp # Advanced syntax demo
│   ├── modular_pipelines.vp # Pipeline composition
│   └── multi_pipeline_demo.vp # Multi-pipeline execution
└── archive/            # Legacy C implementation (ignore)
```

### Important Files to Monitor
- **Always check `vidpipe/__init__.py`** after adding new modules to package exports
- **Always validate `examples/*.vp`** files after parser changes - they demonstrate language features
- **Always test `test_vidpipe.py`** after core changes - covers lexer, parser, functions, compilation

## Pipeline Language Features

### Basic Syntax
```python
# Simple pipeline
webcam -> grayscale -> edges -> display

# With parameters  
webcam with (camera_id: 0) -> blur with (kernel_size: 5) -> display
```

### Advanced Features Validated to Work
```python
# Pipeline definitions (modular)
pipeline prep = test-pattern -> grayscale
prep -> display

# Timing control (duration specified)
webcam @ 5s -> edges @ 3s -> display

# Multi-pipeline files (sequential and parallel execution)
--pipeline 5s
webcam -> display
--pipeline 8s  
webcam -> edges -> display
```

### 23+ Built-in Functions Available
- **Sources**: webcam, camera, capture, test-pattern
- **Processors**: grayscale, blur, edges, threshold, resize, flip, rotate, crop, brightness, contrast, hue, saturation, gamma, histogram-eq, morphology, contours, corners, optical-flow
- **Sinks**: display, window, save, record

## Development Workflow

### Before Making Changes
1. Run `python test_vidpipe.py` to verify current state
2. Test CLI parsing: `python main.py --cli -c "test-pattern -> display" --ast`

### After Making Changes
1. **Always run tests**: `python test_vidpipe.py`
2. **Test CLI functionality**: `python main.py --cli -c "test-pattern -> grayscale -> display" --tokens`
3. **Validate examples**: `python main.py --cli -f examples/simple.vp --ast`
4. **Test modular pipelines**: Ensure pipeline definitions and references work correctly

### Adding New Functions
```python
# In vidpipe/functions.py
from vidpipe.functions import FunctionRegistry

def my_custom_filter(frame, param1=10, **kwargs):
    # Processing logic here
    return frame

# Register the function
registry = FunctionRegistry()
registry.register("my-filter", my_custom_filter, 
                 description="My custom filter")
```

### Common Issues and Solutions
- **GUI won't start**: Requires display environment with Qt6/PyQt6 libraries
- **pytest-qt fails**: Use `pytest -p no:qt` to disable Qt plugin in headless environments
- **Camera errors**: Expected in CI - use `test-pattern` source for testing
- **Parser errors**: Check pipeline syntax in examples/ for correct language features

## Environment Limitations

### What Works in CI/Headless
- All CLI functionality
- Pipeline parsing and compilation
- Test pattern video processing
- File-based pipeline execution
- Multi-pipeline parsing and timing

### What Requires Display Environment
- GUI mode (`python main.py --gui`)
- Camera input (webcam, camera functions)
- Display output functions
- pytest-qt plugin

### Testing Strategy
- **Use `test-pattern` source** instead of webcam for automated testing
- **Use `save` function** instead of display for output verification
- **Focus on parsing and compilation** rather than actual video processing in CI

## Quick Reference Commands

```bash
# Setup
pip install -r requirements.txt

# Test everything
python test_vidpipe.py

# CLI examples
python main.py --cli -c "test-pattern -> grayscale -> display" --ast
python main.py --cli -f examples/simple.vp --tokens

# Multi-pipeline test
python main.py --cli -m examples/multi_pipeline_demo.vp

# Alternative testing with pytest (if display available)
pytest test_vidpipe.py -v

# Alternative testing without GUI (headless)
pytest test_vidpipe.py -p no:qt -v
```