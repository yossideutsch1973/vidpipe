#ifdef USE_OPENCV
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/videoio.hpp>
using namespace cv;
#endif

#ifdef USE_SDL2
#include <SDL2/SDL.h>
#endif

extern "C" {
#include "vidpipe.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
}

extern "C" {

// Camera capture function - captures from webcam if available
Frame* webcam_capture_func(Frame* input, void* params) {
#ifdef USE_OPENCV
    static VideoCapture* cap = nullptr;
    static int frame_counter = 0;
    static int initialized = 0;
    (void)input;
    (void)params;
    
    // Initialize camera on first call
    if (!initialized) {
        cap = new VideoCapture(0); // Default camera
        if (!cap->isOpened()) {
            printf("[webcam] Error: Cannot open camera\n");
            delete cap;
            cap = nullptr;
            return NULL;
        }
        
        // Set camera properties
        cap->set(CAP_PROP_FRAME_WIDTH, 640);
        cap->set(CAP_PROP_FRAME_HEIGHT, 480);
        cap->set(CAP_PROP_FPS, 30);
        
        printf("[webcam] Camera initialized successfully\n");
        initialized = 1;
    }
    
    if (!cap || !cap->isOpened()) {
        return NULL;
    }
    
    // Capture frame
    Mat opencv_frame;
    if (!cap->read(opencv_frame) || opencv_frame.empty()) {
        printf("[webcam] Failed to capture frame\n");
        return NULL;
    }
    
    // Convert BGR to RGB and create VidPipe frame
    Mat rgb_frame;
    cvtColor(opencv_frame, rgb_frame, COLOR_BGR2RGB);
    
    Frame* frame = frame_create(rgb_frame.cols, rgb_frame.rows, 3);
    frame->timestamp = frame_counter++;
    
    // Copy pixel data
    memcpy(frame->data, rgb_frame.data, rgb_frame.cols * rgb_frame.rows * 3);
    
    if (frame_counter % 30 == 0) {
        printf("[webcam] Frame %d captured (%dx%d)\n", frame_counter, frame->width, frame->height);
    }
    
    return frame;
#else
    // Fallback: simulate camera with test pattern
    static int frame_counter = 0;
    (void)input;
    (void)params;
    
    usleep(33333); // 30 FPS
    
    Frame* frame = frame_create(640, 480, 3);
    frame->timestamp = frame_counter++;
    
    // Generate a test pattern
    for (int y = 0; y < frame->height; y++) {
        for (int x = 0; x < frame->width; x++) {
            int idx = (y * frame->width + x) * 3;
            frame->data[idx] = (uint8_t)((x * 255) / frame->width);     // R
            frame->data[idx + 1] = (uint8_t)((y * 255) / frame->height); // G
            frame->data[idx + 2] = (uint8_t)(frame_counter % 255);       // B
        }
    }
    
    if (frame_counter % 30 == 0) {
        printf("[webcam] Simulated frame %d captured\n", frame_counter);
    }
    
    return frame;
#endif
}

// Window display function - simple console display (thread-safe, no file I/O)
Frame* window_display_func(Frame* input, void* params) {
    static int frame_counter = 0;
    (void)params;
    
    if (!input) return NULL;
    
    // Simple frame counter display - no heavy operations
    frame_counter++;
    
    // Display basic info every 30 frames (1 second at 30fps)
    if (frame_counter % 30 == 0) {
        printf("\r[window] Live frame %d (%dx%d, %d channels) - FPS: ~30", 
               frame_counter, input->width, input->height, input->channels);
        fflush(stdout);
    }
    
    return input;
}

// SDL2 window display function - real-time GUI window (with macOS workaround)
Frame* sdl_window_display_func(Frame* input, void* params) {
#ifdef USE_SDL2
    static SDL_Window* window = NULL;
    static SDL_Renderer* renderer = NULL;
    static SDL_Texture* texture = NULL;
    static int initialized = 0;
    static int init_attempted = 0;
    static int frame_counter = 0;
    static int last_width = 0, last_height = 0;
    (void)params;
    
    if (!input) return NULL;
    
    // Try SDL initialization once (may fail on macOS worker threads)
    if (!initialized && !init_attempted) {
        init_attempted = 1;
        
        // Set SDL to allow initialization from any thread (macOS workaround)
        SDL_SetHint(SDL_HINT_MAC_CTRL_CLICK_EMULATE_RIGHT_CLICK, "1");
        SDL_SetHint(SDL_HINT_VIDEO_MAC_FULLSCREEN_SPACES, "1");
        
        if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_NOPARACHUTE) < 0) {
            printf("[sdl-window] SDL initialization failed (expected on macOS): %s\n", SDL_GetError());
            printf("[sdl-window] Falling back to console display. Use 'http' for GUI viewing.\n");
            return input;
        }
        
        // Create window
        window = SDL_CreateWindow(
            "VidPipe Live - Real-time Video Processing",
            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
            input->width, input->height,
            SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE
        );
        
        if (!window) {
            printf("[sdl-window] Window creation failed: %s\n", SDL_GetError());
            SDL_Quit();
            return input;
        }
        
        // Create renderer with hardware acceleration
        renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
        if (!renderer) {
            printf("[sdl-window] Renderer creation failed: %s\n", SDL_GetError());
            SDL_DestroyWindow(window);
            SDL_Quit();
            return input;
        }
        
        last_width = input->width;
        last_height = input->height;
        initialized = 1;
        printf("[sdl-window] SDL window initialized (%dx%d)\n", input->width, input->height);
    }
    
    // Handle window events (ESC to close, etc.)
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT || 
           (event.type == SDL_KEYDOWN && event.key.keysym.sym == SDLK_ESCAPE)) {
            printf("[sdl-window] Window close requested\n");
            // Note: In a real implementation, we'd signal the pipeline to stop
        }
    }
    
    // Recreate texture if frame size changed
    if (input->width != last_width || input->height != last_height) {
        if (texture) SDL_DestroyTexture(texture);
        texture = NULL;
        last_width = input->width;
        last_height = input->height;
    }
    
    // Create texture for this frame size
    if (!texture) {
        texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB24, 
                                   SDL_TEXTUREACCESS_STREAMING, 
                                   input->width, input->height);
        
        if (!texture) {
            printf("[sdl-window] Texture creation failed: %s\n", SDL_GetError());
            return input;
        }
    }
    
    // Prepare pixel data for SDL
    void* pixels;
    int pitch;
    if (SDL_LockTexture(texture, NULL, &pixels, &pitch) < 0) {
        printf("[sdl-window] Texture lock failed: %s\n", SDL_GetError());
        return input;
    }
    
    // Copy frame data to texture
    if (input->channels == 3) {
        // RGB data - direct copy
        for (int y = 0; y < input->height; y++) {
            memcpy((uint8_t*)pixels + y * pitch, 
                   input->data + y * input->width * 3, 
                   input->width * 3);
        }
    } else if (input->channels == 1) {
        // Grayscale - convert to RGB
        for (int y = 0; y < input->height; y++) {
            uint8_t* dst_row = (uint8_t*)pixels + y * pitch;
            uint8_t* src_row = input->data + y * input->width;
            for (int x = 0; x < input->width; x++) {
                uint8_t gray = src_row[x];
                dst_row[x * 3 + 0] = gray; // R
                dst_row[x * 3 + 1] = gray; // G
                dst_row[x * 3 + 2] = gray; // B
            }
        }
    }
    
    SDL_UnlockTexture(texture);
    
    // Render to screen
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255); // Black background
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, texture, NULL, NULL);
    SDL_RenderPresent(renderer);
    
    frame_counter++;
    if (frame_counter % 120 == 0) {
        printf("[sdl-window] Displayed %d frames\n", frame_counter);
    }
    
    return input; // Pass through
#else
    // SDL2 not available - fall back to console  
    return window_display_func(input, params);
#endif
}

// HTTP server-based display - serves frames via localhost HTTP server
Frame* http_display_func(Frame* input, void* params) {
    static bool server_started = false;
    static char server_filename[256];
    static int frame_counter = 0;
    (void)params;
    
    if (!input) return NULL;
    
    // Initialize HTTP display on first frame
    if (!server_started) {
        snprintf(server_filename, sizeof(server_filename), "/tmp/vidpipe_stream_%d.jpg", getpid());
        
        // Create an auto-refreshing HTML viewer page
        char html_filename[256];
        snprintf(html_filename, sizeof(html_filename), "/tmp/vidpipe_viewer_%d.html", getpid());
        FILE* html = fopen(html_filename, "w");
        if (html) {
            fprintf(html, "<!DOCTYPE html>\n<html>\n<head>\n");
            fprintf(html, "<title>VidPipe Live Stream</title>\n");
            fprintf(html, "<style>\n");
            fprintf(html, "body { margin: 0; padding: 20px; background: #000; color: #fff; font-family: Arial; }\n");
            fprintf(html, "h1 { text-align: center; }\n");
            fprintf(html, "#video { display: block; margin: 0 auto; border: 2px solid #333; }\n");
            fprintf(html, "#stats { text-align: center; margin-top: 10px; }\n");
            fprintf(html, "</style>\n</head>\n<body>\n");
            fprintf(html, "<h1>VidPipe Live Camera Stream</h1>\n");
            fprintf(html, "<img id='video' src='vidpipe_stream_%d.jpg' width='640' height='480'>\n", getpid());
            fprintf(html, "<div id='stats'>FPS: <span id='fps'>0</span> | Frames: <span id='frames'>0</span></div>\n");
            fprintf(html, "<script>\n");
            fprintf(html, "let frameCount = 0;\n");
            fprintf(html, "let lastTime = Date.now();\n");
            fprintf(html, "let fps = 0;\n");
            fprintf(html, "const img = document.getElementById('video');\n");
            fprintf(html, "const fpsElement = document.getElementById('fps');\n");
            fprintf(html, "const framesElement = document.getElementById('frames');\n");
            fprintf(html, "function refreshImage() {\n");
            fprintf(html, "  img.src = 'vidpipe_stream_%d.jpg?t=' + Date.now();\n", getpid());
            fprintf(html, "  frameCount++;\n");
            fprintf(html, "  framesElement.textContent = frameCount;\n");
            fprintf(html, "  const now = Date.now();\n");
            fprintf(html, "  if (now - lastTime >= 1000) {\n");
            fprintf(html, "    fps = Math.round(frameCount * 1000 / (now - lastTime));\n");
            fprintf(html, "    fpsElement.textContent = fps;\n");
            fprintf(html, "    frameCount = 0;\n");
            fprintf(html, "    lastTime = now;\n");
            fprintf(html, "  }\n");
            fprintf(html, "}\n");
            fprintf(html, "setInterval(refreshImage, 33); // 30 FPS\n");
            fprintf(html, "</script>\n</body>\n</html>\n");
            fclose(html);
        }
        
        // Start a simple HTTP server in the background
        char command[512];
        snprintf(command, sizeof(command), 
                "python3 -c \"import http.server, socketserver, threading, os;\n"
                "os.chdir('/tmp');\n"
                "httpd = socketserver.TCPServer(('', 8080), http.server.SimpleHTTPRequestHandler);\n"
                "thread = threading.Thread(target=httpd.serve_forever);\n"
                "thread.daemon = True;\n"
                "thread.start();\n"
                "print('[HTTP Display] Server started at http://localhost:8080/');\n"
                "while True: pass\" &");
        system(command);
        
        printf("[HTTP Display] Starting server at http://localhost:8080/\n");
        printf("[HTTP Display] ************************************\n");
        printf("[HTTP Display] * REAL-TIME VIDEO STREAM READY!   *\n");
        printf("[HTTP Display] * Open your browser to:           *\n");
        printf("[HTTP Display] * http://localhost:8080/vidpipe_viewer_%d.html\n", getpid());
        printf("[HTTP Display] ************************************\n");
        server_started = true;
        
        // Give server time to start
        usleep(500000); // 0.5 seconds
    }
    
    // Convert and save frame as JPEG (only when needed for HTTP serving)
#ifdef USE_OPENCV
    Mat display_frame;
    if (input->channels == 3) {
        Mat rgb_frame(input->height, input->width, CV_8UC3, input->data);
        cvtColor(rgb_frame, display_frame, COLOR_RGB2BGR);
    } else {
        display_frame = Mat(input->height, input->width, CV_8UC1, input->data);
    }
    
    // Use JPEG compression with high quality but fast encoding
    std::vector<int> compression_params;
    compression_params.push_back(IMWRITE_JPEG_QUALITY);
    compression_params.push_back(85); // Good quality, fast compression
    
    imwrite(server_filename, display_frame, compression_params);
#else
    // Fallback: write as PPM (simpler, no compression)
    FILE* file = fopen(server_filename, "wb");
    if (file) {
        if (input->channels == 1) {
            fprintf(file, "P5\n%d %d\n255\n", input->width, input->height);
            fwrite(input->data, 1, input->width * input->height, file);
        } else {
            fprintf(file, "P6\n%d %d\n255\n", input->width, input->height);
            fwrite(input->data, 1, input->width * input->height * 3, file);
        }
        fclose(file);
    }
#endif
    
    frame_counter++;
    if (frame_counter % 60 == 0) {  // Log every 2 seconds at 30fps
        printf("[HTTP Display] Served %d frames via HTTP\n", frame_counter);
    }
    
    return input;
}


} // extern "C"