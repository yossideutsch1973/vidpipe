#include "vidpipe.h"
#import <AVFoundation/AVFoundation.h>
#import <CoreMedia/CoreMedia.h>
#import <CoreVideo/CoreVideo.h>
#import <Foundation/Foundation.h>

static AVCaptureSession *captureSession = nil;
static AVCaptureDevice *camera = nil;
static AVCaptureVideoDataOutput *videoOutput = nil;
static dispatch_queue_t videoQueue = nil;
static CVPixelBufferRef latestPixelBuffer = NULL;
static dispatch_semaphore_t frameSemaphore;

// Delegate for handling camera frames
@interface CameraDelegate : NSObject <AVCaptureVideoDataOutputSampleBufferDelegate>
@end

@implementation CameraDelegate
- (void)captureOutput:(AVCaptureOutput *)output
    didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer
           fromConnection:(AVCaptureConnection *)connection {
    
    CVPixelBufferRef pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer);
    if (pixelBuffer) {
        // Replace the latest frame
        if (latestPixelBuffer) {
            CVPixelBufferRelease(latestPixelBuffer);
        }
        latestPixelBuffer = CVPixelBufferRetain(pixelBuffer);
        dispatch_semaphore_signal(frameSemaphore);
    }
}
@end

static CameraDelegate *delegate = nil;

int init_camera() {
    @autoreleasepool {
        // Create semaphore for frame synchronization
        frameSemaphore = dispatch_semaphore_create(0);
        
        // Create capture session
        captureSession = [[AVCaptureSession alloc] init];
        [captureSession setSessionPreset:AVCaptureSessionPreset640x480];
        
        // Find camera device
        camera = [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
        if (!camera) {
            NSLog(@"No camera found");
            return -1;
        }
        
        NSError *error = nil;
        AVCaptureDeviceInput *input = [AVCaptureDeviceInput deviceInputWithDevice:camera error:&error];
        if (error) {
            NSLog(@"Error creating camera input: %@", error.localizedDescription);
            return -1;
        }
        
        if ([captureSession canAddInput:input]) {
            [captureSession addInput:input];
        } else {
            NSLog(@"Cannot add camera input");
            return -1;
        }
        
        // Create video output
        videoOutput = [[AVCaptureVideoDataOutput alloc] init];
        
        // Set pixel format to 32BGRA for easier processing
        NSDictionary *settings = @{
            (NSString*)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_32BGRA)
        };
        [videoOutput setVideoSettings:settings];
        
        // Create delegate and queue
        delegate = [[CameraDelegate alloc] init];
        videoQueue = dispatch_queue_create("VideoQueue", DISPATCH_QUEUE_SERIAL);
        [videoOutput setSampleBufferDelegate:delegate queue:videoQueue];
        
        if ([captureSession canAddOutput:videoOutput]) {
            [captureSession addOutput:videoOutput];
        } else {
            NSLog(@"Cannot add video output");
            return -1;
        }
        
        // Start capture
        [captureSession startRunning];
        
        NSLog(@"Camera initialized successfully");
        return 0;
    }
}

void cleanup_camera() {
    @autoreleasepool {
        if (captureSession) {
            [captureSession stopRunning];
            captureSession = nil;
        }
        
        if (latestPixelBuffer) {
            CVPixelBufferRelease(latestPixelBuffer);
            latestPixelBuffer = NULL;
        }
        
        if (frameSemaphore) {
            // Don't release semaphore while potentially in use
            frameSemaphore = NULL;
        }
        
        camera = nil;
        videoOutput = nil;
        delegate = nil;
        videoQueue = nil;
    }
}

Frame* capture_camera_frame() {
    static int initialized = 0;
    
    if (!initialized) {
        if (init_camera() != 0) {
            printf("Failed to initialize camera\n");
            return NULL;
        }
        initialized = 1;
    }
    
    // Wait for a frame with timeout
    dispatch_time_t timeout = dispatch_time(DISPATCH_TIME_NOW, 100 * NSEC_PER_MSEC);
    if (dispatch_semaphore_wait(frameSemaphore, timeout) != 0) {
        // Timeout - return NULL or previous frame
        return NULL;
    }
    
    if (!latestPixelBuffer) {
        return NULL;
    }
    
    @autoreleasepool {
        CVPixelBufferLockBaseAddress(latestPixelBuffer, kCVPixelBufferLock_ReadOnly);
        
        size_t width = CVPixelBufferGetWidth(latestPixelBuffer);
        size_t height = CVPixelBufferGetHeight(latestPixelBuffer);
        
        Frame* frame = frame_create((int)width, (int)height, 3);
        frame->timestamp = (uint64_t)time(NULL);
        
        uint8_t* baseAddress = (uint8_t*)CVPixelBufferGetBaseAddress(latestPixelBuffer);
        size_t bytesPerRow = CVPixelBufferGetBytesPerRow(latestPixelBuffer);
        
        // Convert BGRA to RGB
        for (size_t y = 0; y < height; y++) {
            for (size_t x = 0; x < width; x++) {
                size_t srcIdx = y * bytesPerRow + x * 4; // BGRA = 4 bytes per pixel
                size_t dstIdx = (y * width + x) * 3;     // RGB = 3 bytes per pixel
                
                // BGRA -> RGB
                frame->data[dstIdx] = baseAddress[srcIdx + 2];     // R
                frame->data[dstIdx + 1] = baseAddress[srcIdx + 1]; // G  
                frame->data[dstIdx + 2] = baseAddress[srcIdx];     // B
                // Skip A (alpha)
            }
        }
        
        CVPixelBufferUnlockBaseAddress(latestPixelBuffer, kCVPixelBufferLock_ReadOnly);
        
        return frame;
    }
}