# VidPipe Web Interface

VidPipe now includes a modern web-based editor that allows you to run video processing pipelines directly in your browser without any desktop dependencies.

## Features

### 🌐 Browser-Native Processing
- Uses WebRTC for camera access
- Canvas API for real-time image processing 
- No plugins or external software required
- Works on any modern browser (Chrome, Firefox, Safari, Edge)

### 🎨 Interactive Editor
- Live syntax highlighting and validation
- Real-time pipeline parsing with token visualization
- Interactive examples with one-click loading
- Comprehensive help system with function documentation

### 📹 Video Processing
- **Webcam source**: Direct camera access via `webcam`
- **Test patterns**: Generated patterns via `test-pattern`
- **Real-time filters**: `grayscale`, `invert`, `sepia`, `edges`, `blur`
- **Canvas display**: Live video output with effects applied

### 💻 Modern UI
- Split-panel design: editor on left, video output on right
- Responsive layout works on desktop and tablet
- Clean, professional interface matching the Qt GUI
- Status indicators and real-time logging

## Quick Start

1. **Start the web server**:
   ```bash
   python main.py --web
   ```

2. **Open your browser** to `http://localhost:8080`

3. **Try an example**:
   - Click "Test Pattern" to load a simple pipeline
   - Click "Validate" to check syntax
   - Click "Run Pipeline" to execute

4. **Use webcam**:
   - Click "Edge Detection" example
   - Click "Run Pipeline" 
   - Allow camera access when prompted

## Supported Pipeline Syntax

The web editor supports the core VidPipe syntax:

```
source -> filter -> filter -> sink
```

### Available Functions

**Sources:**
- `webcam` - Capture from camera (requires permission)
- `test-pattern` - Generate checkerboard test pattern

**Filters:**
- `grayscale` - Convert to grayscale
- `invert` - Invert all colors
- `sepia` - Apply sepia tone effect
- `edges` - Sobel edge detection
- `blur` - Box blur filter

**Sinks:**
- `display` - Show in web video panel

### Example Pipelines

```bash
# Basic webcam with edge detection
webcam -> grayscale -> edges -> display

# Test pattern with sepia effect  
test-pattern -> sepia -> display

# Color inversion
webcam -> invert -> display

# Multiple effects
test-pattern -> grayscale -> blur -> display
```

## Technical Implementation

### Architecture
- **Frontend**: TypeScript/ES6 with modern web APIs
- **Video Processing**: Canvas 2D context for pixel manipulation
- **Pipeline Parsing**: Complete lexer implementation matching Python version
- **Build System**: TypeScript compiler with ES6 modules

### Browser Compatibility
- **Chrome/Chromium**: Full support
- **Firefox**: Full support  
- **Safari**: Full support (iOS 11+)
- **Edge**: Full support

### Security
- All processing happens locally in the browser
- No data is sent to external servers
- Camera access requires explicit user permission
- Follows modern web security best practices

## Limitations

The web version implements a subset of the full VidPipe functionality:

- **Limited function library**: Core image processing only
- **No file I/O**: Cannot save/load video files 
- **No external dependencies**: Cannot use OpenCV advanced features
- **Performance**: JavaScript is slower than native Python/OpenCV

## Development

### Building from Source

```bash
# Install TypeScript (if not already installed)
npm install

# Compile TypeScript to JavaScript
npm run build

# Start development server
python web_server.py
```

### File Structure

```
docs/
├── index.html          # Main web interface
├── web-editor.js       # Compiled TypeScript application
├── main.js            # Original reference loader
└── *.md               # Documentation files

src/
├── web-editor.ts      # TypeScript source
└── main.ts           # Original TypeScript reference loader
```

### Adding New Filters

To add a new image processing filter:

1. **Add filter function** to `WebVideoProcessor.applyPipelineEffects()`
2. **Implement pixel manipulation** in new method
3. **Update help text** in `WebEditor.showHelp()`
4. **Add example** if desired

Example filter implementation:

```typescript
private applyBrightness(data: Uint8ClampedArray, amount: number = 50): void {
  for (let i = 0; i < data.length; i += 4) {
    data[i] = Math.min(255, data[i] + amount);     // Red
    data[i + 1] = Math.min(255, data[i + 1] + amount); // Green  
    data[i + 2] = Math.min(255, data[i + 2] + amount); // Blue
  }
}
```

## Troubleshooting

### Camera Not Working
- Ensure you're accessing via `http://localhost` (not file://)
- Check browser permissions for camera access
- Try a different browser if issues persist

### Pipeline Not Running
- Check syntax with "Validate" button first
- Look for error messages in the output console
- Ensure you're using supported functions only

### Performance Issues
- Use smaller video resolution if processing is slow
- Reduce complex filter chains
- Try different browser for better performance

## Future Enhancements

- **WebAssembly**: Port core algorithms for better performance
- **WebGL**: GPU-accelerated image processing
- **WebCodecs**: Advanced video encoding/decoding
- **File Upload**: Support for video file processing
- **More Filters**: Extended function library
- **Mobile Support**: Touch-optimized interface