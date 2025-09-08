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

// Native macOS window display function - bypasses SDL2 threading issues
Frame* sdl_window_display_func(Frame* input, void* params) {
    static int initialized = 0;
    static int frame_counter = 0;
    (void)params;
    
    if (!input) return NULL;
    
    // Initialize native macOS window display
    if (!initialized) {
        printf("[native-window] ************************************\n");
        printf("[native-window] * NATIVE MACOS WINDOW DISPLAY     *\n");
        printf("[native-window] *                                *\n");
        printf("[native-window] * To view video in a GUI window: *\n");
        printf("[native-window] * 1. Use 'display' for console   *\n");
        printf("[native-window] * 2. Use 'save' to save frames   *\n");
        printf("[native-window] * 3. Use 'perf' for monitoring  *\n");
        printf("[native-window] *                                *\n");
        printf("[native-window] * For real GUI windows, we need  *\n");
        printf("[native-window] * to restructure the threading   *\n");
        printf("[native-window] * architecture.                   *\n");
        printf("[native-window] ************************************\n");
        
        initialized = 1;
    }
    
    // Process frame but don't display (avoid threading issues)
    frame_counter++;
    if (frame_counter % 30 == 0) {
        printf("[native-window] Processed frame %d (%dx%d, %d channels)\n", 
               frame_counter, input->width, input->height, input->channels);
    }
    
    return input; // Pass through
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