# VidPipe Language Reference

This document summarises the pipeline syntax, file formats, and built-in operations available in VidPipe. It replaces the
previous README fragments and examples write-ups so the language can evolve in a single place.

## Pipeline building blocks

### Operators

- `->` — sequential composition of nodes (default queue size 10, asynchronous via `~>` in pipeline files)
- `|` — parallel fan-out with an implicit merge into the downstream node
- `()` — explicit grouping for nested expressions
- `pipeline name = ...` — define a reusable pipeline segment
- `name` — reference a previously defined pipeline or function
- `@ <duration>s` — run the preceding segment for a fixed number of seconds
- `with (param: value, ...)` — provide parameters to a function call

### Example

```python
pipeline preprocess = webcam with (camera_id: 0) -> brightness with (brightness: 20)
pipeline detect = grayscale -> edges -> contours with (min_area: 200)

preprocess @ 3s -> detect -> display with (window_name: "Analysis")
```

## Multi-pipeline files

Multi-pipeline files (used by `python main.py --multi <file>`) describe timed sequences followed by optional parallel blocks.
Each pipeline block begins with `--pipeline` and an optional duration suffix (`5s`). Use `--parallel` to start a parallel section
and `--end` to finish it.

```text
--pipeline 5s intro
webcam -> display

--pipeline review
webcam -> grayscale -> edges -> display

--parallel

--pipeline stream1
webcam -> display with (window_name: "Stream 1")

--pipeline stream2
webcam -> edges -> display with (window_name: "Stream 2")

--end
```

While the pipelines run the command-line driver owns the OpenCV display loop: close a window or press `q` to stop all active
pipelines.

## Function library

Metadata used by both the runtime and GUI lives in the shared function registry. The table below lists the shipped operations
and their notable parameters.

### Sources

| Name | Description | Parameters |
| --- | --- | --- |
| `webcam` | Capture frames from the default camera. | `camera_id` — Device index (default `0`). |
| `camera` | Alias of `webcam`. | `device` — Device index (default `0`). |
| `capture` | Read frames from a video file. | `filename` — Path to video source. |
| `test-pattern` | Generate synthetic test images. | `width`, `height`, `pattern` (`checkerboard`, `gradient`, ...). |
| `solid-color` | Generate solid color frames. | `width`, `height`, `color` — [B,G,R] color values. |
| `random-noise` | Generate random noise frames. | `width`, `height`, `noise_type` (`uniform`, `gaussian`). |
| `image-loader` | Load static image as continuous frames. | `filename` — Image file path. |
| `mandelbrot` | Generate Mandelbrot fractal. | `width`, `height`, `zoom`, `center_x`, `center_y`. |

### Processors

**Basic Image Processing:**
| Name | Description | Parameters |
| --- | --- | --- |
| `grayscale` / `gray` | Convert to grayscale. | — |
| `blur` | Gaussian blur. | `kernel_size`, `sigma`. |
| `edges` | Canny edge detection. | `low_threshold`, `high_threshold`. |
| `threshold` | Binary thresholding. | `threshold`, `max_val`. |
| `resize` | Resize frame. | `width`, `height`, `scale`. |
| `flip` | Horizontal and/or vertical flip. | `horizontal`, `vertical`. |
| `rotate` | Rotate image. | `angle` in degrees. |
| `crop` | Crop to region of interest. | `x`, `y`, `width`, `height`. |
| `brightness` | Adjust brightness. | `brightness` in range `-100..100`. |
| `contrast` | Adjust contrast. | `contrast` in range `-100..100`. |
| `hue` | Hue shift. | `hue` in degrees. |
| `saturation` | Adjust saturation. | `saturation` in range `-100..100`. |
| `gamma` | Gamma correction. | `gamma` (0.1–3.0). |
| `histogram-eq` | Histogram equalisation. | — |
| `morphology` | Morphological operations. | `operation` (`open`, `close`, `erode`, `dilate`), `kernel_size`. |
| `contours` | Find and draw contours. | `min_area`. |
| `corners` | Harris corner detection. | `max_corners`, `quality`, `min_distance`. |
| `optical-flow` | Dense optical flow visualisation. | — |

**Advanced Filters:**
| Name | Description | Parameters |
| --- | --- | --- |
| `sharpen` | Apply sharpening filter. | — |
| `emboss` | Apply emboss effect. | — |
| `median` | Apply median filter. | `kernel_size`. |
| `bilateral` | Apply bilateral filter. | `d`, `sigma_color`, `sigma_space`. |
| `gaussian` | Apply Gaussian filter. | `kernel_size`, `sigma_x`, `sigma_y`. |
| `laplacian` | Apply Laplacian edge detection. | — |
| `sobel-x` / `sobel-y` | Apply Sobel gradient filters. | — |
| `scharr-x` / `scharr-y` | Apply Scharr gradient filters. | — |

**Color Space Conversions:**
| Name | Description | Parameters |
| --- | --- | --- |
| `bgr2rgb` / `rgb2bgr` | Convert between BGR and RGB. | — |
| `bgr2hsv` / `hsv2bgr` | Convert between BGR and HSV. | — |
| `bgr2lab` / `lab2bgr` | Convert between BGR and LAB. | — |
| `bgr2yuv` / `yuv2bgr` | Convert between BGR and YUV. | — |

**Geometric Transformations:**
| Name | Description | Parameters |
| --- | --- | --- |
| `translate` | Translate (move) image. | `x`, `y`. |
| `scale` | Scale image. | `scale_x`, `scale_y`. |
| `shear` | Apply shear transformation. | `shear_x`, `shear_y`. |
| `perspective` | Apply perspective transformation. | `matrix`. |
| `affine` | Apply affine transformation. | `matrix`. |

**Mathematical Operations:**
| Name | Description | Parameters |
| --- | --- | --- |
| `add` / `subtract` | Add/subtract constant values. | `value`. |
| `multiply` / `divide` | Multiply/divide by constant. | `value`. |
| `abs` / `square` / `sqrt` | Mathematical operations. | — |
| `log` / `exp` / `power` | Logarithmic and exponential operations. | `power` (for power function). |

**Statistical Filters:**
| Name | Description | Parameters |
| --- | --- | --- |
| `mean` / `min` / `max` | Statistical filters. | `kernel_size`. |
| `variance` / `std` | Calculate local variance/standard deviation. | `kernel_size`. |

**Noise and Distortion:**
| Name | Description | Parameters |
| --- | --- | --- |
| `gaussian-noise` | Add Gaussian noise. | `mean`, `std`. |
| `salt-pepper` | Add salt and pepper noise. | `amount`. |
| `speckle` | Add speckle noise. | `variance`. |

**Feature Detection:**
| Name | Description | Parameters |
| --- | --- | --- |
| `hough-lines` | Detect lines using Hough transform. | `rho`, `theta`, `threshold`. |
| `hough-circles` | Detect circles using Hough transform. | `dp`, `min_dist`, `param1`, `param2`. |
| `sift` / `surf` / `orb` | Feature detection algorithms. | — |
| `fast` | FAST corner detection. | `threshold`. |
| `brief` | BRIEF feature description. | — |

**Special Effects:**
| Name | Description | Parameters |
| --- | --- | --- |
| `invert` | Invert colors. | — |
| `sepia` | Apply sepia tone effect. | — |
| `black-white` | Convert to black and white. | `threshold`. |
| `vintage` | Apply vintage effect. | — |
| `cartoon` | Apply cartoon effect. | — |
| `sketch` | Convert to pencil sketch. | — |
| `thermal` | Apply thermal vision effect. | — |
| `night-vision` | Apply night vision effect. | — |
| `x-ray` | Apply X-ray effect. | — |
| `polaroid` | Apply Polaroid effect. | — |
| `cross-process` | Apply cross-processing effect. | — |
| `lomo` | Apply lomography effect. | — |
| `vignette` | Apply vignette effect. | `strength`. |
| `fisheye` | Apply fisheye distortion. | — |
| `barrel` | Apply barrel distortion. | `strength`. |
| `pinch` | Apply pinch distortion. | `strength`. |
| `swirl` | Apply swirl distortion. | `angle`. |
| `mirror-horizontal` / `mirror-vertical` | Mirror effects. | — |
| `kaleidoscope` | Apply kaleidoscope effect. | `segments`. |
| `pixelate` | Apply pixelation effect. | `block_size`. |
| `mosaic` | Apply mosaic effect. | `tile_size`. |
| `oil-painting` | Apply oil painting effect. | — |
| `watercolor` | Apply watercolor effect. | — |
| `posterize` | Apply posterization. | `levels`. |
| `solarize` | Apply solarization effect. | `threshold`. |

**Color Grading:**
| Name | Description | Parameters |
| --- | --- | --- |
| `duotone` | Apply duotone effect. | `color1`, `color2`. |
| `tritone` | Apply tritone effect. | `color1`, `color2`, `color3`. |
| `color-replace` | Replace specific color. | `target_color`, `replacement_color`, `tolerance`. |
| `color-enhance` | Enhance specific color. | `target_color`, `enhancement`. |
| `white-balance` | Auto white balance correction. | — |
| `exposure` | Adjust exposure. | `stops`. |
| `shadows-highlights` | Adjust shadows and highlights. | `shadows`, `highlights`. |
| `vibrance` | Adjust vibrance. | `vibrance`. |
| `clarity` | Adjust clarity/structure. | `amount`. |
| `dehaze` | Remove atmospheric haze. | — |

**Advanced Effects:**
| Name | Description | Parameters |
| --- | --- | --- |
| `denoise` | Reduce noise. | `strength`. |
| `unsharp-mask` | Apply unsharp mask sharpening. | `amount`, `radius`, `threshold`. |
| `tilt-shift` | Apply tilt-shift effect. | `focus_y`. |
| `depth-of-field` | Simulate depth of field. | `focus_distance`, `blur_amount`. |
| `motion-blur` | Apply motion blur. | `angle`, `distance`. |
| `radial-blur` | Apply radial blur. | `center_x`, `center_y`, `amount`. |
| `zoom-blur` | Apply zoom blur. | `amount`. |
| `chromatic-aberration` | Add chromatic aberration. | `strength`. |
| `lens-distortion` | Apply lens distortion. | `amount`. |
| `film-grain` | Add film grain. | `intensity`. |
| `color-grading` | Apply color grading. | `shadows`, `midtones`, `highlights`. |

**Segmentation:**
| Name | Description | Parameters |
| --- | --- | --- |
| `watershed` | Watershed segmentation. | — |
| `kmeans` | K-means clustering segmentation. | `k`. |
| `region-growing` | Region growing segmentation. | `threshold`. |
| `template-match` | Template matching. | `template`, `method`. |

### Sinks

| Name | Description | Parameters |
| --- | --- | --- |
| `display` / `window` | Show frames in an OpenCV window. | `window_name`. |
| `save` | Save frames as images. | `filename` with optional `{timestamp}` placeholder. |
| `record` | Write frames to a video file. | `filename`, `fps`. |
| `csv-export` | Export frame statistics to CSV. | `filename` — CSV output file. |
| `json-export` | Export frame metadata to JSON. | `filename` — JSON output file. |
| `histogram-sink` | Display live histogram. | `window_name` — Histogram window name. |

Refer to the implementation in `vidpipe/functions.py` for the definitive source of function behaviour and metadata.

**Total Functions: 133** (8 sources, 118 processors, 7 sinks)
