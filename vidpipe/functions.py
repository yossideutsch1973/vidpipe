"""
Built-in video processing functions for VidPipe
"""

import cv2
import numpy as np
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from .pipeline import Frame, FrameFormat
import time
import threading
from queue import Queue


@dataclass
class FunctionDef:
    """Definition of a video processing function"""
    name: str
    function: Callable
    is_source: bool = False
    is_sink: bool = False
    description: str = ""


class FunctionRegistry:
    """Registry for video processing functions"""
    
    def __init__(self):
        self.functions: Dict[str, FunctionDef] = {}
        self.register_builtin_functions()
    
    def register(self, name: str, function: Callable, is_source: bool = False, 
                is_sink: bool = False, description: str = ""):
        """Register a function"""
        self.functions[name] = FunctionDef(
            name=name,
            function=function,
            is_source=is_source,
            is_sink=is_sink,
            description=description
        )
    
    def get_function(self, name: str) -> Optional[FunctionDef]:
        """Get a function by name"""
        return self.functions.get(name)
    
    def list_functions(self) -> Dict[str, FunctionDef]:
        """List all registered functions"""
        return self.functions.copy()
    
    def register_builtin_functions(self):
        """Register built-in video processing functions"""
        
        # Source functions
        self.register("webcam", webcam_source, is_source=True, 
                     description="Capture frames from webcam")
        self.register("camera", camera_source, is_source=True,
                     description="Capture frames from camera")
        self.register("capture", capture_source, is_source=True,
                     description="Capture frames from video file")
        self.register("test-pattern", test_pattern_source, is_source=True,
                     description="Generate test pattern frames")
        
        # Processing functions
        self.register("grayscale", grayscale_filter,
                     description="Convert to grayscale")
        self.register("gray", grayscale_filter,
                     description="Convert to grayscale (alias)")
        self.register("blur", blur_filter,
                     description="Apply Gaussian blur")
        self.register("edges", edge_filter,
                     description="Detect edges using Canny")
        self.register("threshold", threshold_filter,
                     description="Apply binary threshold")
        self.register("resize", resize_filter,
                     description="Resize frame")
        self.register("flip", flip_filter,
                     description="Flip frame horizontally or vertically")
        self.register("rotate", rotate_filter,
                     description="Rotate frame")
        self.register("crop", crop_filter,
                     description="Crop frame to specified region")
        self.register("brightness", brightness_filter,
                     description="Adjust brightness")
        self.register("contrast", contrast_filter,
                     description="Adjust contrast")
        self.register("hue", hue_filter,
                     description="Adjust hue")
        self.register("saturation", saturation_filter,
                     description="Adjust saturation")
        self.register("gamma", gamma_filter,
                     description="Apply gamma correction")
        self.register("histogram-eq", histogram_equalization_filter,
                     description="Apply histogram equalization")
        self.register("morphology", morphology_filter,
                     description="Apply morphological operations")
        self.register("contours", contours_filter,
                     description="Find and draw contours")
        self.register("corners", corners_filter,
                     description="Detect corners using Harris")
        self.register("optical-flow", optical_flow_filter,
                     description="Compute optical flow")
        
        # Sink functions
        self.register("display", display_sink, is_sink=True,
                     description="Display frames in window")
        self.register("window", window_sink, is_sink=True,
                     description="Display frames in window (alias)")
        self.register("save", save_sink, is_sink=True,
                     description="Save frames to file")
        self.register("record", record_sink, is_sink=True,
                     description="Record frames to video file")


# Source functions
def webcam_source(frame: Optional[Frame], camera_id: int = 0, **kwargs) -> Optional[Frame]:
    """Capture frame from webcam"""
    if not hasattr(webcam_source, 'cap'):
        webcam_source.cap = cv2.VideoCapture(camera_id)
        if not webcam_source.cap.isOpened():
            print(f"Error: Could not open camera {camera_id}")
            return None
    
    ret, frame_data = webcam_source.cap.read()
    if not ret:
        return None
    
    height, width = frame_data.shape[:2]
    return Frame(
        data=frame_data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


def camera_source(frame: Optional[Frame], device: int = 0, **kwargs) -> Optional[Frame]:
    """Alias for webcam_source"""
    return webcam_source(frame, camera_id=device, **kwargs)


def capture_source(frame: Optional[Frame], filename: str = "", **kwargs) -> Optional[Frame]:
    """Capture frames from video file"""
    if not hasattr(capture_source, 'cap'):
        if not filename:
            print("Error: filename parameter required for capture source")
            return None
        capture_source.cap = cv2.VideoCapture(filename)
        if not capture_source.cap.isOpened():
            print(f"Error: Could not open video file {filename}")
            return None
    
    ret, frame_data = capture_source.cap.read()
    if not ret:
        return None
    
    height, width = frame_data.shape[:2]
    return Frame(
        data=frame_data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


def test_pattern_source(frame: Optional[Frame], width: int = 640, height: int = 480, 
                       pattern: str = "checkerboard", **kwargs) -> Optional[Frame]:
    """Generate test pattern frames"""
    if pattern == "checkerboard":
        # Create checkerboard pattern
        checker_size = 32
        data = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(0, height, checker_size):
            for x in range(0, width, checker_size):
                if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                    data[y:y+checker_size, x:x+checker_size] = 255
    
    elif pattern == "gradient":
        # Create gradient pattern
        data = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(width):
            intensity = int((i / width) * 255)
            data[:, i] = [intensity, intensity, intensity]
    
    else:
        # Solid color
        data = np.full((height, width, 3), 128, dtype=np.uint8)
    
    return Frame(
        data=data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


# Processing functions
def grayscale_filter(frame: Frame, **kwargs) -> Frame:
    """Convert frame to grayscale"""
    if frame.format == FrameFormat.GRAY:
        return frame
    
    if frame.format == FrameFormat.BGR:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    elif frame.format == FrameFormat.RGB:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2GRAY)
    else:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_RGBA2GRAY)
    
    return Frame(
        data=gray_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def blur_filter(frame: Frame, kernel_size: int = 5, sigma: float = 0, **kwargs) -> Frame:
    """Apply Gaussian blur to frame"""
    if sigma == 0:
        sigma = kernel_size / 6.0
    
    blurred_data = cv2.GaussianBlur(frame.data, (kernel_size, kernel_size), sigma)
    
    return Frame(
        data=blurred_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def edge_filter(frame: Frame, low_threshold: int = 50, high_threshold: int = 150, **kwargs) -> Frame:
    """Detect edges using Canny edge detection"""
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        if frame.format == FrameFormat.BGR:
            gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
        elif frame.format == FrameFormat.RGB:
            gray_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2GRAY)
        else:
            gray_data = cv2.cvtColor(frame.data, cv2.COLOR_RGBA2GRAY)
    else:
        gray_data = frame.data
    
    edges = cv2.Canny(gray_data, low_threshold, high_threshold)
    
    return Frame(
        data=edges,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def threshold_filter(frame: Frame, threshold: int = 127, max_val: int = 255, **kwargs) -> Frame:
    """Apply binary threshold"""
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_frame = grayscale_filter(frame)
        gray_data = gray_frame.data
    else:
        gray_data = frame.data
    
    _, thresh_data = cv2.threshold(gray_data, threshold, max_val, cv2.THRESH_BINARY)
    
    return Frame(
        data=thresh_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def resize_filter(frame: Frame, width: int = None, height: int = None, 
                 scale: float = None, **kwargs) -> Frame:
    """Resize frame"""
    if scale:
        new_width = int(frame.width * scale)
        new_height = int(frame.height * scale)
    else:
        new_width = width or frame.width
        new_height = height or frame.height
    
    resized_data = cv2.resize(frame.data, (new_width, new_height))
    
    return Frame(
        data=resized_data,
        format=frame.format,
        width=new_width,
        height=new_height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def flip_filter(frame: Frame, horizontal: bool = False, vertical: bool = False, **kwargs) -> Frame:
    """Flip frame"""
    flip_code = None
    if horizontal and vertical:
        flip_code = -1
    elif horizontal:
        flip_code = 1
    elif vertical:
        flip_code = 0
    
    if flip_code is not None:
        flipped_data = cv2.flip(frame.data, flip_code)
    else:
        flipped_data = frame.data
    
    return Frame(
        data=flipped_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def rotate_filter(frame: Frame, angle: float = 0, **kwargs) -> Frame:
    """Rotate frame by angle degrees"""
    if angle == 0:
        return frame
    
    center = (frame.width // 2, frame.height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_data = cv2.warpAffine(frame.data, rotation_matrix, (frame.width, frame.height))
    
    return Frame(
        data=rotated_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Display manager for handling threading issues
class DisplayManager:
    """Manages display operations to handle threading issues on macOS"""

    def __init__(self):
        self.display_queue = Queue()
        self.running = True
        self.windows = {}

    def add_frame(self, frame: Frame, window_name: str = "VidPipe"):
        """Add a frame to be displayed (thread-safe)"""
        self.display_queue.put((frame, window_name))

    def process_display_queue(self):
        """Process the display queue (call this from main thread)"""
        while not self.display_queue.empty():
            try:
                frame, window_name = self.display_queue.get_nowait()

                # Ensure window is initialized
                if window_name not in self.windows:
                    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
                    self.windows[window_name] = True

                # Convert frame data to ensure it's in the right format
                display_data = frame.data.copy()
                if frame.format == FrameFormat.GRAY:
                    display_data = cv2.cvtColor(display_data, cv2.COLOR_GRAY2BGR)

                cv2.imshow(window_name, display_data)

            except Exception as e:
                print(f"Display queue error: {e}")

        # Handle keyboard input
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC to quit
            cv2.destroyAllWindows()
            return False
        return True

# Global display manager instance
_display_manager = DisplayManager()

# Sink functions
def display_sink(frame: Frame, window_name: str = "VidPipe", **kwargs):
    """Display frame in OpenCV window"""
    try:
        # Add frame to display queue (thread-safe)
        _display_manager.add_frame(frame, window_name)
        return True
    except Exception as e:
        print(f"Display queue error: {e}")
        return False


def window_sink(frame: Frame, **kwargs):
    """Alias for display_sink"""
    return display_sink(frame, **kwargs)


def save_sink(frame: Frame, filename: str = "frame_{timestamp}.png", **kwargs):
    """Save frame to file"""
    if "{timestamp}" in filename:
        filename = filename.format(timestamp=int(frame.timestamp))
    cv2.imwrite(filename, frame.data)


def record_sink(frame: Frame, filename: str = "output.avi", fps: float = 30.0, **kwargs):
    """Record frames to video file"""
    if not hasattr(record_sink, 'writer'):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        record_sink.writer = cv2.VideoWriter(
            filename, fourcc, fps, (frame.width, frame.height)
        )
    
    record_sink.writer.write(frame.data)


# Advanced processing functions
def crop_filter(frame: Frame, x: int = 0, y: int = 0, width: int = None, height: int = None, **kwargs) -> Frame:
    """Crop frame to specified region"""
    if width is None:
        width = frame.width - x
    if height is None:
        height = frame.height - y
    
    # Ensure bounds are valid
    x = max(0, min(x, frame.width - 1))
    y = max(0, min(y, frame.height - 1))
    width = max(1, min(width, frame.width - x))
    height = max(1, min(height, frame.height - y))
    
    cropped_data = frame.data[y:y+height, x:x+width]
    
    return Frame(
        data=cropped_data,
        format=frame.format,
        width=width,
        height=height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def brightness_filter(frame: Frame, brightness: float = 0, **kwargs) -> Frame:
    """Adjust frame brightness"""
    # brightness: -100 to 100, where 0 is no change
    brightness = max(-100, min(100, brightness))
    
    # Convert to OpenCV format (0-255 range)
    alpha = 1.0 + brightness / 100.0
    beta = brightness * 2.55  # Convert to 0-255 range
    
    adjusted_data = cv2.convertScaleAbs(frame.data, alpha=alpha, beta=beta)
    
    return Frame(
        data=adjusted_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def contrast_filter(frame: Frame, contrast: float = 0, **kwargs) -> Frame:
    """Adjust frame contrast"""
    # contrast: -100 to 100, where 0 is no change
    contrast = max(-100, min(100, contrast))
    
    # Convert to OpenCV format
    alpha = 1.0 + contrast / 100.0
    
    adjusted_data = cv2.convertScaleAbs(frame.data, alpha=alpha, beta=0)
    
    return Frame(
        data=adjusted_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def hue_filter(frame: Frame, hue: float = 0, **kwargs) -> Frame:
    """Adjust frame hue"""
    if frame.format == FrameFormat.GRAY:
        return frame  # Hue adjustment not applicable to grayscale
    
    # Convert to HSV
    if frame.format == FrameFormat.BGR:
        hsv_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2HSV)
    else:
        hsv_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2HSV)
    
    # Adjust hue
    hsv_data[:, :, 0] = (hsv_data[:, :, 0] + hue) % 180
    
    # Convert back to original format
    if frame.format == FrameFormat.BGR:
        adjusted_data = cv2.cvtColor(hsv_data, cv2.COLOR_HSV2BGR)
    else:
        adjusted_data = cv2.cvtColor(hsv_data, cv2.COLOR_HSV2RGB)
    
    return Frame(
        data=adjusted_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def saturation_filter(frame: Frame, saturation: float = 0, **kwargs) -> Frame:
    """Adjust frame saturation"""
    if frame.format == FrameFormat.GRAY:
        return frame  # Saturation adjustment not applicable to grayscale
    
    # Convert to HSV
    if frame.format == FrameFormat.BGR:
        hsv_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2HSV)
    else:
        hsv_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2HSV)
    
    # Adjust saturation
    hsv_data[:, :, 1] = np.clip(hsv_data[:, :, 1] * (1 + saturation / 100.0), 0, 255)
    
    # Convert back to original format
    if frame.format == FrameFormat.BGR:
        adjusted_data = cv2.cvtColor(hsv_data, cv2.COLOR_HSV2BGR)
    else:
        adjusted_data = cv2.cvtColor(hsv_data, cv2.COLOR_HSV2RGB)
    
    return Frame(
        data=adjusted_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def gamma_filter(frame: Frame, gamma: float = 1.0, **kwargs) -> Frame:
    """Apply gamma correction"""
    # gamma: 0.1 to 3.0, where 1.0 is no change
    gamma = max(0.1, min(3.0, gamma))
    
    # Build lookup table
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    
    # Apply gamma correction
    corrected_data = cv2.LUT(frame.data, table)
    
    return Frame(
        data=corrected_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def histogram_equalization_filter(frame: Frame, **kwargs) -> Frame:
    """Apply histogram equalization"""
    if frame.format == FrameFormat.GRAY:
        # Grayscale histogram equalization
        equalized_data = cv2.equalizeHist(frame.data)
    else:
        # Color histogram equalization
        if frame.format == FrameFormat.BGR:
            # Convert to YUV and equalize Y channel
            yuv_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2YUV)
            yuv_data[:, :, 0] = cv2.equalizeHist(yuv_data[:, :, 0])
            equalized_data = cv2.cvtColor(yuv_data, cv2.COLOR_YUV2BGR)
        else:
            # Convert to YUV and equalize Y channel
            yuv_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2YUV)
            yuv_data[:, :, 0] = cv2.equalizeHist(yuv_data[:, :, 0])
            equalized_data = cv2.cvtColor(yuv_data, cv2.COLOR_YUV2RGB)
    
    return Frame(
        data=equalized_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def morphology_filter(frame: Frame, operation: str = "open", kernel_size: int = 5, **kwargs) -> Frame:
    """Apply morphological operations"""
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_frame = grayscale_filter(frame)
        gray_data = gray_frame.data
    else:
        gray_data = frame.data
    
    # Create kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # Apply morphological operation
    if operation == "open":
        result_data = cv2.morphologyEx(gray_data, cv2.MORPH_OPEN, kernel)
    elif operation == "close":
        result_data = cv2.morphologyEx(gray_data, cv2.MORPH_CLOSE, kernel)
    elif operation == "erode":
        result_data = cv2.erode(gray_data, kernel)
    elif operation == "dilate":
        result_data = cv2.dilate(gray_data, kernel)
    else:
        result_data = gray_data
    
    return Frame(
        data=result_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def contours_filter(frame: Frame, min_area: int = 100, **kwargs) -> Frame:
    """Find and draw contours"""
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_frame = grayscale_filter(frame)
        gray_data = gray_frame.data
    else:
        gray_data = frame.data
    
    # Find contours
    contours, _ = cv2.findContours(gray_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = np.zeros_like(gray_data)
    else:
        output_data = np.zeros_like(frame.data)
    
    # Draw contours
    for contour in contours:
        if cv2.contourArea(contour) >= min_area:
            if frame.format == FrameFormat.GRAY:
                cv2.drawContours(output_data, [contour], -1, 255, 2)
            else:
                cv2.drawContours(output_data, [contour], -1, (0, 255, 0), 2)
    
    return Frame(
        data=output_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def corners_filter(frame: Frame, max_corners: int = 100, quality: float = 0.01, min_distance: float = 10, **kwargs) -> Frame:
    """Detect corners using Harris corner detection"""
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_frame = grayscale_filter(frame)
        gray_data = gray_frame.data
    else:
        gray_data = frame.data
    
    # Detect corners
    corners = cv2.goodFeaturesToTrack(gray_data, maxCorners=max_corners, 
                                     qualityLevel=quality, minDistance=min_distance)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw corners
    if corners is not None:
        for corner in corners:
            x, y = corner.ravel()
            cv2.circle(output_data, (int(x), int(y)), 5, (0, 0, 255), -1)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def optical_flow_filter(frame: Frame, **kwargs) -> Frame:
    """Compute optical flow (simplified version)"""
    # This is a placeholder implementation
    # A full optical flow implementation would require frame history
    # For now, just return the frame with a message
    if frame.format == FrameFormat.GRAY:
        output_data = frame.data.copy()
    else:
        gray_frame = grayscale_filter(frame)
        output_data = gray_frame.data
    
    # Add text indicating optical flow
    cv2.putText(output_data, "Optical Flow", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return Frame(
        data=output_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )