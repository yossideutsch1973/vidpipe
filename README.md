# VidPipe

VidPipe is a composable pipeline language and runtime for building real-time video processing workflows in Python. The project
pairs a Qt-based visual editor with a command-line runner and an extensible library of OpenCV-powered operations.

## Features

- Functional pipeline syntax with definitions, timing and parallel composition
- Built-in registry of video sources, processors and sinks with shared metadata
- Threaded runtime with OpenCV display management
- Optional Qt GUI featuring a syntax-highlighting editor and function browser

## Installation

```bash
git clone <repository-url>
cd vidpipe
pip install -r requirements.txt
```

Optional frontend tooling used for the static references page can be installed with npm:

```bash
npm install
npm run build  # compiles docs/main.js from src/main.ts
```

## Usage

### Web Editor (NEW!)

```bash
python main.py --web
```

Launches a modern web-based editor that runs in your browser at `http://localhost:8080`. The web editor provides:

- **Real-time pipeline editing** with syntax highlighting
- **Browser-native video processing** using WebRTC and Canvas APIs
- **Live validation** and error checking
- **Interactive examples** and help system
- **Webcam integration** and test pattern generation
- **No desktop dependencies** - works on any modern browser

The web editor supports a subset of VidPipe operations optimized for browser execution, including:
- **Sources**: `webcam`, `test-pattern`
- **Filters**: `grayscale`, `invert`, `sepia`, `edges`, `blur`
- **Sinks**: `display` (renders to web canvas)

### Qt GUI editor

```bash
python main.py --gui
```

Launches the Qt interface with live syntax validation, a function browser backed by the shared registry metadata, and timed
processing of display windows.

### Command line

```bash
python main.py --cli -c "webcam -> grayscale -> display"
python main.py --cli -f examples/simple.vp
```

Pass `--tokens` or `--ast` to inspect lexer and parser output before execution. When running interactively, close any OpenCV
windows or press `q` to stop execution.

### Multi-pipeline files

```bash
python main.py --cli --multi examples/comprehensive_demo.vp
```

Multi-pipeline file syntax and orchestration notes live in [`docs/language_reference.md`](docs/language_reference.md#multi-pipeline-files).

## Documentation

- [`docs/language_reference.md`](docs/language_reference.md) — pipeline syntax, file formats, and the standard function library
- [`docs/architecture_overview.md`](docs/architecture_overview.md) — lexer, parser, runtime and GUI design summary
- [`docs/computer_vision_pipeline_texts.md`](docs/computer_vision_pipeline_texts.md) — curated reading list rendered by the static site

## Development

Run the automated test suite with:

```bash
make test
```

The helper target ensures `pytest` starts without auto-loading the optional
`pytest-qt` plugin, which requires system OpenGL libraries that are usually
missing on headless CI machines.  If you prefer to run the command manually,
export `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` first.

Generated assets (`node_modules/` and `docs/main.js`) are ignored from version
control; rebuild them locally with `npm run build` when you need to refresh the
static site bundle.

For a high-level review of the repository and a list of suggested next steps,
see [`docs/project_status.md`](docs/project_status.md).
