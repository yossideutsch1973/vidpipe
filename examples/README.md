# VidPipe Examples

This folder contains ready-to-run `.vp` files that highlight the language features documented in
[`docs/language_reference.md`](../docs/language_reference.md).

## Categories

- **Core** — `simple.vp`, `with_parameters.vp`, and `test_pattern.vp` cover the basics of sources, processors and sinks.
- **Parallelism & orchestration** — `multi_processing.vp`, `modular_pipelines.vp`, and `comprehensive_demo.vp` demonstrate
  definitions, timing, and parallel operators. Multi-pipeline file structure is described in the language reference.
- **Advanced techniques** — Files such as `advanced_processing.vp`, `pipeline_patterns.vp`, and `real_world_apps.vp` showcase the
  richer function library.

Use the CLI to execute an example directly:

```bash
python main.py --cli --file examples/simple.vp
python main.py --cli --multi examples/comprehensive_demo.vp
```

Or launch the GUI (`python main.py --gui`) and open any file from the editor. The function browser and code completion draw on
shared metadata, so new registry entries appear automatically.
