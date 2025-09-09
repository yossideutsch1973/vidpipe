# VidPipe - Advanced Functional Pipeline Language for Video Processing

VidPipe is a Python implementation of a **composable functional pipeline language** designed for real-time video processing. It provides an intuitive, declarative syntax for building complex video processing pipelines with advanced features like modularity, timing control, parallel execution, and a sophisticated Qt GUI.

## 🌟 Key Features

- **🎯 Composable Pipeline Language**: Define reusable pipeline components and compose complex workflows
- **⏱️ Timing Control**: Execute pipelines for specific durations with automatic transitions
- **🔄 Parallel Processing**: Run multiple pipelines simultaneously with separate display windows
- **🧩 Modular Architecture**: Build complex systems from simple, reusable components
- **⚡ Real-time Processing**: Efficient threading model for high-performance video processing
- **🎨 Qt GUI**: Professional visual editor with syntax highlighting and function browser
- **📚 Rich Function Library**: 23+ built-in video processing functions
- **🔧 Extensible**: Easy-to-add custom video processing functions
- **🌍 Cross-platform**: Works on Windows, macOS, and Linux

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vidpipe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Installation & Setup
```bash
# Clone the repository
git clone <repository-url>
cd vidpipe

# Install dependencies
pip install -r requirements.txt
```

### Launch GUI (Recommended)
```bash
python main.py  # Launches the visual pipeline editor
```

### Command Line Usage
```bash
# Simple pipeline
python main.py --cli -c "webcam -> grayscale -> display"

# Pipeline from file
python main.py --cli -f examples/modular_pipelines.vp

# Debug options
python main.py --cli -c "webcam -> display" --tokens  # View tokens
python main.py --cli -c "webcam -> display" --ast     # View AST
```

## 🎯 Pipeline Language Syntax

VidPipe features a powerful, composable syntax for building video processing workflows:

### Basic Pipelines
```python
# Simple sequential processing
webcam -> grayscale -> edges -> display

# With parameters
webcam with (camera_id: 0) -> blur with (kernel_size: 5) -> display with (window_name: "Processed")
```

### Advanced Language Features

#### Pipeline Definitions & Composition
```python
# Define reusable pipeline components
pipeline preprocess = webcam -> brightness with (brightness: 20) -> contrast with (contrast: 25)
pipeline analyze = grayscale -> edges -> contours with (min_area: 200)
pipeline display_hd = resize with (width: 1920, height: 1080) -> display

# Compose pipelines
preprocess -> analyze -> display_hd
```

#### Timing Control
```python
# Execute pipelines for specific durations
webcam @ 5s -> edges @ 3s -> display

# Sequential with timing
preprocess @ 3s -> analyze @ 5s -> display_hd
```

#### Parallel Processing
```python
# Run multiple pipelines simultaneously
webcam | edges -> display

# Parallel with composition
(preprocess | analyze) -> display

# Multiple parallel streams
webcam -> (grayscale -> edges | blur with (kernel_size: 7) | threshold) -> display
```

#### Complex Workflows
```python
# Define components
pipeline prep = webcam -> brightness with (brightness: 20)
pipeline detect = grayscale -> edges
pipeline show = display with (window_name: "Analysis")

# Sequential execution
prep @ 2s -> detect @ 3s -> show

# Parallel execution
prep | detect -> show

# Nested composition
pipeline full_analysis = prep -> detect
full_analysis @ 8s -> show
```

#### Multi-Output Processing
```python
# Display and record simultaneously
webcam -> edges -> (display with (window_name: "Live") | record with (filename: "output.avi"))

# Multiple analysis outputs
webcam -> (grayscale -> edges | blur | threshold) -> display
```

## 📚 Built-in Functions (23+ Functions)

### 🎥 Input Sources
- `webcam` - Capture from webcam
- `camera` - Capture from camera (alias for webcam)
- `capture` - Read from video file
- `test-pattern` - Generate synthetic test patterns (checkerboard, gradient)

### 🔧 Processing Functions
- **Color & Brightness**: `grayscale`/`gray`, `brightness`, `contrast`, `hue`, `saturation`, `gamma`, `histogram-eq`
- **Filtering**: `blur`, `morphology` (open/close/erode/dilate)
- **Feature Detection**: `edges`, `corners`, `contours`
- **Geometric**: `resize`, `flip`, `rotate`, `crop`
- **Thresholding**: `threshold`

### 📺 Output Sinks
- `display`/`window` - Show in OpenCV window with custom names
- `save` - Save frames to image files with timestamps
- `record` - Record video to AVI files with configurable FPS

## 🎬 Example Pipelines

### Basic Examples
```python
# Simple edge detection
webcam -> grayscale -> edges -> display

# Enhanced processing with parameters
webcam with (camera_id: 0) -> brightness with (brightness: 30) -> contrast with (contrast: 20) -> display
```

### Advanced Composition
```python
# Define reusable components
pipeline preprocess = webcam -> brightness with (brightness: 20) -> contrast with (contrast: 25)
pipeline analyze = grayscale -> edges -> contours with (min_area: 200)
pipeline display_hd = resize with (width: 1920, height: 1080) -> display

# Compose complex workflows
preprocess -> analyze -> display_hd
```

### Timing & Sequential Execution
```python
# Run each pipeline for specific durations
webcam @ 3s -> edges @ 5s -> contours @ 4s -> display

# Complex sequential workflow
preprocess @ 2s -> analyze @ 4s -> display_hd
```

### Parallel Processing
```python
# Multiple simultaneous pipelines
webcam -> (grayscale -> edges | blur with (kernel_size: 7) | threshold) -> display

# Parallel composition
(preprocess | analyze) -> display
```

### Multi-Output Workflows
```python
# Display and record simultaneously
webcam -> edges -> (display with (window_name: "Live Feed") | record with (filename: "processed.avi", fps: 30))

# Multiple analysis branches
webcam -> (brightness with (brightness: 30) | contrast with (contrast: 40) | gamma with (gamma: 1.2)) -> display
```

### Real-World Applications
```python
# Security monitoring
webcam -> brightness with (brightness: 40) -> histogram-eq -> edges -> display

# Document processing
webcam -> grayscale -> brightness with (brightness: 30) -> contrast with (contrast: 60) -> threshold -> display

# Quality inspection
webcam -> histogram-eq -> contrast with (contrast: 40) -> edges -> contours -> display
```

## 🏗️ Architecture

VidPipe is built with a sophisticated, modular architecture supporting advanced language features:

### Core Components
- **🎯 Enhanced Lexer**: Tokenizes advanced VidPipe syntax (definitions, timing, composition)
- **🔍 Advanced Parser**: Builds rich AST with support for pipeline definitions, references, and timing
- **⚡ Intelligent Runtime**: Compiles AST to executable pipelines with modular composition
- **🔄 Multi-threaded Pipeline**: Advanced thread-based execution with queue management
- **📚 Function Registry**: Extensible library of 23+ video processing functions
- **🎨 Qt GUI**: Professional visual editor with syntax highlighting and pipeline visualization

### Language Features
- **🧩 Pipeline Definitions**: Define reusable pipeline components
- **🔗 Pipeline References**: Compose complex systems from simple parts
- **⏱️ Timing Control**: Execute pipelines for specific durations
- **🔄 Parallel Execution**: Run multiple pipelines simultaneously
- **📊 Multi-threading**: Efficient resource utilization and real-time performance
- **🔧 Error Handling**: Robust exception handling and recovery
- **🌍 Cross-platform**: Consistent behavior across Windows, macOS, and Linux

## 🧪 Testing & Validation

### Run Test Suite
```bash
python test_vidpipe.py
```

### Test Language Features
```python
# Test pipeline definitions and composition
python -c "
from vidpipe import Lexer, Parser, Runtime
code = '''
pipeline prep = webcam -> grayscale
pipeline analyze = edges -> contours
prep -> analyze -> display
'''
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
runtime = Runtime()
pipeline = runtime.compile(ast)
print(f'Compilation successful! {len(pipeline.nodes)} nodes, {len(runtime.pipeline_definitions)} definitions')
"
```

### Debug Options
```bash
# View tokenization
python main.py --cli -c "webcam -> display" --tokens

# View AST structure
python main.py --cli -c "webcam -> display" --ast

# Test timing features
python main.py --cli -c "webcam @ 3s -> edges @ 2s -> display"
```

## Extending VidPipe

### Adding Custom Functions

```python
from vidpipe.functions import FunctionRegistry
from vidpipe.pipeline import Frame

def my_custom_filter(frame: Frame, **kwargs) -> Frame:
    # Your processing code here
    return frame

# Register the function
registry = FunctionRegistry()
registry.register("my-filter", my_custom_filter, description="My custom filter")
```

## 🎨 GUI Features

VidPipe includes a professional Qt-based visual editor with advanced capabilities:

### Editor Features
- **🎯 Enhanced Code Editor**: Full syntax highlighting for all language features (definitions, timing, composition)
- **🔍 Advanced Auto-completion**: Context-aware suggestions for functions and parameters
- **⚡ Real-time Validation**: Instant syntax checking with detailed error reporting
- **📚 Function Browser**: Browse and insert all 23+ built-in functions with parameter descriptions
- **🎨 Syntax Themes**: Multiple color schemes and customizable highlighting

### Pipeline Management
- **📁 File Operations**: Open, save, and manage pipeline files
- **🎬 Pipeline Runner**: Execute pipelines with proper thread management
- **⏹️ Smart Termination**: Graceful pipeline stopping with cleanup
- **📊 Status Monitoring**: Real-time execution status and progress
- **🔧 Error Console**: Detailed error reporting and debugging information

### Advanced GUI Capabilities
- **🧩 Modular Pipeline Support**: Full support for pipeline definitions and composition
- **⏱️ Timing Visualization**: Display execution timing and progress
- **🔄 Parallel Pipeline Display**: Multiple simultaneous pipeline windows
- **📈 Performance Monitoring**: CPU usage and frame rate monitoring
- **🎛️ Parameter Editor**: GUI-based parameter adjustment and testing

### Keyboard Shortcuts
- `Ctrl+N`: New pipeline file
- `Ctrl+O`: Open pipeline file
- `Ctrl+Shift+O`: Open multi-pipeline file
- `Ctrl+S`: Save pipeline
- `Ctrl+Shift+S`: Save pipeline as
- `F5`: Run pipeline
- `Ctrl+C`: Stop pipeline
- `F7`: Validate syntax
- `Ctrl+Q`: Quit application

## 📋 Requirements

### Core Dependencies
- **Python 3.8+** - Modern Python with advanced language features
- **OpenCV 4.5+** - Computer vision library with GPU acceleration
- **NumPy 1.20+** - High-performance numerical computing

### GUI Dependencies
- **PyQt6 6.2+** - Modern Qt6 GUI framework for Python

### Optional Dependencies
- **pytest** - For running test suite
- **pytest-qt** - For GUI testing

### Installation
```bash
# Install core dependencies
pip install opencv-python numpy

# Install GUI (recommended)
pip install PyQt6

# Install development dependencies
pip install pytest pytest-qt
```

### Platform Notes
- **macOS**: Full OpenCV GUI support with threading compatibility
- **Windows**: Native OpenCV window management
- **Linux**: X11/OpenCV integration for display

## 📈 Version History

### v0.2.0 - Advanced Composition & Modularity
- **🧩 Pipeline Definitions**: Define reusable pipeline components with `pipeline name = ...`
- **🔗 Pipeline References**: Compose complex systems from simple parts
- **⏱️ Timing Control**: Execute pipelines for specific durations with `@ duration`
- **🔄 Parallel Execution**: Run multiple pipelines simultaneously with `|`
- **📚 Enhanced Function Library**: Added 23+ video processing functions
- **🎨 Improved GUI**: Professional editor with advanced syntax highlighting
- **🔧 Language Integration**: All features built into core VidPipe syntax
- **⚡ Performance Optimization**: Advanced threading and queue management
- **🧪 Comprehensive Testing**: Extensive test coverage and validation

### v0.1.0 - Initial Release
- Basic pipeline syntax with `->` operator
- Fundamental video processing functions
- Qt-based GUI with syntax highlighting
- Multi-threading support
- Cross-platform compatibility

## 🤝 Contributing

We welcome contributions! VidPipe is designed to be extensible and community-driven.

### Ways to Contribute
- **🐛 Bug Reports**: Found an issue? Let us know!
- **💡 Feature Requests**: Have ideas for new functions or language features?
- **🔧 Code Contributions**: Submit pull requests for enhancements
- **📚 Documentation**: Help improve examples and tutorials
- **🧪 Testing**: Add test cases and improve coverage

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd vidpipe
pip install -r requirements.txt

# Run tests
python test_vidpipe.py

# Test GUI
python main.py --gui
```

### Adding New Functions
```python
from vidpipe.functions import FunctionRegistry

def my_custom_filter(frame, param1=10, **kwargs):
    # Your processing logic here
    return frame

# Register the function
registry = FunctionRegistry()
registry.register("my-filter", my_custom_filter,
                 description="My custom video processing filter")
```

## 📄 License

MIT License - see LICENSE file for details.

---

**🎯 VidPipe - Where Video Processing Meets Functional Programming Excellence**

Transform your video processing workflows with VidPipe's advanced composable language. From simple edge detection to complex multi-stream analysis, VidPipe makes sophisticated computer vision accessible and elegant.

**🚀 Ready to build amazing video processing applications?**

## 🌐 Web Frontend & GitHub Pages

A minimal web frontend is available under the `docs/` directory. Build the TypeScript source with `npm run build` and enable GitHub Pages from the repository settings (main branch, /docs folder) to host it for free.

