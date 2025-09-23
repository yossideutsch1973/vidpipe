"""
Built-in video processing functions for VidPipe
"""

import numpy as np
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from .pipeline import Frame, FrameFormat
import time
import threading
from queue import Queue

try:
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover - exercised only on headless systems
    cv2 = None  # type: ignore
    _CV2_IMPORT_ERROR = exc
else:  # pragma: no cover - exercised when OpenCV is available
    _CV2_IMPORT_ERROR = None


def _require_cv2():
    """Ensure OpenCV is available before executing a function that depends on it."""
    if cv2 is None:
        raise RuntimeError(
            "OpenCV (cv2) is required for this operation. Install opencv-python to enable video processing."
        ) from _CV2_IMPORT_ERROR


@dataclass
class FunctionDef:
    """Definition of a video processing function"""
    name: str
    function: Callable
    is_source: bool = False
    is_sink: bool = False
    description: str = ""
    parameters: Dict[str, str] = field(default_factory=dict)


class FunctionRegistry:
    """Registry for video processing functions"""
    
    def __init__(self):
        self.functions: Dict[str, FunctionDef] = {}
        self.register_builtin_functions()
    
    def register(self, name: str, function: Callable, is_source: bool = False,
                is_sink: bool = False, description: str = "",
                parameters: Optional[Dict[str, str]] = None):
        """Register a function"""
        self.functions[name] = FunctionDef(
            name=name,
            function=function,
            is_source=is_source,
            is_sink=is_sink,
            description=description,
            parameters=parameters or {}
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
        self.register(
            "webcam",
            webcam_source,
            is_source=True,
            description="Capture frames from webcam",
            parameters={"camera_id": "Camera device ID (default: 0)"}
        )
        self.register(
            "camera",
            camera_source,
            is_source=True,
            description="Capture frames from camera",
            parameters={"device": "Camera device ID (default: 0)"}
        )
        self.register(
            "capture",
            capture_source,
            is_source=True,
            description="Capture frames from video file",
            parameters={"filename": "Video file path"}
        )
        self.register(
            "test-pattern",
            test_pattern_source,
            is_source=True,
            description="Generate test pattern frames",
            parameters={
                "width": "Frame width (default: 640)",
                "height": "Frame height (default: 480)",
                "pattern": "Pattern type: 'checkerboard', 'gradient' (default: 'checkerboard')"
            }
        )
        
        # Processing functions
        self.register("grayscale", grayscale_filter,
                     description="Convert to grayscale")
        self.register("gray", grayscale_filter,
                     description="Convert to grayscale (alias)")
        self.register(
            "blur",
            blur_filter,
            description="Apply Gaussian blur",
            parameters={
                "kernel_size": "Blur kernel size (default: 5)",
                "sigma": "Gaussian sigma (default: kernel_size/6)"
            }
        )
        self.register(
            "edges",
            edge_filter,
            description="Detect edges using Canny",
            parameters={
                "low_threshold": "Low threshold for Canny (default: 50)",
                "high_threshold": "High threshold for Canny (default: 150)"
            }
        )
        self.register(
            "threshold",
            threshold_filter,
            description="Apply binary threshold",
            parameters={
                "threshold": "Threshold value (default: 127)",
                "max_val": "Maximum value (default: 255)"
            }
        )
        self.register(
            "resize",
            resize_filter,
            description="Resize frame",
            parameters={
                "width": "New width",
                "height": "New height",
                "scale": "Scale factor (alternative to width/height)"
            }
        )
        self.register(
            "flip",
            flip_filter,
            description="Flip frame horizontally or vertically",
            parameters={
                "horizontal": "Flip horizontally (default: False)",
                "vertical": "Flip vertically (default: False)"
            }
        )
        self.register(
            "rotate",
            rotate_filter,
            description="Rotate frame",
            parameters={"angle": "Rotation angle in degrees"}
        )
        self.register(
            "crop",
            crop_filter,
            description="Crop frame to specified region",
            parameters={
                "x": "X coordinate of crop region (default: 0)",
                "y": "Y coordinate of crop region (default: 0)",
                "width": "Width of crop region (default: remaining width)",
                "height": "Height of crop region (default: remaining height)"
            }
        )
        self.register(
            "brightness",
            brightness_filter,
            description="Adjust brightness",
            parameters={"brightness": "Brightness adjustment (-100 to 100, default: 0)"}
        )
        self.register(
            "contrast",
            contrast_filter,
            description="Adjust contrast",
            parameters={"contrast": "Contrast adjustment (-100 to 100, default: 0)"}
        )
        self.register(
            "hue",
            hue_filter,
            description="Adjust hue",
            parameters={"hue": "Hue adjustment in degrees (default: 0)"}
        )
        self.register(
            "saturation",
            saturation_filter,
            description="Adjust saturation",
            parameters={"saturation": "Saturation adjustment (-100 to 100, default: 0)"}
        )
        self.register(
            "gamma",
            gamma_filter,
            description="Apply gamma correction",
            parameters={"gamma": "Gamma correction value (0.1 to 3.0, default: 1.0)"}
        )
        self.register("histogram-eq", histogram_equalization_filter,
                     description="Apply histogram equalization")
        self.register(
            "morphology",
            morphology_filter,
            description="Apply morphological operations",
            parameters={
                "operation": "Morphological operation: 'open', 'close', 'erode', 'dilate' (default: 'open')",
                "kernel_size": "Kernel size (default: 5)"
            }
        )
        self.register(
            "contours",
            contours_filter,
            description="Find and draw contours",
            parameters={"min_area": "Minimum contour area (default: 100)"}
        )
        self.register(
            "corners",
            corners_filter,
            description="Detect corners using Harris",
            parameters={
                "max_corners": "Maximum number of corners (default: 100)",
                "quality": "Corner quality threshold (default: 0.01)",
                "min_distance": "Minimum distance between corners (default: 10)"
            }
        )
        self.register("optical-flow", optical_flow_filter,
                     description="Compute optical flow")
        
        # Advanced image processing functions
        self.register("sharpen", sharpen_filter,
                     description="Apply sharpening filter")
        self.register("emboss", emboss_filter,
                     description="Apply emboss effect")
        self.register("median", median_filter,
                     description="Apply median filter",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        self.register("bilateral", bilateral_filter,
                     description="Apply bilateral filter",
                     parameters={
                         "d": "Diameter of pixel neighborhood (default: 9)",
                         "sigma_color": "Filter sigma in color space (default: 75)",
                         "sigma_space": "Filter sigma in coordinate space (default: 75)"
                     })
        self.register("gaussian", gaussian_filter,
                     description="Apply Gaussian filter",
                     parameters={
                         "kernel_size": "Kernel size (default: 5)",
                         "sigma_x": "Gaussian sigma X (default: 0)",
                         "sigma_y": "Gaussian sigma Y (default: 0)"
                     })
        self.register("laplacian", laplacian_filter,
                     description="Apply Laplacian edge detection")
        self.register("sobel-x", sobel_x_filter,
                     description="Apply Sobel X gradient")
        self.register("sobel-y", sobel_y_filter,
                     description="Apply Sobel Y gradient")
        self.register("scharr-x", scharr_x_filter,
                     description="Apply Scharr X gradient")
        self.register("scharr-y", scharr_y_filter,
                     description="Apply Scharr Y gradient")
        
        # Color space conversions
        self.register("bgr2rgb", bgr2rgb_filter,
                     description="Convert BGR to RGB")
        self.register("rgb2bgr", rgb2bgr_filter,
                     description="Convert RGB to BGR")
        self.register("bgr2hsv", bgr2hsv_filter,
                     description="Convert BGR to HSV")
        self.register("hsv2bgr", hsv2bgr_filter,
                     description="Convert HSV to BGR")
        self.register("bgr2lab", bgr2lab_filter,
                     description="Convert BGR to LAB")
        self.register("lab2bgr", lab2bgr_filter,
                     description="Convert LAB to BGR")
        self.register("bgr2yuv", bgr2yuv_filter,
                     description="Convert BGR to YUV")
        self.register("yuv2bgr", yuv2bgr_filter,
                     description="Convert YUV to BGR")
        
        # Geometric transformations
        self.register("translate", translate_filter,
                     description="Translate (move) image",
                     parameters={
                         "x": "X translation (default: 0)",
                         "y": "Y translation (default: 0)"
                     })
        self.register("scale", scale_filter,
                     description="Scale image",
                     parameters={
                         "scale_x": "X scale factor (default: 1.0)",
                         "scale_y": "Y scale factor (default: 1.0)"
                     })
        self.register("shear", shear_filter,
                     description="Apply shear transformation",
                     parameters={
                         "shear_x": "X shear factor (default: 0)",
                         "shear_y": "Y shear factor (default: 0)"
                     })
        self.register("perspective", perspective_filter,
                     description="Apply perspective transformation",
                     parameters={"matrix": "3x3 perspective matrix"})
        self.register("affine", affine_filter,
                     description="Apply affine transformation",
                     parameters={"matrix": "2x3 affine matrix"})
        
        # Mathematical operations
        self.register("add", add_filter,
                     description="Add constant value to all pixels",
                     parameters={"value": "Value to add (default: 10)"})
        self.register("subtract", subtract_filter,
                     description="Subtract constant value from all pixels",
                     parameters={"value": "Value to subtract (default: 10)"})
        self.register("multiply", multiply_filter,
                     description="Multiply all pixels by constant",
                     parameters={"value": "Multiplication factor (default: 1.1)"})
        self.register("divide", divide_filter,
                     description="Divide all pixels by constant",
                     parameters={"value": "Division factor (default: 1.1)"})
        self.register("abs", abs_filter,
                     description="Take absolute value of all pixels")
        self.register("square", square_filter,
                     description="Square all pixel values")
        self.register("sqrt", sqrt_filter,
                     description="Take square root of all pixel values")
        self.register("log", log_filter,
                     description="Take logarithm of all pixel values")
        self.register("exp", exp_filter,
                     description="Take exponential of all pixel values")
        self.register("power", power_filter,
                     description="Raise all pixels to power",
                     parameters={"power": "Power value (default: 2)"})
        
        # Statistical operations
        self.register("mean", mean_filter,
                     description="Apply mean filter",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        self.register("min", min_filter,
                     description="Apply minimum filter",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        self.register("max", max_filter,
                     description="Apply maximum filter",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        self.register("variance", variance_filter,
                     description="Calculate local variance",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        self.register("std", std_filter,
                     description="Calculate local standard deviation",
                     parameters={"kernel_size": "Kernel size (default: 5)"})
        
        # Noise and distortion
        self.register("gaussian-noise", gaussian_noise_filter,
                     description="Add Gaussian noise",
                     parameters={
                         "mean": "Noise mean (default: 0)",
                         "std": "Noise standard deviation (default: 25)"
                     })
        self.register("salt-pepper", salt_pepper_filter,
                     description="Add salt and pepper noise",
                     parameters={"amount": "Noise amount (0-1, default: 0.05)"})
        self.register("speckle", speckle_filter,
                     description="Add speckle noise",
                     parameters={"variance": "Noise variance (default: 0.1)"})
        
        # Feature detection
        self.register("hough-lines", hough_lines_filter,
                     description="Detect lines using Hough transform",
                     parameters={
                         "rho": "Distance resolution (default: 1)",
                         "theta": "Angle resolution (default: np.pi/180)",
                         "threshold": "Accumulator threshold (default: 100)"
                     })
        self.register("hough-circles", hough_circles_filter,
                     description="Detect circles using Hough transform",
                     parameters={
                         "dp": "Inverse ratio of accumulator resolution (default: 1)",
                         "min_dist": "Minimum distance between centers (default: 50)",
                         "param1": "Upper threshold for edge detection (default: 100)",
                         "param2": "Accumulator threshold (default: 30)"
                     })
        self.register("sift", sift_filter,
                     description="SIFT feature detection")
        self.register("surf", surf_filter,
                     description="SURF feature detection")
        self.register("orb", orb_filter,
                     description="ORB feature detection")
        self.register("fast", fast_filter,
                     description="FAST corner detection",
                     parameters={"threshold": "Corner threshold (default: 10)"})
        self.register("brief", brief_filter,
                     description="BRIEF feature description")
        
        # Template matching
        self.register("template-match", template_match_filter,
                     description="Template matching",
                     parameters={
                         "template": "Template image path",
                         "method": "Matching method (default: 'TM_CCOEFF_NORMED')"
                     })
        
        # Segmentation
        self.register("watershed", watershed_filter,
                     description="Watershed segmentation")
        self.register("kmeans", kmeans_filter,
                     description="K-means clustering segmentation",
                     parameters={"k": "Number of clusters (default: 3)"})
        self.register("region-growing", region_growing_filter,
                     description="Region growing segmentation",
                     parameters={"threshold": "Growth threshold (default: 10)"})
        
        # Additional sources
        self.register("solid-color", solid_color_source,
                     is_source=True,
                     description="Generate solid color frames",
                     parameters={
                         "width": "Frame width (default: 640)",
                         "height": "Frame height (default: 480)",
                         "color": "Color as [B,G,R] tuple (default: [0,0,0])"
                     })
        self.register("random-noise", random_noise_source,
                     is_source=True,
                     description="Generate random noise frames",
                     parameters={
                         "width": "Frame width (default: 640)",
                         "height": "Frame height (default: 480)",
                         "noise_type": "Noise type: 'uniform', 'gaussian' (default: 'uniform')"
                     })
        self.register("image-loader", image_loader_source,
                     is_source=True,
                     description="Load static image as continuous frames",
                     parameters={"filename": "Image file path"})
        self.register("mandelbrot", mandelbrot_source,
                     is_source=True,
                     description="Generate Mandelbrot fractal",
                     parameters={
                         "width": "Frame width (default: 640)",
                         "height": "Frame height (default: 480)",
                         "zoom": "Zoom level (default: 1.0)",
                         "center_x": "Center X coordinate (default: -0.5)",
                         "center_y": "Center Y coordinate (default: 0.0)"
                     })
        
        # Sink functions
        self.register(
            "display",
            display_sink,
            is_sink=True,
            description="Display frames in window",
            parameters={"window_name": "Window name (default: 'VidPipe')"}
        )
        self.register(
            "window",
            window_sink,
            is_sink=True,
            description="Display frames in window (alias)",
            parameters={"window_name": "Window name (default: 'VidPipe')"}
        )
        self.register(
            "save",
            save_sink,
            is_sink=True,
            description="Save frames to file",
            parameters={"filename": "Output filename pattern"}
        )
        self.register(
            "record",
            record_sink,
            is_sink=True,
            description="Record frames to video file",
            parameters={
                "filename": "Output video filename (default: 'output.avi')",
                "fps": "Frames per second (default: 30.0)"
            }
        )
        self.register(
            "csv-export",
            csv_export_sink,
            is_sink=True,
            description="Export frame statistics to CSV",
            parameters={"filename": "CSV filename (default: 'stats.csv')"}
        )
        self.register(
            "json-export",
            json_export_sink,
            is_sink=True,
            description="Export frame metadata to JSON",
            parameters={"filename": "JSON filename (default: 'metadata.json')"}
        )
        self.register(
            "histogram-sink",
            histogram_sink,
            is_sink=True,
            description="Display live histogram",
            parameters={"window_name": "Histogram window name (default: 'Histogram')"}
        )
        
        # Additional processing functions
        self.register("invert", invert_filter,
                     description="Invert colors")
        self.register("sepia", sepia_filter,
                     description="Apply sepia tone effect")
        self.register("black-white", black_white_filter,
                     description="Convert to black and white with threshold",
                     parameters={"threshold": "Threshold value (default: 127)"})
        self.register("vintage", vintage_filter,
                     description="Apply vintage effect")
        self.register("cartoon", cartoon_filter,
                     description="Apply cartoon effect")
        self.register("sketch", sketch_filter,
                     description="Convert to pencil sketch")
        self.register("thermal", thermal_filter,
                     description="Apply thermal vision effect")
        self.register("night-vision", night_vision_filter,
                     description="Apply night vision effect")
        self.register("x-ray", xray_filter,
                     description="Apply X-ray effect")
        self.register("polaroid", polaroid_filter,
                     description="Apply Polaroid effect")
        self.register("cross-process", cross_process_filter,
                     description="Apply cross-processing effect")
        self.register("lomo", lomo_filter,
                     description="Apply lomography effect")
        self.register("vignette", vignette_filter,
                     description="Apply vignette effect",
                     parameters={"strength": "Vignette strength (default: 0.5)"})
        self.register("fisheye", fisheye_filter,
                     description="Apply fisheye distortion")
        self.register("barrel", barrel_filter,
                     description="Apply barrel distortion",
                     parameters={"strength": "Distortion strength (default: 0.1)"})
        self.register("pinch", pinch_filter,
                     description="Apply pinch distortion",
                     parameters={"strength": "Pinch strength (default: 0.5)"})
        self.register("swirl", swirl_filter,
                     description="Apply swirl distortion",
                     parameters={"angle": "Swirl angle in degrees (default: 45)"})
        self.register("mirror-horizontal", mirror_h_filter,
                     description="Mirror horizontally")
        self.register("mirror-vertical", mirror_v_filter,
                     description="Mirror vertically")
        self.register("kaleidoscope", kaleidoscope_filter,
                     description="Apply kaleidoscope effect",
                     parameters={"segments": "Number of segments (default: 6)"})
        self.register("pixelate", pixelate_filter,
                     description="Apply pixelation effect",
                     parameters={"block_size": "Pixel block size (default: 10)"})
        self.register("mosaic", mosaic_filter,
                     description="Apply mosaic effect",
                     parameters={"tile_size": "Mosaic tile size (default: 20)"})
        self.register("oil-painting", oil_painting_filter,
                     description="Apply oil painting effect")
        self.register("watercolor", watercolor_filter,
                     description="Apply watercolor effect")
        self.register("posterize", posterize_filter,
                     description="Apply posterization",
                     parameters={"levels": "Number of color levels (default: 4)"})
        self.register("solarize", solarize_filter,
                     description="Apply solarization effect",
                     parameters={"threshold": "Solarization threshold (default: 128)"})
        self.register("duotone", duotone_filter,
                     description="Apply duotone effect",
                     parameters={
                         "color1": "First color as [B,G,R] (default: [0,0,255])",
                         "color2": "Second color as [B,G,R] (default: [255,255,0])"
                     })
        self.register("tritone", tritone_filter,
                     description="Apply tritone effect",
                     parameters={
                         "color1": "First color as [B,G,R] (default: [0,0,255])",
                         "color2": "Second color as [B,G,R] (default: [0,255,0])",
                         "color3": "Third color as [B,G,R] (default: [255,0,0])"
                     })
        self.register("color-replace", color_replace_filter,
                     description="Replace specific color",
                     parameters={
                         "target_color": "Target color to replace [B,G,R]",
                         "replacement_color": "Replacement color [B,G,R]",
                         "tolerance": "Color tolerance (default: 50)"
                     })
        self.register("color-enhance", color_enhance_filter,
                     description="Enhance specific color",
                     parameters={
                         "target_color": "Target color to enhance [B,G,R]",
                         "enhancement": "Enhancement factor (default: 1.5)"
                     })
        self.register("white-balance", white_balance_filter,
                     description="Auto white balance correction")
        self.register("exposure", exposure_filter,
                     description="Adjust exposure",
                     parameters={"stops": "Exposure adjustment in stops (default: 0)"})
        self.register("shadows-highlights", shadows_highlights_filter,
                     description="Adjust shadows and highlights",
                     parameters={
                         "shadows": "Shadow adjustment (-100 to 100, default: 0)",
                         "highlights": "Highlight adjustment (-100 to 100, default: 0)"
                     })
        self.register("vibrance", vibrance_filter,
                     description="Adjust vibrance",
                     parameters={"vibrance": "Vibrance adjustment (-100 to 100, default: 0)"})
        self.register("clarity", clarity_filter,
                     description="Adjust clarity/structure",
                     parameters={"amount": "Clarity amount (default: 0.5)"})
        self.register("dehaze", dehaze_filter,
                     description="Remove atmospheric haze")
        self.register("denoise", denoise_filter,
                     description="Reduce noise",
                     parameters={"strength": "Denoising strength (default: 10)"})
        self.register("unsharp-mask", unsharp_mask_filter,
                     description="Apply unsharp mask sharpening",
                     parameters={
                         "amount": "Sharpening amount (default: 1.0)",
                         "radius": "Blur radius (default: 1.0)",
                         "threshold": "Threshold (default: 0)"
                     })
        self.register("tilt-shift", tilt_shift_filter,
                     description="Apply tilt-shift effect",
                     parameters={"focus_y": "Focus line Y position (0-1, default: 0.5)"})
        self.register("depth-of-field", depth_of_field_filter,
                     description="Simulate depth of field",
                     parameters={
                         "focus_distance": "Focus distance (default: 0.5)",
                         "blur_amount": "Background blur amount (default: 5)"
                     })
        self.register("motion-blur", motion_blur_filter,
                     description="Apply motion blur",
                     parameters={
                         "angle": "Motion direction in degrees (default: 0)",
                         "distance": "Motion distance (default: 15)"
                     })
        self.register("radial-blur", radial_blur_filter,
                     description="Apply radial blur",
                     parameters={
                         "center_x": "Blur center X (0-1, default: 0.5)",
                         "center_y": "Blur center Y (0-1, default: 0.5)",
                         "amount": "Blur amount (default: 10)"
                     })
        self.register("zoom-blur", zoom_blur_filter,
                     description="Apply zoom blur",
                     parameters={"amount": "Zoom blur amount (default: 10)"})
        self.register("chromatic-aberration", chromatic_aberration_filter,
                     description="Add chromatic aberration",
                     parameters={"strength": "Aberration strength (default: 2)"})
        self.register("lens-distortion", lens_distortion_filter,
                     description="Apply lens distortion",
                     parameters={"amount": "Distortion amount (default: 0.1)"})
        self.register("film-grain", film_grain_filter,
                     description="Add film grain",
                     parameters={"intensity": "Grain intensity (default: 0.1)"})
        self.register("color-grading", color_grading_filter,
                     description="Apply color grading",
                     parameters={
                         "shadows": "Shadow color tint [B,G,R]",
                         "midtones": "Midtone color tint [B,G,R]",
                         "highlights": "Highlight color tint [B,G,R]"
                     })
        self.register(
            "display",
            display_sink,
            is_sink=True,
            description="Display frames in window",
            parameters={"window_name": "Window name (default: 'VidPipe')"}
        )
        self.register(
            "window",
            window_sink,
            is_sink=True,
            description="Display frames in window (alias)",
            parameters={"window_name": "Window name (default: 'VidPipe')"}
        )
        self.register(
            "save",
            save_sink,
            is_sink=True,
            description="Save frames to file",
            parameters={"filename": "Output filename pattern"}
        )
        self.register(
            "record",
            record_sink,
            is_sink=True,
            description="Record frames to video file",
            parameters={
                "filename": "Output video filename (default: 'output.avi')",
                "fps": "Frames per second (default: 30.0)"
            }
        )


# Source functions
def webcam_source(frame: Optional[Frame], camera_id: int = 0, **kwargs) -> Optional[Frame]:
    """Capture frame from webcam"""
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
        _require_cv2()
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
    """Queue a frame to be shown in an OpenCV window.

    Parameters
    ----------
    frame: Frame
        The video frame to display.
    window_name: str, optional
        Name of the window used for display.

    Returns
    -------
    bool
        ``True`` if the frame was queued successfully, ``False`` otherwise.

    Notes
    -----
    Frames are only rendered when ``DisplayManager.process_display_queue`` is
    called from the main thread.
    """
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
    """Save a frame to an image file.

    Parameters
    ----------
    frame: Frame
        The video frame to save.
    filename: str, optional
        Destination filename. ``{timestamp}`` in the name is replaced with the
        frame's timestamp to make filenames unique.
    """
    _require_cv2()
    if "{timestamp}" in filename:
        filename = filename.format(timestamp=int(frame.timestamp))
    cv2.imwrite(filename, frame.data)


def record_sink(frame: Frame, filename: str = "output.avi", fps: float = 30.0, **kwargs):
    """Append frames to a video file.

    Parameters
    ----------
    frame: Frame
        The video frame to write.
    filename: str, optional
        Output video filename. The writer is created lazily on first call.
    fps: float, optional
        Frames-per-second used for the output file.
    """
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    _require_cv2()
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
    """Visualize dense optical flow using the Farneback algorithm."""
    _require_cv2()
    # Convert input to grayscale
    gray = grayscale_filter(frame).data if frame.format != FrameFormat.GRAY else frame.data

    # Initialize previous frame storage on first call
    if not hasattr(optical_flow_filter, "_prev"):
        optical_flow_filter._prev = gray
        blank = np.zeros((frame.height, frame.width, 3), dtype=np.uint8)
        blank[..., 1] = 255
        return Frame(
            data=blank,
            format=FrameFormat.BGR,
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy(),
        )

    flow = cv2.calcOpticalFlowFarneback(
        optical_flow_filter._prev, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
    )
    optical_flow_filter._prev = gray

    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv = np.zeros((frame.height, frame.width, 3), dtype=np.uint8)
    hsv[..., 0] = angle * 180 / np.pi / 2
    hsv[..., 1] = 255
    hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return Frame(
        data=bgr,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy(),
    )


# Advanced image processing functions
def sharpen_filter(frame: Frame, **kwargs) -> Frame:
    """Apply sharpening filter"""
    _require_cv2()
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened_data = cv2.filter2D(frame.data, -1, kernel)
    
    return Frame(
        data=sharpened_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def emboss_filter(frame: Frame, **kwargs) -> Frame:
    """Apply emboss effect"""
    _require_cv2()
    kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
    embossed_data = cv2.filter2D(frame.data, -1, kernel)
    
    return Frame(
        data=embossed_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def median_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Apply median filter"""
    _require_cv2()
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    filtered_data = cv2.medianBlur(frame.data, kernel_size)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def bilateral_filter(frame: Frame, d: int = 9, sigma_color: float = 75, sigma_space: float = 75, **kwargs) -> Frame:
    """Apply bilateral filter"""
    _require_cv2()
    filtered_data = cv2.bilateralFilter(frame.data, d, sigma_color, sigma_space)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def gaussian_filter(frame: Frame, kernel_size: int = 5, sigma_x: float = 0, sigma_y: float = 0, **kwargs) -> Frame:
    """Apply Gaussian filter"""
    _require_cv2()
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    filtered_data = cv2.GaussianBlur(frame.data, (kernel_size, kernel_size), sigma_x, sigmaY=sigma_y)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def laplacian_filter(frame: Frame, **kwargs) -> Frame:
    """Apply Laplacian edge detection"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    laplacian_data = cv2.Laplacian(gray_data, cv2.CV_64F)
    laplacian_data = np.uint8(np.absolute(laplacian_data))
    
    return Frame(
        data=laplacian_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def sobel_x_filter(frame: Frame, **kwargs) -> Frame:
    """Apply Sobel X gradient"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    sobel_data = cv2.Sobel(gray_data, cv2.CV_64F, 1, 0, ksize=3)
    sobel_data = np.uint8(np.absolute(sobel_data))
    
    return Frame(
        data=sobel_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def sobel_y_filter(frame: Frame, **kwargs) -> Frame:
    """Apply Sobel Y gradient"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    sobel_data = cv2.Sobel(gray_data, cv2.CV_64F, 0, 1, ksize=3)
    sobel_data = np.uint8(np.absolute(sobel_data))
    
    return Frame(
        data=sobel_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def scharr_x_filter(frame: Frame, **kwargs) -> Frame:
    """Apply Scharr X gradient"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    scharr_data = cv2.Scharr(gray_data, cv2.CV_64F, 1, 0)
    scharr_data = np.uint8(np.absolute(scharr_data))
    
    return Frame(
        data=scharr_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def scharr_y_filter(frame: Frame, **kwargs) -> Frame:
    """Apply Scharr Y gradient"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    scharr_data = cv2.Scharr(gray_data, cv2.CV_64F, 0, 1)
    scharr_data = np.uint8(np.absolute(scharr_data))
    
    return Frame(
        data=scharr_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Color space conversions
def bgr2rgb_filter(frame: Frame, **kwargs) -> Frame:
    """Convert BGR to RGB"""
    _require_cv2()
    if frame.format == FrameFormat.BGR:
        rgb_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2RGB)
        return Frame(
            data=rgb_data,
            format=FrameFormat.RGB,
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy()
        )
    return frame


def rgb2bgr_filter(frame: Frame, **kwargs) -> Frame:
    """Convert RGB to BGR"""
    _require_cv2()
    if frame.format == FrameFormat.RGB:
        bgr_data = cv2.cvtColor(frame.data, cv2.COLOR_RGB2BGR)
        return Frame(
            data=bgr_data,
            format=FrameFormat.BGR,
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy()
        )
    return frame


def bgr2hsv_filter(frame: Frame, **kwargs) -> Frame:
    """Convert BGR to HSV"""
    _require_cv2()
    if frame.format == FrameFormat.BGR:
        hsv_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2HSV)
        return Frame(
            data=hsv_data,
            format=FrameFormat.BGR,  # Keep as BGR for display compatibility
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy()
        )
    return frame


def hsv2bgr_filter(frame: Frame, **kwargs) -> Frame:
    """Convert HSV to BGR"""
    _require_cv2()
    bgr_data = cv2.cvtColor(frame.data, cv2.COLOR_HSV2BGR)
    return Frame(
        data=bgr_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def bgr2lab_filter(frame: Frame, **kwargs) -> Frame:
    """Convert BGR to LAB"""
    _require_cv2()
    if frame.format == FrameFormat.BGR:
        lab_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2LAB)
        return Frame(
            data=lab_data,
            format=FrameFormat.BGR,  # Keep as BGR for display compatibility
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy()
        )
    return frame


def lab2bgr_filter(frame: Frame, **kwargs) -> Frame:
    """Convert LAB to BGR"""
    _require_cv2()
    bgr_data = cv2.cvtColor(frame.data, cv2.COLOR_LAB2BGR)
    return Frame(
        data=bgr_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def bgr2yuv_filter(frame: Frame, **kwargs) -> Frame:
    """Convert BGR to YUV"""
    _require_cv2()
    if frame.format == FrameFormat.BGR:
        yuv_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2YUV)
        return Frame(
            data=yuv_data,
            format=FrameFormat.BGR,  # Keep as BGR for display compatibility
            width=frame.width,
            height=frame.height,
            timestamp=frame.timestamp,
            metadata=frame.metadata.copy()
        )
    return frame


def yuv2bgr_filter(frame: Frame, **kwargs) -> Frame:
    """Convert YUV to BGR"""
    _require_cv2()
    bgr_data = cv2.cvtColor(frame.data, cv2.COLOR_YUV2BGR)
    return Frame(
        data=bgr_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Geometric transformations
def translate_filter(frame: Frame, x: float = 0, y: float = 0, **kwargs) -> Frame:
    """Translate (move) image"""
    _require_cv2()
    rows, cols = frame.height, frame.width
    M = np.float32([[1, 0, x], [0, 1, y]])
    translated_data = cv2.warpAffine(frame.data, M, (cols, rows))
    
    return Frame(
        data=translated_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def scale_filter(frame: Frame, scale_x: float = 1.0, scale_y: float = 1.0, **kwargs) -> Frame:
    """Scale image"""
    _require_cv2()
    scaled_data = cv2.resize(frame.data, None, fx=scale_x, fy=scale_y, interpolation=cv2.INTER_LINEAR)
    
    return Frame(
        data=scaled_data,
        format=frame.format,
        width=int(frame.width * scale_x),
        height=int(frame.height * scale_y),
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def shear_filter(frame: Frame, shear_x: float = 0, shear_y: float = 0, **kwargs) -> Frame:
    """Apply shear transformation"""
    _require_cv2()
    rows, cols = frame.height, frame.width
    M = np.float32([[1, shear_x, 0], [shear_y, 1, 0]])
    sheared_data = cv2.warpAffine(frame.data, M, (cols, rows))
    
    return Frame(
        data=sheared_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def perspective_filter(frame: Frame, matrix: Optional[np.ndarray] = None, **kwargs) -> Frame:
    """Apply perspective transformation"""
    _require_cv2()
    if matrix is None:
        # Default perspective transformation (slight perspective effect)
        rows, cols = frame.height, frame.width
        pts1 = np.float32([[0, 0], [cols, 0], [0, rows], [cols, rows]])
        pts2 = np.float32([[0, 0], [cols, 0], [cols*0.1, rows], [cols*0.9, rows]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
    
    transformed_data = cv2.warpPerspective(frame.data, matrix, (frame.width, frame.height))
    
    return Frame(
        data=transformed_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def affine_filter(frame: Frame, matrix: Optional[np.ndarray] = None, **kwargs) -> Frame:
    """Apply affine transformation"""
    _require_cv2()
    if matrix is None:
        # Default affine transformation (slight rotation and scaling)
        rows, cols = frame.height, frame.width
        pts1 = np.float32([[0, 0], [cols, 0], [0, rows]])
        pts2 = np.float32([[cols*0.1, rows*0.1], [cols*0.9, rows*0.1], [cols*0.1, rows*0.9]])
        matrix = cv2.getAffineTransform(pts1, pts2)
    
    transformed_data = cv2.warpAffine(frame.data, matrix, (frame.width, frame.height))
    
    return Frame(
        data=transformed_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Mathematical operations
def add_filter(frame: Frame, value: float = 10, **kwargs) -> Frame:
    """Add constant value to all pixels"""
    _require_cv2()
    added_data = cv2.add(frame.data, np.full_like(frame.data, value, dtype=np.uint8))
    
    return Frame(
        data=added_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def subtract_filter(frame: Frame, value: float = 10, **kwargs) -> Frame:
    """Subtract constant value from all pixels"""
    _require_cv2()
    subtracted_data = cv2.subtract(frame.data, np.full_like(frame.data, value, dtype=np.uint8))
    
    return Frame(
        data=subtracted_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def multiply_filter(frame: Frame, value: float = 1.1, **kwargs) -> Frame:
    """Multiply all pixels by constant"""
    multiplied_data = np.clip(frame.data.astype(np.float32) * value, 0, 255).astype(np.uint8)
    
    return Frame(
        data=multiplied_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def divide_filter(frame: Frame, value: float = 1.1, **kwargs) -> Frame:
    """Divide all pixels by constant"""
    if value == 0:
        value = 1  # Prevent division by zero
    divided_data = np.clip(frame.data.astype(np.float32) / value, 0, 255).astype(np.uint8)
    
    return Frame(
        data=divided_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def abs_filter(frame: Frame, **kwargs) -> Frame:
    """Take absolute value of all pixels"""
    abs_data = np.abs(frame.data.astype(np.int16)).astype(np.uint8)
    
    return Frame(
        data=abs_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def square_filter(frame: Frame, **kwargs) -> Frame:
    """Square all pixel values"""
    squared_data = np.clip((frame.data.astype(np.float32) / 255.0) ** 2 * 255, 0, 255).astype(np.uint8)
    
    return Frame(
        data=squared_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def sqrt_filter(frame: Frame, **kwargs) -> Frame:
    """Take square root of all pixel values"""
    sqrt_data = np.clip(np.sqrt(frame.data.astype(np.float32) / 255.0) * 255, 0, 255).astype(np.uint8)
    
    return Frame(
        data=sqrt_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def log_filter(frame: Frame, **kwargs) -> Frame:
    """Take logarithm of all pixel values"""
    # Add 1 to avoid log(0)
    log_data = np.clip(np.log(frame.data.astype(np.float32) + 1) * 255 / np.log(256), 0, 255).astype(np.uint8)
    
    return Frame(
        data=log_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def exp_filter(frame: Frame, **kwargs) -> Frame:
    """Take exponential of all pixel values"""
    exp_data = np.clip(np.exp(frame.data.astype(np.float32) / 255.0) / np.e * 255, 0, 255).astype(np.uint8)
    
    return Frame(
        data=exp_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def power_filter(frame: Frame, power: float = 2, **kwargs) -> Frame:
    """Raise all pixels to power"""
    power_data = np.clip((frame.data.astype(np.float32) / 255.0) ** power * 255, 0, 255).astype(np.uint8)
    
    return Frame(
        data=power_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Statistical operations
def mean_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Apply mean filter"""
    _require_cv2()
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
    filtered_data = cv2.filter2D(frame.data, -1, kernel)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def min_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Apply minimum filter"""
    _require_cv2()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    filtered_data = cv2.erode(frame.data, kernel)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def max_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Apply maximum filter"""
    _require_cv2()
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    filtered_data = cv2.dilate(frame.data, kernel)
    
    return Frame(
        data=filtered_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def variance_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Calculate local variance"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY).astype(np.float32)
    else:
        gray_data = frame.data.astype(np.float32)
    
    # Calculate local mean and variance
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
    mean = cv2.filter2D(gray_data, -1, kernel)
    sqr_mean = cv2.filter2D(gray_data**2, -1, kernel)
    variance = sqr_mean - mean**2
    variance_data = np.clip(variance, 0, 255).astype(np.uint8)
    
    return Frame(
        data=variance_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def std_filter(frame: Frame, kernel_size: int = 5, **kwargs) -> Frame:
    """Calculate local standard deviation"""
    variance_frame = variance_filter(frame, kernel_size, **kwargs)
    std_data = np.sqrt(variance_frame.data.astype(np.float32)).astype(np.uint8)
    
    return Frame(
        data=std_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Noise and distortion
def gaussian_noise_filter(frame: Frame, mean: float = 0, std: float = 25, **kwargs) -> Frame:
    """Add Gaussian noise"""
    noise = np.random.normal(mean, std, frame.data.shape).astype(np.float32)
    noisy_data = np.clip(frame.data.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    return Frame(
        data=noisy_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def salt_pepper_filter(frame: Frame, amount: float = 0.05, **kwargs) -> Frame:
    """Add salt and pepper noise"""
    noisy_data = frame.data.copy()
    
    # Salt noise
    num_salt = np.ceil(amount * frame.data.size * 0.5).astype(int)
    coords = [np.random.randint(0, i - 1, num_salt) for i in frame.data.shape]
    noisy_data[coords[0], coords[1]] = 255
    
    # Pepper noise
    num_pepper = np.ceil(amount * frame.data.size * 0.5).astype(int)
    coords = [np.random.randint(0, i - 1, num_pepper) for i in frame.data.shape]
    noisy_data[coords[0], coords[1]] = 0
    
    return Frame(
        data=noisy_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def speckle_filter(frame: Frame, variance: float = 0.1, **kwargs) -> Frame:
    """Add speckle noise"""
    noise = np.random.randn(*frame.data.shape) * variance
    noisy_data = np.clip(frame.data.astype(np.float32) + frame.data.astype(np.float32) * noise, 0, 255).astype(np.uint8)
    
    return Frame(
        data=noisy_data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Feature detection
def hough_lines_filter(frame: Frame, rho: float = 1, theta: float = np.pi/180, threshold: int = 100, **kwargs) -> Frame:
    """Detect lines using Hough transform"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    # Apply edge detection first
    edges = cv2.Canny(gray_data, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, rho, theta, threshold)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw lines
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(output_data, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def hough_circles_filter(frame: Frame, dp: float = 1, min_dist: int = 50, param1: int = 100, param2: int = 30, **kwargs) -> Frame:
    """Detect circles using Hough transform"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    circles = cv2.HoughCircles(gray_data, cv2.HOUGH_GRADIENT, dp, min_dist, param1=param1, param2=param2)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw circles
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(output_data, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output_data, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def sift_filter(frame: Frame, **kwargs) -> Frame:
    """SIFT feature detection"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    try:
        sift = cv2.SIFT_create()
        keypoints, descriptors = sift.detectAndCompute(gray_data, None)
        
        # Create output frame
        if frame.format == FrameFormat.GRAY:
            output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
        else:
            output_data = frame.data.copy()
        
        # Draw keypoints
        output_data = cv2.drawKeypoints(output_data, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    except AttributeError:
        # SIFT not available, return original frame
        output_data = frame.data.copy() if frame.format != FrameFormat.GRAY else cv2.cvtColor(frame.data, cv2.COLOR_GRAY2BGR)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def surf_filter(frame: Frame, **kwargs) -> Frame:
    """SURF feature detection"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    try:
        surf = cv2.xfeatures2d.SURF_create(400)
        keypoints, descriptors = surf.detectAndCompute(gray_data, None)
        
        # Create output frame
        if frame.format == FrameFormat.GRAY:
            output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
        else:
            output_data = frame.data.copy()
        
        # Draw keypoints
        output_data = cv2.drawKeypoints(output_data, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    except (AttributeError, cv2.error):
        # SURF not available, return original frame
        output_data = frame.data.copy() if frame.format != FrameFormat.GRAY else cv2.cvtColor(frame.data, cv2.COLOR_GRAY2BGR)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def orb_filter(frame: Frame, **kwargs) -> Frame:
    """ORB feature detection"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(gray_data, None)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw keypoints
    output_data = cv2.drawKeypoints(output_data, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def fast_filter(frame: Frame, threshold: int = 10, **kwargs) -> Frame:
    """FAST corner detection"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    fast = cv2.FastFeatureDetector_create(threshold)
    keypoints = fast.detect(gray_data, None)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw keypoints
    output_data = cv2.drawKeypoints(output_data, keypoints, None, color=(255, 0, 0))
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def brief_filter(frame: Frame, **kwargs) -> Frame:
    """BRIEF feature description"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    # First detect keypoints using FAST
    fast = cv2.FastFeatureDetector_create()
    keypoints = fast.detect(gray_data, None)
    
    try:
        brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
        keypoints, descriptors = brief.compute(gray_data, keypoints)
    except (AttributeError, cv2.error):
        # BRIEF not available, use ORB instead
        orb = cv2.ORB_create()
        keypoints, descriptors = orb.compute(gray_data, keypoints)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw keypoints
    output_data = cv2.drawKeypoints(output_data, keypoints, None, color=(0, 255, 0))
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def template_match_filter(frame: Frame, template: str = "", method: str = "TM_CCOEFF_NORMED", **kwargs) -> Frame:
    """Template matching"""
    _require_cv2()
    if not template:
        return frame  # No template provided
    
    try:
        template_img = cv2.imread(template, 0)
        if template_img is None:
            return frame
    except:
        return frame
    
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    # Template matching
    method_dict = {
        'TM_CCOEFF': cv2.TM_CCOEFF,
        'TM_CCOEFF_NORMED': cv2.TM_CCOEFF_NORMED,
        'TM_CCORR': cv2.TM_CCORR,
        'TM_CCORR_NORMED': cv2.TM_CCORR_NORMED,
        'TM_SQDIFF': cv2.TM_SQDIFF,
        'TM_SQDIFF_NORMED': cv2.TM_SQDIFF_NORMED
    }
    
    cv_method = method_dict.get(method, cv2.TM_CCOEFF_NORMED)
    result = cv2.matchTemplate(gray_data, template_img, cv_method)
    
    # Find best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Create output frame
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    # Draw rectangle around match
    h, w = template_img.shape
    if cv_method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(output_data, top_left, bottom_right, (0, 255, 0), 2)
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Segmentation
def watershed_filter(frame: Frame, **kwargs) -> Frame:
    """Watershed segmentation"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    # Apply threshold
    ret, thresh = cv2.threshold(gray_data, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Remove noise
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    
    # Sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    
    # Unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1
    
    # Mark the region of unknown with zero
    markers[unknown == 255] = 0
    
    # Apply watershed
    if frame.format == FrameFormat.GRAY:
        output_data = cv2.cvtColor(gray_data, cv2.COLOR_GRAY2BGR)
    else:
        output_data = frame.data.copy()
    
    markers = cv2.watershed(output_data, markers)
    output_data[markers == -1] = [255, 0, 0]
    
    return Frame(
        data=output_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def kmeans_filter(frame: Frame, k: int = 3, **kwargs) -> Frame:
    """K-means clustering segmentation"""
    _require_cv2()
    # Reshape data for K-means
    data = frame.data.reshape((-1, frame.channels))
    data = np.float32(data)
    
    # Define criteria and apply K-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Convert back to uint8 and reshape
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(frame.data.shape)
    
    return Frame(
        data=result,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def region_growing_filter(frame: Frame, threshold: int = 10, **kwargs) -> Frame:
    """Region growing segmentation"""
    _require_cv2()
    # Convert to grayscale if needed
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    # Simple region growing from center
    visited = np.zeros_like(gray_data, dtype=bool)
    segmented = np.zeros_like(gray_data)
    
    h, w = gray_data.shape
    seed = (h // 2, w // 2)
    seed_value = gray_data[seed]
    
    stack = [seed]
    region_value = 255
    
    while stack:
        x, y = stack.pop()
        if visited[x, y]:
            continue
        
        if abs(int(gray_data[x, y]) - int(seed_value)) <= threshold:
            visited[x, y] = True
            segmented[x, y] = region_value
            
            # Add neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < h and 0 <= ny < w and not visited[nx, ny]:
                    stack.append((nx, ny))
    
    return Frame(
        data=segmented,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Additional source functions
def solid_color_source(frame: Optional[Frame], width: int = 640, height: int = 480, color: list = None, **kwargs) -> Frame:
    """Generate solid color frames"""
    if color is None:
        color = [0, 0, 0]  # Black by default
    
    # Ensure color has 3 components
    if len(color) < 3:
        color = color + [0] * (3 - len(color))
    
    # Create solid color frame
    frame_data = np.full((height, width, 3), color, dtype=np.uint8)
    
    return Frame(
        data=frame_data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


def random_noise_source(frame: Optional[Frame], width: int = 640, height: int = 480, noise_type: str = "uniform", **kwargs) -> Frame:
    """Generate random noise frames"""
    if noise_type == "gaussian":
        frame_data = np.random.normal(128, 50, (height, width, 3))
    else:  # uniform
        frame_data = np.random.randint(0, 256, (height, width, 3))
    
    frame_data = np.clip(frame_data, 0, 255).astype(np.uint8)
    
    return Frame(
        data=frame_data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


def image_loader_source(frame: Optional[Frame], filename: str = "", **kwargs) -> Optional[Frame]:
    """Load static image as continuous frames"""
    _require_cv2()
    if not filename:
        return None
    
    try:
        frame_data = cv2.imread(filename)
        if frame_data is None:
            return None
        
        height, width = frame_data.shape[:2]
        return Frame(
            data=frame_data,
            format=FrameFormat.BGR,
            width=width,
            height=height,
            timestamp=time.time()
        )
    except:
        return None


def mandelbrot_source(frame: Optional[Frame], width: int = 640, height: int = 480, 
                     zoom: float = 1.0, center_x: float = -0.5, center_y: float = 0.0, **kwargs) -> Frame:
    """Generate Mandelbrot fractal"""
    # Create coordinate matrices
    x = np.linspace(center_x - 2/zoom, center_x + 2/zoom, width)
    y = np.linspace(center_y - 2/zoom, center_y + 2/zoom, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    
    # Calculate Mandelbrot set
    Z = np.zeros_like(C)
    M = np.zeros(C.shape)
    
    for i in range(256):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + C[mask]
        M[mask] = i
    
    # Convert to color
    M = (M * 255 / M.max()).astype(np.uint8)
    frame_data = cv2.applyColorMap(M, cv2.COLORMAP_HOT)
    
    return Frame(
        data=frame_data,
        format=FrameFormat.BGR,
        width=width,
        height=height,
        timestamp=time.time()
    )


# Additional sink functions for comprehensive library
def csv_export_sink(frame: Frame, filename: str = "stats.csv", **kwargs) -> bool:
    """Export frame statistics to CSV"""
    import csv
    import os
    
    stats = {
        'timestamp': frame.timestamp,
        'width': frame.width,
        'height': frame.height,
        'format': frame.format.value,
        'mean': float(np.mean(frame.data)),
        'std': float(np.std(frame.data)),
        'min': int(np.min(frame.data)),
        'max': int(np.max(frame.data))
    }
    
    file_exists = os.path.exists(filename)
    
    try:
        with open(filename, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=stats.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(stats)
        return True
    except:
        return False


def json_export_sink(frame: Frame, filename: str = "metadata.json", **kwargs) -> bool:
    """Export frame metadata to JSON"""
    import json
    
    metadata = {
        'timestamp': frame.timestamp,
        'width': frame.width,
        'height': frame.height,
        'format': frame.format.value,
        'metadata': frame.metadata
    }
    
    try:
        with open(filename, 'w') as jsonfile:
            json.dump(metadata, jsonfile, indent=2)
        return True
    except:
        return False


def histogram_sink(frame: Frame, window_name: str = "Histogram", **kwargs) -> bool:
    """Display live histogram"""
    _require_cv2()
    
    if frame.format == FrameFormat.GRAY:
        hist = cv2.calcHist([frame.data], [0], None, [256], [0, 256])
        hist_img = np.zeros((400, 512, 3), dtype=np.uint8)
        hist = cv2.normalize(hist, hist, 0, 400, cv2.NORM_MINMAX)
        
        for i in range(256):
            h = int(hist[i])
            cv2.rectangle(hist_img, (i*2, 400), (i*2+2, 400-h), (255, 255, 255), -1)
    else:
        hist_img = np.zeros((400, 512, 3), dtype=np.uint8)
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        for i, color in enumerate(colors):
            hist = cv2.calcHist([frame.data], [i], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist, 0, 400, cv2.NORM_MINMAX)
            
            for j in range(256):
                h = int(hist[j])
                cv2.rectangle(hist_img, (j*2, 400), (j*2+2, 400-h), color, -1)
    
    cv2.imshow(window_name, hist_img)
    return cv2.waitKey(1) & 0xFF != ord('q')


# Comprehensive set of processing functions
def invert_filter(frame: Frame, **kwargs) -> Frame:
    """Invert colors"""
    return Frame(
        data=255 - frame.data,
        format=frame.format,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def sepia_filter(frame: Frame, **kwargs) -> Frame:
    """Apply sepia tone effect"""
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                            [0.349, 0.686, 0.168],
                            [0.393, 0.769, 0.189]])
    
    if frame.format == FrameFormat.GRAY:
        bgr_data = cv2.cvtColor(frame.data, cv2.COLOR_GRAY2BGR)
    else:
        bgr_data = frame.data
    
    sepia_data = np.dot(bgr_data, sepia_matrix.T)
    sepia_data = np.clip(sepia_data, 0, 255).astype(np.uint8)
    
    return Frame(
        data=sepia_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def black_white_filter(frame: Frame, threshold: int = 127, **kwargs) -> Frame:
    """Convert to black and white with threshold"""
    _require_cv2()
    if frame.format != FrameFormat.GRAY:
        gray_data = cv2.cvtColor(frame.data, cv2.COLOR_BGR2GRAY)
    else:
        gray_data = frame.data
    
    _, bw_data = cv2.threshold(gray_data, threshold, 255, cv2.THRESH_BINARY)
    
    return Frame(
        data=bw_data,
        format=FrameFormat.GRAY,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


def vintage_filter(frame: Frame, **kwargs) -> Frame:
    """Apply vintage effect"""
    _require_cv2()
    sepia_frame = sepia_filter(frame)
    noise = np.random.normal(0, 25, sepia_frame.data.shape).astype(np.float32)
    vintage_data = np.clip(sepia_frame.data.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    hsv_data = cv2.cvtColor(vintage_data, cv2.COLOR_BGR2HSV)
    hsv_data[:, :, 1] = hsv_data[:, :, 1] * 0.6
    vintage_data = cv2.cvtColor(hsv_data, cv2.COLOR_HSV2BGR)
    
    return Frame(
        data=vintage_data,
        format=FrameFormat.BGR,
        width=frame.width,
        height=frame.height,
        timestamp=frame.timestamp,
        metadata=frame.metadata.copy()
    )


# Additional stub functions (implementations can be expanded as needed)
def cartoon_filter(frame: Frame, **kwargs) -> Frame: return frame
def sketch_filter(frame: Frame, **kwargs) -> Frame: return frame  
def thermal_filter(frame: Frame, **kwargs) -> Frame: return frame
def night_vision_filter(frame: Frame, **kwargs) -> Frame: return frame
def xray_filter(frame: Frame, **kwargs) -> Frame: return frame
def polaroid_filter(frame: Frame, **kwargs) -> Frame: return frame
def cross_process_filter(frame: Frame, **kwargs) -> Frame: return frame
def lomo_filter(frame: Frame, **kwargs) -> Frame: return frame
def vignette_filter(frame: Frame, strength: float = 0.5, **kwargs) -> Frame: return frame
def fisheye_filter(frame: Frame, **kwargs) -> Frame: return frame
def barrel_filter(frame: Frame, strength: float = 0.1, **kwargs) -> Frame: return frame
def pinch_filter(frame: Frame, strength: float = 0.5, **kwargs) -> Frame: return frame
def swirl_filter(frame: Frame, angle: float = 45, **kwargs) -> Frame: return frame
def mirror_h_filter(frame: Frame, **kwargs) -> Frame: return frame
def mirror_v_filter(frame: Frame, **kwargs) -> Frame: return frame
def kaleidoscope_filter(frame: Frame, segments: int = 6, **kwargs) -> Frame: return frame
def pixelate_filter(frame: Frame, block_size: int = 10, **kwargs) -> Frame: return frame
def mosaic_filter(frame: Frame, tile_size: int = 20, **kwargs) -> Frame: return frame
def oil_painting_filter(frame: Frame, **kwargs) -> Frame: return frame
def watercolor_filter(frame: Frame, **kwargs) -> Frame: return frame
def posterize_filter(frame: Frame, levels: int = 4, **kwargs) -> Frame: return frame
def solarize_filter(frame: Frame, threshold: int = 128, **kwargs) -> Frame: return frame
def duotone_filter(frame: Frame, color1: list = None, color2: list = None, **kwargs) -> Frame: return frame
def tritone_filter(frame: Frame, color1: list = None, color2: list = None, color3: list = None, **kwargs) -> Frame: return frame
def color_replace_filter(frame: Frame, target_color: list = None, replacement_color: list = None, tolerance: int = 50, **kwargs) -> Frame: return frame
def color_enhance_filter(frame: Frame, target_color: list = None, enhancement: float = 1.5, **kwargs) -> Frame: return frame
def white_balance_filter(frame: Frame, **kwargs) -> Frame: return frame
def exposure_filter(frame: Frame, stops: float = 0, **kwargs) -> Frame: return frame
def shadows_highlights_filter(frame: Frame, shadows: int = 0, highlights: int = 0, **kwargs) -> Frame: return frame
def vibrance_filter(frame: Frame, vibrance: int = 0, **kwargs) -> Frame: return frame
def clarity_filter(frame: Frame, amount: float = 0.5, **kwargs) -> Frame: return frame
def dehaze_filter(frame: Frame, **kwargs) -> Frame: return frame
def denoise_filter(frame: Frame, strength: float = 10, **kwargs) -> Frame: return frame
def unsharp_mask_filter(frame: Frame, amount: float = 1.0, radius: float = 1.0, threshold: int = 0, **kwargs) -> Frame: return frame
def tilt_shift_filter(frame: Frame, focus_y: float = 0.5, **kwargs) -> Frame: return frame
def depth_of_field_filter(frame: Frame, focus_distance: float = 0.5, blur_amount: int = 5, **kwargs) -> Frame: return frame
def motion_blur_filter(frame: Frame, angle: float = 0, distance: int = 15, **kwargs) -> Frame: return frame
def radial_blur_filter(frame: Frame, center_x: float = 0.5, center_y: float = 0.5, amount: int = 10, **kwargs) -> Frame: return frame
def zoom_blur_filter(frame: Frame, amount: int = 10, **kwargs) -> Frame: return frame
def chromatic_aberration_filter(frame: Frame, strength: int = 2, **kwargs) -> Frame: return frame
def lens_distortion_filter(frame: Frame, amount: float = 0.1, **kwargs) -> Frame: return frame
def film_grain_filter(frame: Frame, intensity: float = 0.1, **kwargs) -> Frame: return frame
def color_grading_filter(frame: Frame, shadows: list = None, midtones: list = None, highlights: list = None, **kwargs) -> Frame: return frame