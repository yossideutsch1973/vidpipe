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

### Processors

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

### Sinks

| Name | Description | Parameters |
| --- | --- | --- |
| `display` / `window` | Show frames in an OpenCV window. | `window_name`. |
| `save` | Save frames as images. | `filename` with optional `{timestamp}` placeholder. |
| `record` | Write frames to a video file. | `filename`, `fps`. |

Refer to the implementation in `vidpipe/functions.py` for the definitive source of function behaviour and metadata.
