/**
 * VidPipe Web Editor - Browser-based pipeline editor and runtime
 */

// Token types (matching Python implementation)
enum TokenType {
  SYNC_PIPE = 'SYNC_PIPE',         // ->
  ASYNC_PIPE = 'ASYNC_PIPE',       // ~>
  BLOCKING_PIPE = 'BLOCKING_PIPE', // =>
  PARALLEL = 'PARALLEL',           // &>
  MERGE = 'MERGE',                 // +>
  CHOICE = 'CHOICE',               // |
  LPAREN = 'LPAREN',               // (
  RPAREN = 'RPAREN',               // )
  LBRACKET = 'LBRACKET',           // [
  RBRACKET = 'RBRACKET',           // ]
  LBRACE = 'LBRACE',               // {
  RBRACE = 'RBRACE',               // }
  IDENTIFIER = 'IDENTIFIER',       // function names
  NUMBER = 'NUMBER',               // buffer sizes, parameters
  STRING = 'STRING',               // string parameters
  COMMA = 'COMMA',                 // ,
  COLON = 'COLON',                 // :
  EOF = 'EOF',                     // End of file
  WITH = 'WITH',                   // with keyword
  PIPELINE = 'PIPELINE',           // pipeline keyword
  AT = 'AT',                       // @ timing operator
  EQUALS = 'EQUALS'                // = assignment
}

interface Token {
  type: TokenType;
  value: any;
  line: number;
  column: number;
}

// Frame representation for web
interface WebFrame {
  canvas: HTMLCanvasElement;
  width: number;
  height: number;
  timestamp: number;
  metadata: Record<string, any>;
}

// Web-based lexer
class WebLexer {
  private source: string;
  private position: number = 0;
  private line: number = 1;
  private column: number = 1;

  constructor(source: string) {
    this.source = source;
  }

  private peek(offset: number = 0): string | null {
    const pos = this.position + offset;
    return pos < this.source.length ? this.source[pos] : null;
  }

  private advance(): string | null {
    if (this.position < this.source.length) {
      const char = this.source[this.position];
      this.position++;
      if (char === '\n') {
        this.line++;
        this.column = 1;
      } else {
        this.column++;
      }
      return char;
    }
    return null;
  }

  private skipWhitespace(): void {
    while (this.peek() && /\s/.test(this.peek()!)) {
      this.advance();
    }
  }

  private skipComment(): boolean {
    if (this.peek() === '#') {
      while (this.peek() && this.peek() !== '\n') {
        this.advance();
      }
      return true;
    }
    return false;
  }

  private readNumber(): Token {
    const startLine = this.line;
    const startColumn = this.column;
    let numStr = '';

    while (this.peek() && (/\d/.test(this.peek()!) || this.peek() === '.')) {
      numStr += this.advance();
    }

    const value = numStr.includes('.') ? parseFloat(numStr) : parseInt(numStr);
    return { type: TokenType.NUMBER, value, line: startLine, column: startColumn };
  }

  private readString(): Token {
    const startLine = this.line;
    const startColumn = this.column;
    const quoteChar = this.advance(); // Skip opening quote
    let stringVal = '';

    while (this.peek() && this.peek() !== quoteChar) {
      const char = this.advance();
      if (char === '\\' && this.peek()) {
        const nextChar = this.advance();
        switch (nextChar) {
          case 'n': stringVal += '\n'; break;
          case 't': stringVal += '\t'; break;
          case '\\': stringVal += '\\'; break;
          default: stringVal += nextChar; break;
        }
      } else {
        stringVal += char;
      }
    }

    if (this.peek() === quoteChar) {
      this.advance(); // Skip closing quote
    }

    return { type: TokenType.STRING, value: stringVal, line: startLine, column: startColumn };
  }

  private readIdentifier(): Token {
    const startLine = this.line;
    const startColumn = this.column;
    let identifier = '';

    while (this.peek() && (/\w/.test(this.peek()!) || this.peek() === '-')) {
      identifier += this.advance();
    }

    // Check for keywords
    let tokenType = TokenType.IDENTIFIER;
    switch (identifier) {
      case 'with': tokenType = TokenType.WITH; break;
      case 'pipeline': tokenType = TokenType.PIPELINE; break;
    }

    return { type: tokenType, value: identifier, line: startLine, column: startColumn };
  }

  tokenize(): Token[] {
    const tokens: Token[] = [];

    while (this.position < this.source.length) {
      this.skipWhitespace();

      if (this.position >= this.source.length) break;

      if (this.skipComment()) continue;

      const char = this.peek();
      if (!char) break;

      const startLine = this.line;
      const startColumn = this.column;

      // Multi-character operators
      if (char === '-' && this.peek(1) === '>') {
        this.advance(); this.advance();
        tokens.push({ type: TokenType.SYNC_PIPE, value: '->', line: startLine, column: startColumn });
      } else if (char === '~' && this.peek(1) === '>') {
        this.advance(); this.advance();
        tokens.push({ type: TokenType.ASYNC_PIPE, value: '~>', line: startLine, column: startColumn });
      } else if (char === '=' && this.peek(1) === '>') {
        this.advance(); this.advance();
        tokens.push({ type: TokenType.BLOCKING_PIPE, value: '=>', line: startLine, column: startColumn });
      } else if (char === '&' && this.peek(1) === '>') {
        this.advance(); this.advance();
        tokens.push({ type: TokenType.PARALLEL, value: '&>', line: startLine, column: startColumn });
      } else if (char === '+' && this.peek(1) === '>') {
        this.advance(); this.advance();
        tokens.push({ type: TokenType.MERGE, value: '+>', line: startLine, column: startColumn });
      }
      // Single character tokens
      else if (char === '(') {
        this.advance();
        tokens.push({ type: TokenType.LPAREN, value: '(', line: startLine, column: startColumn });
      } else if (char === ')') {
        this.advance();
        tokens.push({ type: TokenType.RPAREN, value: ')', line: startLine, column: startColumn });
      } else if (char === '[') {
        this.advance();
        tokens.push({ type: TokenType.LBRACKET, value: '[', line: startLine, column: startColumn });
      } else if (char === ']') {
        this.advance();
        tokens.push({ type: TokenType.RBRACKET, value: ']', line: startLine, column: startColumn });
      } else if (char === '{') {
        this.advance();
        tokens.push({ type: TokenType.LBRACE, value: '{', line: startLine, column: startColumn });
      } else if (char === '}') {
        this.advance();
        tokens.push({ type: TokenType.RBRACE, value: '}', line: startLine, column: startColumn });
      } else if (char === ',') {
        this.advance();
        tokens.push({ type: TokenType.COMMA, value: ',', line: startLine, column: startColumn });
      } else if (char === ':') {
        this.advance();
        tokens.push({ type: TokenType.COLON, value: ':', line: startLine, column: startColumn });
      } else if (char === '=') {
        this.advance();
        tokens.push({ type: TokenType.EQUALS, value: '=', line: startLine, column: startColumn });
      } else if (char === '@') {
        this.advance();
        tokens.push({ type: TokenType.AT, value: '@', line: startLine, column: startColumn });
      } else if (char === '|') {
        this.advance();
        tokens.push({ type: TokenType.CHOICE, value: '|', line: startLine, column: startColumn });
      }
      // Numbers
      else if (/\d/.test(char)) {
        tokens.push(this.readNumber());
      }
      // Strings
      else if (char === '"' || char === "'") {
        tokens.push(this.readString());
      }
      // Identifiers
      else if (/[a-zA-Z_]/.test(char)) {
        tokens.push(this.readIdentifier());
      }
      // Unknown character
      else {
        throw new Error(`Unknown character '${char}' at line ${this.line}, column ${this.column}`);
      }
    }

    tokens.push({ type: TokenType.EOF, value: null, line: this.line, column: this.column });
    return tokens;
  }
}

// Web-based video processing functions
class WebVideoProcessor {
  private stream: MediaStream | null = null;
  private video: HTMLVideoElement;
  private canvas: HTMLCanvasElement;
  private context: CanvasRenderingContext2D;
  private isRunning: boolean = false;
  private pipeline: string = '';

  constructor(videoElement: HTMLVideoElement, canvasElement: HTMLCanvasElement) {
    this.video = videoElement;
    this.canvas = canvasElement;
    this.context = this.canvas.getContext('2d')!;
  }

  async initWebcam(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      this.video.srcObject = this.stream;
      await new Promise((resolve) => {
        this.video.onloadedmetadata = () => resolve(void 0);
      });
    } catch (error) {
      throw new Error(`Failed to access webcam: ${error}`);
    }
  }

  stopWebcam(): void {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    this.video.srcObject = null;
  }

  startProcessing(pipeline: string): void {
    this.pipeline = pipeline;
    this.isRunning = true;
    this.processFrame();
  }

  stopProcessing(): void {
    this.isRunning = false;
  }

  private processFrame(): void {
    if (!this.isRunning) return;

    if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;
      
      // Draw video frame to canvas
      this.context.drawImage(this.video, 0, 0);
      
      // Apply pipeline processing
      this.applyPipelineEffects();
    }

    requestAnimationFrame(() => this.processFrame());
  }

  private applyPipelineEffects(): void {
    const imageData = this.context.getImageData(0, 0, this.canvas.width, this.canvas.height);
    const data = imageData.data;

    // Simple pipeline parsing and effect application
    if (this.pipeline.includes('grayscale')) {
      this.applyGrayscale(data);
    }
    if (this.pipeline.includes('invert')) {
      this.applyInvert(data);
    }
    if (this.pipeline.includes('sepia')) {
      this.applySepia(data);
    }
    if (this.pipeline.includes('edges')) {
      this.applyEdgeDetection(imageData);
      return; // Edge detection replaces the entire image
    }
    if (this.pipeline.includes('blur')) {
      this.applyBlur(imageData);
      return;
    }

    this.context.putImageData(imageData, 0, 0);
  }

  private applyGrayscale(data: Uint8ClampedArray): void {
    for (let i = 0; i < data.length; i += 4) {
      const gray = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114;
      data[i] = gray;     // Red
      data[i + 1] = gray; // Green
      data[i + 2] = gray; // Blue
    }
  }

  private applyInvert(data: Uint8ClampedArray): void {
    for (let i = 0; i < data.length; i += 4) {
      data[i] = 255 - data[i];         // Red
      data[i + 1] = 255 - data[i + 1]; // Green
      data[i + 2] = 255 - data[i + 2]; // Blue
    }
  }

  private applySepia(data: Uint8ClampedArray): void {
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      
      data[i] = Math.min(255, (r * 0.393) + (g * 0.769) + (b * 0.189));
      data[i + 1] = Math.min(255, (r * 0.349) + (g * 0.686) + (b * 0.168));
      data[i + 2] = Math.min(255, (r * 0.272) + (g * 0.534) + (b * 0.131));
    }
  }

  private applyEdgeDetection(imageData: ImageData): void {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;
    const output = new Uint8ClampedArray(data.length);

    // Simple Sobel edge detection
    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const idx = (y * width + x) * 4;
        
        // Get surrounding pixels
        const pixels = [
          this.getGrayValue(data, (y - 1) * width + (x - 1)),
          this.getGrayValue(data, (y - 1) * width + x),
          this.getGrayValue(data, (y - 1) * width + (x + 1)),
          this.getGrayValue(data, y * width + (x - 1)),
          this.getGrayValue(data, y * width + x),
          this.getGrayValue(data, y * width + (x + 1)),
          this.getGrayValue(data, (y + 1) * width + (x - 1)),
          this.getGrayValue(data, (y + 1) * width + x),
          this.getGrayValue(data, (y + 1) * width + (x + 1))
        ];

        // Sobel kernels
        const sobelX = (-1 * pixels[0]) + (1 * pixels[2]) +
                       (-2 * pixels[3]) + (2 * pixels[5]) +
                       (-1 * pixels[6]) + (1 * pixels[8]);
        
        const sobelY = (-1 * pixels[0]) + (-2 * pixels[1]) + (-1 * pixels[2]) +
                       (1 * pixels[6]) + (2 * pixels[7]) + (1 * pixels[8]);

        const magnitude = Math.sqrt(sobelX * sobelX + sobelY * sobelY);
        const edge = magnitude > 50 ? 255 : 0;

        output[idx] = edge;
        output[idx + 1] = edge;
        output[idx + 2] = edge;
        output[idx + 3] = 255; // Alpha
      }
    }

    for (let i = 0; i < data.length; i++) {
      data[i] = output[i];
    }
  }

  private applyBlur(imageData: ImageData): void {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;
    const output = new Uint8ClampedArray(data.length);

    // Simple box blur
    const radius = 2;
    for (let y = radius; y < height - radius; y++) {
      for (let x = radius; x < width - radius; x++) {
        let r = 0, g = 0, b = 0, count = 0;
        
        for (let dy = -radius; dy <= radius; dy++) {
          for (let dx = -radius; dx <= radius; dx++) {
            const idx = ((y + dy) * width + (x + dx)) * 4;
            r += data[idx];
            g += data[idx + 1];
            b += data[idx + 2];
            count++;
          }
        }

        const idx = (y * width + x) * 4;
        output[idx] = r / count;
        output[idx + 1] = g / count;
        output[idx + 2] = b / count;
        output[idx + 3] = 255;
      }
    }

    for (let i = 0; i < data.length; i++) {
      data[i] = output[i];
    }
  }

  private getGrayValue(data: Uint8ClampedArray, pixelIndex: number): number {
    const idx = pixelIndex * 4;
    return data[idx] * 0.299 + data[idx + 1] * 0.587 + data[idx + 2] * 0.114;
  }

  generateTestPattern(): void {
    this.canvas.width = 640;
    this.canvas.height = 480;
    
    // Generate a checkerboard pattern
    const squareSize = 40;
    for (let y = 0; y < this.canvas.height; y += squareSize) {
      for (let x = 0; x < this.canvas.width; x += squareSize) {
        const isBlack = ((x / squareSize) + (y / squareSize)) % 2 === 0;
        this.context.fillStyle = isBlack ? '#000' : '#fff';
        this.context.fillRect(x, y, squareSize, squareSize);
      }
    }
  }
}

// Main Web Editor Application
class WebEditor {
  private processor: WebVideoProcessor;
  private isRunning: boolean = false;

  constructor() {
    const video = document.getElementById('video-display') as HTMLVideoElement;
    const canvas = document.getElementById('canvas-display') as HTMLCanvasElement;
    this.processor = new WebVideoProcessor(video, canvas);
    
    this.initializeUI();
  }

  private initializeUI(): void {
    const editor = document.getElementById('pipeline-editor') as HTMLTextAreaElement;
    const runBtn = document.getElementById('run-btn') as HTMLButtonElement;
    const stopBtn = document.getElementById('stop-btn') as HTMLButtonElement;
    const validateBtn = document.getElementById('validate-btn') as HTMLButtonElement;
    const helpBtn = document.getElementById('help-btn') as HTMLButtonElement;
    const output = document.getElementById('output') as HTMLDivElement;
    const status = document.getElementById('status') as HTMLDivElement;

    // Example buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const example = (e.target as HTMLButtonElement).dataset.example;
        if (example) {
          editor.value = example;
        }
      });
    });

    runBtn.addEventListener('click', async () => {
      if (this.isRunning) return;
      
      try {
        const pipeline = editor.value.trim();
        if (!pipeline) {
          this.log('Please enter a pipeline first.', 'error');
          return;
        }

        this.log('Starting pipeline...', 'info');
        status.textContent = 'Starting...';
        
        // Validate pipeline first
        try {
          const lexer = new WebLexer(pipeline);
          const tokens = lexer.tokenize();
          this.log(`Parsed ${tokens.length - 1} tokens`, 'success');
        } catch (error) {
          this.log(`Syntax error: ${error}`, 'error');
          return;
        }

        // Initialize video source
        if (pipeline.includes('webcam')) {
          await this.processor.initWebcam();
          this.log('Webcam initialized', 'success');
        } else if (pipeline.includes('test-pattern')) {
          this.processor.generateTestPattern();
          this.log('Test pattern generated', 'success');
        }

        // Start processing
        this.processor.startProcessing(pipeline);
        this.isRunning = true;
        
        runBtn.disabled = true;
        stopBtn.disabled = false;
        status.textContent = 'Running';
        
        this.log('Pipeline started successfully', 'success');
        
      } catch (error) {
        this.log(`Error: ${error}`, 'error');
        status.textContent = 'Error';
      }
    });

    stopBtn.addEventListener('click', () => {
      this.stop();
    });

    validateBtn.addEventListener('click', () => {
      const pipeline = editor.value.trim();
      if (!pipeline) {
        this.log('Please enter a pipeline to validate.', 'error');
        return;
      }

      try {
        const lexer = new WebLexer(pipeline);
        const tokens = lexer.tokenize();
        this.log(`✓ Valid syntax. Parsed ${tokens.length - 1} tokens.`, 'success');
        
        // Show tokens for debugging
        const tokenStr = tokens.slice(0, -1).map(t => 
          `${t.type}(${typeof t.value === 'string' ? `"${t.value}"` : t.value})`
        ).join(' ');
        this.log(`Tokens: ${tokenStr}`, 'info');
        
      } catch (error) {
        this.log(`✗ Syntax error: ${error}`, 'error');
      }
    });

    helpBtn.addEventListener('click', () => {
      this.showHelp();
    });
  }

  private stop(): void {
    if (!this.isRunning) return;
    
    this.processor.stopProcessing();
    this.processor.stopWebcam();
    this.isRunning = false;
    
    const runBtn = document.getElementById('run-btn') as HTMLButtonElement;
    const stopBtn = document.getElementById('stop-btn') as HTMLButtonElement;
    const status = document.getElementById('status') as HTMLDivElement;
    
    runBtn.disabled = false;
    stopBtn.disabled = true;
    status.textContent = 'Stopped';
    
    this.log('Pipeline stopped', 'info');
  }

  private log(message: string, type: 'info' | 'success' | 'error' = 'info'): void {
    const output = document.getElementById('output') as HTMLDivElement;
    const timestamp = new Date().toLocaleTimeString();
    const className = type === 'error' ? 'error' : type === 'success' ? 'success' : '';
    
    output.innerHTML += `<div class="${className}">[${timestamp}] ${message}</div>`;
    output.scrollTop = output.scrollHeight;
  }

  private showHelp(): void {
    this.log('=== VidPipe Web Help ===', 'info');
    this.log('Available sources:', 'info');
    this.log('  webcam - Capture from camera', 'info');
    this.log('  test-pattern - Generate test pattern', 'info');
    this.log('', 'info');
    this.log('Available filters:', 'info');
    this.log('  grayscale - Convert to grayscale', 'info');
    this.log('  invert - Invert colors', 'info');
    this.log('  sepia - Apply sepia tone', 'info');
    this.log('  edges - Edge detection', 'info');
    this.log('  blur - Apply blur effect', 'info');
    this.log('', 'info');
    this.log('Available sinks:', 'info');
    this.log('  display - Show in video panel', 'info');
    this.log('', 'info');
    this.log('Example pipelines:', 'info');
    this.log('  webcam -> grayscale -> edges -> display', 'info');
    this.log('  test-pattern -> sepia -> display', 'info');
  }
}

// Initialize the web editor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new WebEditor();
});