# PDF Converter

This project is a small Python wrapper around `opendataloader-pdf` for converting PDFs with the need of GPUs, including mathematical formulas into LaTeX.

This script:

- Starts the hybrid backend automatically.
- Waits for the backend health check to come up.
- Runs conversion in `hybrid` mode with `hybrid_mode="full"`.
- Enables formula enrichment by default.
- Uses Java fallback by default if the hybrid backend fails.
- Stops the backend when the conversion finishes or errors out.

## Quick Start

To prepare the Python virtual environment:

```bash
cd convert-pdf
uv sync
source .venv/bin/activate
uv run jar-install.py
```

Run a single PDF:

```bash
uv run convert.py file.pdf
```

Run multiple files or folders:

```bash
uv run convert.py file1.pdf file2.pdf folder/
```

Write output to a custom directory:

```bash
uv run convert.py --output-dir out file.pdf
```

Generate a different output format:

```bash
uv run convert.py --format markdown,json file.pdf
```

## What The Script Does

When you run `convert.py`, it performs these steps:

1. Finds a free localhost port.
2. Starts the hybrid backend on that port.
3. Waits for `GET /health` to return `200`.
4. Calls `opendataloader_pdf.convert(...)` with:
   - `hybrid="docling-fast"`
   - `hybrid_mode="full"`
   - `hybrid_url="http://127.0.0.1:<port>"`
   - `hybrid_timeout="180000"` by default
   - `hybrid_fallback=True` by default
5. Shuts the backend down after the conversion completes.

## Converting Mathematical Formula to LaTeX

This is enabled by default. Use `--no-enrich-formula` if you want to turn it off.

## Command-Line Options

### Required input

- `input_paths`: One or more PDF files and/or folders.

### Output options

- `-o, --output-dir`: Output directory. Default: `./`
- `-f, --format`: Output format. Default: `markdown`

### Hybrid options

- `--no-enrich-formula`: Disable formula enrichment.
- `--hybrid-timeout`: Hybrid backend read timeout in milliseconds. Default: `180000`.
- `--hybrid-fallback`: Enable Java fallback if the hybrid backend fails. This is on by default.
- `--no-hybrid-fallback`: Disable Java fallback.
- `--backend-startup-timeout`: Seconds to wait for the backend health check. Default: `120`.

## Troubleshooting

### The backend does not start

Check that Java is installed:

```bash
java -version
```

If the hybrid server binary is not on `PATH`, the script falls back to:

```bash
python -m opendataloader_pdf.hybrid_server
```

### The backend is slow

Increase the timeout:

```bash
uv run convert.py --hybrid-timeout 300000 file.pdf
```

If startup itself is slow, increase the startup timeout:

```bash
uv run convert.py --backend-startup-timeout 300 file.pdf
```
