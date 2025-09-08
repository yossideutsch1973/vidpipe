#include "vidpipe.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>

// Performance monitoring globals
static struct timeval perf_start_time;
static PerformanceStats global_stats = {0};

void performance_start_timing() {
    gettimeofday(&perf_start_time, NULL);
}

double performance_end_timing() {
    struct timeval end_time;
    gettimeofday(&end_time, NULL);
    return (end_time.tv_sec - perf_start_time.tv_sec) + 
           (end_time.tv_usec - perf_start_time.tv_usec) / 1000000.0;
}

void performance_update_stats(PerformanceStats* stats, const char* function_name, double time) {
    stats->frame_count++;
    stats->processing_time += time;
    stats->frame_time = time;
    stats->fps = 1.0 / time;
    
    if (stats->bottleneck_function) {
        free(stats->bottleneck_function);
    }
    stats->bottleneck_function = strdup(function_name);
}

// Simple video capture simulator
Frame* capture_frame_func(Frame* input, void* params) {
    static int frame_counter = 0;
    (void)input;
    (void)params;
    
    // Simulate 30 FPS
    usleep(33333);
    
    // Create a test pattern frame (640x480 RGB)
    Frame* frame = frame_create(640, 480, 3);
    frame->timestamp = frame_counter++;
    
    // Generate a simple test pattern
    for (int y = 0; y < frame->height; y++) {
        for (int x = 0; x < frame->width; x++) {
            int idx = (y * frame->width + x) * 3;
            // Create gradient pattern
            frame->data[idx] = (uint8_t)((x * 255) / frame->width);     // R
            frame->data[idx + 1] = (uint8_t)((y * 255) / frame->height); // G
            frame->data[idx + 2] = (uint8_t)(frame_counter % 255);       // B
        }
    }
    
    return frame;
}

// Convert RGB to grayscale
// Mathematical representation: G(x,y) = 0.299*R(x,y) + 0.587*G(x,y) + 0.114*B(x,y)
// where (x,y) are pixel coordinates and R,G,B are RGB channel values
Frame* grayscale_func(Frame* input, void* params) {
    (void)params;
    if (!input || input->channels != 3) return input;
    
    Frame* output = frame_create(input->width, input->height, 1);
    output->timestamp = input->timestamp;
    
    for (int i = 0; i < input->width * input->height; i++) {
        int idx = i * 3;
        // Standard grayscale conversion: 0.299*R + 0.587*G + 0.114*B
        uint8_t gray = (uint8_t)(
            0.299 * input->data[idx] +
            0.587 * input->data[idx + 1] +
            0.114 * input->data[idx + 2]
        );
        output->data[i] = gray;
    }
    
    return output;
}

// Simple edge detection (Sobel-like)
// Mathematical representation: 
// Gx = [-1 0 1; -2 0 2; -1 0 1] * I, Gy = [-1 -2 -1; 0 0 0; 1 2 1] * I
// Magnitude = sqrt(Gx² + Gy²) where I is the input image
Frame* edges_func(Frame* input, void* params) {
    (void)params;
    if (!input || input->channels != 1) return input;
    
    Frame* output = frame_create(input->width, input->height, 1);
    output->timestamp = input->timestamp;
    
    // Simple edge detection kernel
    int gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
    
    for (int y = 1; y < input->height - 1; y++) {
        for (int x = 1; x < input->width - 1; x++) {
            int sum_x = 0, sum_y = 0;
            
            for (int ky = -1; ky <= 1; ky++) {
                for (int kx = -1; kx <= 1; kx++) {
                    int pixel = input->data[(y + ky) * input->width + (x + kx)];
                    sum_x += pixel * gx[ky + 1][kx + 1];
                    sum_y += pixel * gy[ky + 1][kx + 1];
                }
            }
            
            int magnitude = (int)sqrt(sum_x * sum_x + sum_y * sum_y);
            output->data[y * output->width + x] = (uint8_t)(magnitude > 255 ? 255 : magnitude);
        }
    }
    
    return output;
}

// Gaussian blur
// Mathematical representation: B(x,y) = Σ(i,j) K(i,j) * I(x+i, y+j)
// where K is the 3x3 Gaussian kernel and I is the input image
Frame* blur_func(Frame* input, void* params) {
    (void)params;
    if (!input) return NULL;
    
    Frame* output = frame_create(input->width, input->height, input->channels);
    output->timestamp = input->timestamp;
    
    // Simple 3x3 Gaussian kernel
    float kernel[3][3] = {
        {1/16.0, 2/16.0, 1/16.0},
        {2/16.0, 4/16.0, 2/16.0},
        {1/16.0, 2/16.0, 1/16.0}
    };
    
    for (int c = 0; c < input->channels; c++) {
        for (int y = 1; y < input->height - 1; y++) {
            for (int x = 1; x < input->width - 1; x++) {
                float sum = 0;
                
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        int idx = ((y + ky) * input->width + (x + kx)) * input->channels + c;
                        sum += input->data[idx] * kernel[ky + 1][kx + 1];
                    }
                }
                
                int out_idx = (y * output->width + x) * output->channels + c;
                output->data[out_idx] = (uint8_t)sum;
            }
        }
    }
    
    return output;
}

// Threshold function
// Mathematical representation: T(x,y) = { 255 if I(x,y) > θ, 0 otherwise }
// where I is the input image and θ is the threshold value
Frame* threshold_func(Frame* input, void* params) {
    if (!input) return NULL;
    
    int threshold = params ? *(int*)params : 128;
    Frame* output = frame_copy(input);
    
    for (int i = 0; i < output->width * output->height * output->channels; i++) {
        output->data[i] = output->data[i] > threshold ? 255 : 0;
    }
    
    return output;
}

// Invert colors
// Mathematical representation: I'(x,y) = 255 - I(x,y)
// where I is the input image and I' is the inverted output
Frame* invert_func(Frame* input, void* params) {
    (void)params;
    if (!input) return NULL;
    
    Frame* output = frame_copy(input);
    
    for (int i = 0; i < output->width * output->height * output->channels; i++) {
        output->data[i] = 255 - output->data[i];
    }
    
    return output;
}

// Simple display function (prints to console)
Frame* display_func(Frame* input, void* params) {
    (void)params;
    if (!input) return NULL;
    
    printf("\033[2J\033[H"); // Clear screen and move cursor to top
    printf("Frame %llu: %dx%d, %d channels\n", 
           (unsigned long long)input->timestamp, input->width, input->height, input->channels);
    
    // Display a small ASCII representation (downsampled)
    int step_x = input->width / 80;
    int step_y = input->height / 40;
    
    if (step_x < 1) step_x = 1;
    if (step_y < 1) step_y = 1;
    
    const char* ascii = " .:-=+*#%@";
    
    for (int y = 0; y < input->height && y < 40 * step_y; y += step_y) {
        for (int x = 0; x < input->width && x < 80 * step_x; x += step_x) {
            int idx = (y * input->width + x) * input->channels;
            int brightness;
            
            if (input->channels == 1) {
                brightness = input->data[idx];
            } else {
                brightness = (input->data[idx] + 
                            input->data[idx + 1] + 
                            input->data[idx + 2]) / 3;
            }
            
            int ascii_idx = (brightness * 9) / 255;
            printf("%c", ascii[ascii_idx]);
        }
        printf("\n");
    }
    
    fflush(stdout);
    return input; // Pass through
}

// Save frame to file
Frame* save_frame_func(Frame* input, void* params) {
    (void)params;
    if (!input) return NULL;
    
    static int save_counter = 0;
    char filename[256];
    snprintf(filename, sizeof(filename), "frame_%06d.ppm", save_counter++);
    
    FILE* file = fopen(filename, "wb");
    if (file) {
        if (input->channels == 1) {
            fprintf(file, "P5\n%d %d\n255\n", input->width, input->height);
        } else {
            fprintf(file, "P6\n%d %d\n255\n", input->width, input->height);
        }
        fwrite(input->data, 1, input->width * input->height * input->channels, file);
        fclose(file);
        printf("Saved frame to %s\n", filename);
    }
    
    return input; // Pass through
}

// Resize/scale frame
Frame* resize_func(Frame* input, void* params) {
    if (!input) return NULL;
    
    // Default to half size if no params
    int new_width = input->width / 2;
    int new_height = input->height / 2;
    
    if (params) {
        int* dimensions = (int*)params;
        new_width = dimensions[0];
        new_height = dimensions[1];
    }
    
    Frame* output = frame_create(new_width, new_height, input->channels);
    output->timestamp = input->timestamp;
    
    // Simple nearest-neighbor scaling
    float x_ratio = (float)input->width / new_width;
    float y_ratio = (float)input->height / new_height;
    
    for (int y = 0; y < new_height; y++) {
        for (int x = 0; x < new_width; x++) {
            int src_x = (int)(x * x_ratio);
            int src_y = (int)(y * y_ratio);
            
            for (int c = 0; c < input->channels; c++) {
                int src_idx = (src_y * input->width + src_x) * input->channels + c;
                int dst_idx = (y * new_width + x) * input->channels + c;
                output->data[dst_idx] = input->data[src_idx];
            }
        }
    }
    
    return output;
}

// Simulated live camera feed with movement
Frame* camera_feed_func(Frame* input, void* params) {
    static int frame_counter = 0;
    static float object_x = 100, object_y = 100;
    static float velocity_x = 2.5f, velocity_y = 1.8f;
    (void)input;
    (void)params;
    
    performance_start_timing();
    
    // Simulate 30 FPS
    usleep(33333);
    
    Frame* frame = frame_create(640, 480, 3);
    frame->timestamp = frame_counter++;
    
    // Clear frame to dark blue background
    for (int i = 0; i < frame->width * frame->height; i++) {
        int idx = i * 3;
        frame->data[idx] = 30;     // R
        frame->data[idx + 1] = 60; // G  
        frame->data[idx + 2] = 100; // B
    }
    
    // Update object position (bouncing ball simulation)
    object_x += velocity_x;
    object_y += velocity_y;
    
    if (object_x < 20 || object_x > frame->width - 20) velocity_x = -velocity_x;
    if (object_y < 20 || object_y > frame->height - 20) velocity_y = -velocity_y;
    
    // Draw moving objects (simulate face/objects for detection)
    int obj_size = 40;
    for (int dy = -obj_size/2; dy < obj_size/2; dy++) {
        for (int dx = -obj_size/2; dx < obj_size/2; dx++) {
            int x = (int)object_x + dx;
            int y = (int)object_y + dy;
            if (x >= 0 && x < frame->width && y >= 0 && y < frame->height) {
                int idx = (y * frame->width + x) * 3;
                // Bright circular object
                float dist = sqrt(dx*dx + dy*dy);
                if (dist < obj_size/2) {
                    float intensity = 1.0f - (dist / (obj_size/2));
                    frame->data[idx] = (uint8_t)(255 * intensity);
                    frame->data[idx + 1] = (uint8_t)(200 * intensity);
                    frame->data[idx + 2] = (uint8_t)(100 * intensity);
                }
            }
        }
    }
    
    // Add some noise and texture
    for (int i = 0; i < 1000; i++) {
        int x = rand() % frame->width;
        int y = rand() % frame->height;
        int idx = (y * frame->width + x) * 3;
        uint8_t noise = rand() % 50;
        frame->data[idx] = (uint8_t)fmin(255, frame->data[idx] + noise);
        frame->data[idx + 1] = (uint8_t)fmin(255, frame->data[idx + 1] + noise);
        frame->data[idx + 2] = (uint8_t)fmin(255, frame->data[idx + 2] + noise);
    }
    
    double time = performance_end_timing();
    performance_update_stats(&global_stats, "camera", time);
    
    return frame;
}

// Harris corner detection
Frame* corner_detect_func(Frame* input, void* params) {
    (void)params; // Suppress unused parameter warning
    if (!input || input->channels != 1) return input;
    
    performance_start_timing();
    
    Frame* output = frame_create(input->width, input->height, 3);
    output->timestamp = input->timestamp;
    
    // Copy grayscale to all channels first
    for (int i = 0; i < input->width * input->height; i++) {
        uint8_t gray = input->data[i];
        output->data[i * 3] = gray;
        output->data[i * 3 + 1] = gray;
        output->data[i * 3 + 2] = gray;
    }
    
    // Simplified Harris corner detector
    int window_size = 3;
    float k = 0.04f;
    float threshold = 10000.0f;
    
    for (int y = window_size; y < input->height - window_size; y++) {
        for (int x = window_size; x < input->width - window_size; x++) {
            float Ixx = 0, Iyy = 0, Ixy = 0;
            
            // Compute gradients and second moments
            for (int wy = -window_size/2; wy <= window_size/2; wy++) {
                for (int wx = -window_size/2; wx <= window_size/2; wx++) {
                    int px = x + wx;
                    int py = y + wy;
                    
                    // Compute gradients
                    float Ix = (px < input->width-1) ? 
                        input->data[py * input->width + px + 1] - input->data[py * input->width + px - 1] : 0;
                    float Iy = (py < input->height-1) ? 
                        input->data[(py + 1) * input->width + px] - input->data[(py - 1) * input->width + px] : 0;
                    
                    Ixx += Ix * Ix;
                    Iyy += Iy * Iy;
                    Ixy += Ix * Iy;
                }
            }
            
            // Harris response
            float det = Ixx * Iyy - Ixy * Ixy;
            float trace = Ixx + Iyy;
            float response = det - k * trace * trace;
            
            // Mark corners in red
            if (response > threshold) {
                for (int dy = -2; dy <= 2; dy++) {
                    for (int dx = -2; dx <= 2; dx++) {
                        int px = x + dx;
                        int py = y + dy;
                        if (px >= 0 && px < output->width && py >= 0 && py < output->height) {
                            int idx = (py * output->width + px) * 3;
                            output->data[idx] = 255;     // Red
                            output->data[idx + 1] = 0;
                            output->data[idx + 2] = 0;
                        }
                    }
                }
            }
        }
    }
    
    double time = performance_end_timing();
    performance_update_stats(&global_stats, "corner_detect", time);
    
    return output;
}

// Optical flow using Lucas-Kanade method (simplified)
Frame* optical_flow_func(Frame* input, void* params) {
    (void)params; // Suppress unused parameter warning
    static Frame* prev_frame = NULL;
    static TrackedPoint* flow_points = NULL;
    static int flow_count = 0;
    
    if (!input || input->channels != 1) return input;
    
    performance_start_timing();
    
    Frame* output = frame_create(input->width, input->height, 3);
    output->timestamp = input->timestamp;
    
    // Convert grayscale to RGB
    for (int i = 0; i < input->width * input->height; i++) {
        uint8_t gray = input->data[i];
        output->data[i * 3] = gray;
        output->data[i * 3 + 1] = gray;
        output->data[i * 3 + 2] = gray;
    }
    
    if (prev_frame) {
        // Initialize flow points if needed
        if (flow_points == NULL) {
            flow_points = malloc(sizeof(TrackedPoint) * 100);
            flow_count = 0;
            
            // Find good features to track (simplified)
            for (int y = 20; y < input->height - 20; y += 30) {
                for (int x = 20; x < input->width - 20; x += 30) {
                    if (flow_count < 100) {
                        flow_points[flow_count].x = x;
                        flow_points[flow_count].y = y;
                        flow_points[flow_count].vx = 0;
                        flow_points[flow_count].vy = 0;
                        flow_points[flow_count].age = 0;
                        flow_points[flow_count].id = flow_count;
                        flow_count++;
                    }
                }
            }
        }
        
        // Track points using Lucas-Kanade (simplified)
        for (int i = 0; i < flow_count; i++) {
            TrackedPoint* pt = &flow_points[i];
            int x = (int)pt->x;
            int y = (int)pt->y;
            
            if (x >= 10 && x < input->width - 10 && y >= 10 && y < input->height - 10) {
                // Compute optical flow (simplified gradient method)
                float sum_Ix2 = 0, sum_Iy2 = 0, sum_IxIy = 0;
                float sum_IxIt = 0, sum_IyIt = 0;
                
                for (int dy = -2; dy <= 2; dy++) {
                    for (int dx = -2; dx <= 2; dx++) {
                        int px = x + dx;
                        int py = y + dy;
                        
                        float Ix = (px < input->width-1) ? 
                            (input->data[py * input->width + px + 1] - input->data[py * input->width + px - 1]) / 2.0f : 0;
                        float Iy = (py < input->height-1) ? 
                            (input->data[(py + 1) * input->width + px] - input->data[(py - 1) * input->width + px]) / 2.0f : 0;
                        float It = input->data[py * input->width + px] - prev_frame->data[py * prev_frame->width + px];
                        
                        sum_Ix2 += Ix * Ix;
                        sum_Iy2 += Iy * Iy;
                        sum_IxIy += Ix * Iy;
                        sum_IxIt += Ix * It;
                        sum_IyIt += Iy * It;
                    }
                }
                
                // Solve for optical flow
                float det = sum_Ix2 * sum_Iy2 - sum_IxIy * sum_IxIy;
                if (fabs(det) > 0.01f) {
                    float vx = (sum_IyIt * sum_IxIy - sum_IxIt * sum_Iy2) / det;
                    float vy = (sum_IxIt * sum_IxIy - sum_IyIt * sum_Ix2) / det;
                    
                    // Update point position and velocity
                    pt->vx = vx * 0.3f + pt->vx * 0.7f; // Smooth velocity
                    pt->vy = vy * 0.3f + pt->vy * 0.7f;
                    pt->x += pt->vx;
                    pt->y += pt->vy;
                    pt->age++;
                    
                    // Draw flow vector
                    int end_x = (int)(pt->x + pt->vx * 10);
                    int end_y = (int)(pt->y + pt->vy * 10);
                    
                    // Draw line (simple Bresenham-like)
                    int dx = abs(end_x - x);
                    int dy = abs(end_y - y);
                    int steps = (dx > dy) ? dx : dy;
                    
                    if (steps > 0) {
                        for (int step = 0; step <= steps; step++) {
                            int lx = x + (end_x - x) * step / steps;
                            int ly = y + (end_y - y) * step / steps;
                            
                            if (lx >= 0 && lx < output->width && ly >= 0 && ly < output->height) {
                                int idx = (ly * output->width + lx) * 3;
                                output->data[idx] = 255;     // Red flow vectors
                                output->data[idx + 1] = 255; // Yellow
                                output->data[idx + 2] = 0;
                            }
                        }
                    }
                    
                    // Draw point
                    if (x >= 0 && x < output->width && y >= 0 && y < output->height) {
                        int idx = (y * output->width + x) * 3;
                        output->data[idx] = 0;
                        output->data[idx + 1] = 255;     // Green points
                        output->data[idx + 2] = 0;
                    }
                }
            }
            
            // Reset points that go out of bounds
            if (pt->x < 0 || pt->x >= input->width || pt->y < 0 || pt->y >= input->height) {
                pt->x = rand() % (input->width - 40) + 20;
                pt->y = rand() % (input->height - 40) + 20;
                pt->vx = pt->vy = 0;
                pt->age = 0;
            }
        }
    }
    
    // Store current frame for next iteration
    if (prev_frame) frame_destroy(prev_frame);
    prev_frame = frame_copy(input);
    
    double time = performance_end_timing();
    performance_update_stats(&global_stats, "optical_flow", time);
    
    return output;
}

// Background subtraction for motion detection
Frame* background_subtract_func(Frame* input, void* params) {
    static Frame* background_model = NULL;
    (void)params;
    
    if (!input) return NULL;
    
    performance_start_timing();
    
    Frame* output = frame_create(input->width, input->height, input->channels);
    output->timestamp = input->timestamp;
    
    // Initialize background model
    if (background_model == NULL) {
        background_model = frame_copy(input);
        memcpy(output->data, input->data, input->width * input->height * input->channels);
        return output;
    }
    
    // Update background model slowly
    float alpha = 0.01f;
    for (int i = 0; i < input->width * input->height * input->channels; i++) {
        background_model->data[i] = (uint8_t)(alpha * input->data[i] + (1 - alpha) * background_model->data[i]);
    }
    
    // Compute foreground mask
    int threshold = 30;
    for (int i = 0; i < input->width * input->height; i++) {
        int diff = 0;
        for (int c = 0; c < input->channels; c++) {
            int idx = i * input->channels + c;
            int pixel_diff = abs(input->data[idx] - background_model->data[idx]);
            diff += pixel_diff;
        }
        diff /= input->channels;
        
        // Binary mask
        uint8_t mask = (diff > threshold) ? 255 : 0;
        
        if (input->channels == 3) {
            output->data[i * 3] = mask;
            output->data[i * 3 + 1] = mask;
            output->data[i * 3 + 2] = mask;
        } else {
            output->data[i] = mask;
        }
    }
    
    double time = performance_end_timing();
    performance_update_stats(&global_stats, "background_subtract", time);
    
    return output;
}

// Performance monitoring display
Frame* performance_display_func(Frame* input, void* params) {
    (void)params;
    if (!input) return NULL;
    
    // Save frame as PPM file every 10 frames
    static int frame_counter = 0;
    frame_counter++;
    
    if (frame_counter % 10 == 0) {
        char filename[100];
        snprintf(filename, sizeof(filename), "frame_%d.ppm", frame_counter);
        
        FILE* file = fopen(filename, "wb");
        if (file) {
            fprintf(file, "P6\n%d %d\n255\n", input->width, input->height);
            if (input->channels == 3) {
                fwrite(input->data, 1, input->width * input->height * 3, file);
            } else {
                // Convert grayscale to RGB
                for (int i = 0; i < input->width * input->height; i++) {
                    uint8_t val = input->data[i];
                    fwrite(&val, 1, 1, file);
                    fwrite(&val, 1, 1, file);
                    fwrite(&val, 1, 1, file);
                }
            }
            fclose(file);
        }
    }
    
    printf("VidPipe Performance Monitor\n");
    printf("===========================\n");
    printf("Frame: %llu\n", (unsigned long long)input->timestamp);
    printf("Resolution: %dx%d (%d channels)\n", input->width, input->height, input->channels);
    printf("FPS: %.2f\n", global_stats.fps);
    printf("Frame Time: %.3f ms\n", global_stats.frame_time * 1000);
    printf("Total Frames: %d\n", global_stats.frame_count);
    printf("Avg Processing Time: %.3f ms\n", 
           (global_stats.processing_time / global_stats.frame_count) * 1000);
    printf("Last Bottleneck: %s\n", global_stats.bottleneck_function ? global_stats.bottleneck_function : "none");
    printf("\n");
    
    // Display a downsampled version of the frame
    int step_x = input->width / 60;
    int step_y = input->height / 30;
    if (step_x < 1) step_x = 1;
    if (step_y < 1) step_y = 1;
    
    const char* ascii = " .:-=+*#%@";
    
    for (int y = 0; y < input->height && y < 30 * step_y; y += step_y) {
        for (int x = 0; x < input->width && x < 60 * step_x; x += step_x) {
            int idx = (y * input->width + x) * input->channels;
            int brightness;
            
            if (input->channels == 1) {
                brightness = input->data[idx];
            } else {
                brightness = (input->data[idx] + 
                            input->data[idx + 1] + 
                            input->data[idx + 2]) / 3;
            }
            
            int ascii_idx = (brightness * 9) / 255;
            printf("%c", ascii[ascii_idx]);
        }
        printf("\n");
    }
    
    fflush(stdout);
    return input; // Pass through
}

// External camera functions
Frame* webcam_capture_func(Frame* input, void* params);
Frame* window_display_func(Frame* input, void* params);
Frame* sdl_window_display_func(Frame* input, void* params);
Frame* http_display_func(Frame* input, void* params);

// Register all built-in functions
void register_builtin_functions(FunctionRegistry* registry) {
    // Sources
    registry_add(registry, "capture-frame", capture_frame_func, NULL, true, false);
    registry_add(registry, "capture", capture_frame_func, NULL, true, false);
    registry_add(registry, "camera", camera_feed_func, NULL, true, false);
    registry_add(registry, "live", camera_feed_func, NULL, true, false);
    registry_add(registry, "webcam", webcam_capture_func, NULL, true, false);
    registry_add(registry, "cam", webcam_capture_func, NULL, true, false);
    
    // Basic processing functions
    registry_add(registry, "grayscale", grayscale_func, NULL, false, false);
    registry_add(registry, "gray", grayscale_func, NULL, false, false);
    registry_add(registry, "edges", edges_func, NULL, false, false);
    registry_add(registry, "blur", blur_func, NULL, false, false);
    registry_add(registry, "threshold", threshold_func, NULL, false, false);
    registry_add(registry, "invert", invert_func, NULL, false, false);
    registry_add(registry, "resize", resize_func, NULL, false, false);
    
    // Advanced CV functions
    registry_add(registry, "corners", corner_detect_func, NULL, false, false);
    registry_add(registry, "harris", corner_detect_func, NULL, false, false);
    registry_add(registry, "optical-flow", optical_flow_func, NULL, false, false);
    registry_add(registry, "flow", optical_flow_func, NULL, false, false);
    registry_add(registry, "motion", background_subtract_func, NULL, false, false);
    registry_add(registry, "background-subtract", background_subtract_func, NULL, false, false);
    
    // Sinks
    registry_add(registry, "display", display_func, NULL, false, true);
    registry_add(registry, "show", display_func, NULL, false, true);
    registry_add(registry, "window", window_display_func, NULL, false, true);
    registry_add(registry, "win", window_display_func, NULL, false, true);
    registry_add(registry, "http-display", http_display_func, NULL, false, true);
    registry_add(registry, "http", http_display_func, NULL, false, true);
    registry_add(registry, "web", http_display_func, NULL, false, true);
    registry_add(registry, "sdl-window", sdl_window_display_func, NULL, false, true);
    registry_add(registry, "sdl", sdl_window_display_func, NULL, false, true);
    registry_add(registry, "gui", sdl_window_display_func, NULL, false, true);
    registry_add(registry, "save", save_frame_func, NULL, false, true);
    registry_add(registry, "perf", performance_display_func, NULL, false, true);
    registry_add(registry, "performance", performance_display_func, NULL, false, true);
}