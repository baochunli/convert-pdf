# PDF Converter

This project is a small Python wrapper around `opendataloader-pdf` for converting PDFs with the need of GPUs, including mathematical formulas into LaTeX.

The main entry point is:

```bash
uv run convert.py file.pdf
```

## Fresh Install

From a new machine or shell session where `.venv` does not exist yet and
`opendataloader_pdf` is not installed, use these commands:

```bash
git clone <repo-url> pdfs
cd pdfs
brew install uv openjdk@17
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
export PATH="$JAVA_HOME/bin:$PATH"
uv sync
source .venv/bin/activate
```

If Java is already installed and on `PATH`, skip the `brew install` and
`JAVA_HOME` lines.

`uv sync` creates `.venv` and installs the `opendataloader-pdf` Python package
that provides `opendataloader_pdf`.

This script:

- Starts the hybrid backend automatically.
- Waits for the backend health check to come up.
- Runs conversion in `hybrid` mode with `hybrid_mode="full"`.
- Enables formula enrichment by default.
- Uses Java fallback by default if the hybrid backend fails.
- Stops the backend when the conversion finishes or errors out.

## Requirements

- Python 3.10+
- `uv`
- Java 11+
- The `opendataloader-pdf` dependency installed through the project environment

If you are working inside the repo directly, activate the local environment first when needed:

```bash
source .venv/bin/activate
```

With `uv`, you can usually skip manual activation and run the script directly.

## Quick Start

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

## Formula Enrichment

Formula enrichment is enabled by default:

```bash
uv run convert.py file.pdf
```

Use `--no-enrich-formula` if you want to turn it off.

This matters because formula extraction runs on the backend, not in the local Java-only path.

## Command-Line Options

### Required input

- `input_paths`: One or more PDF files and/or folders.

### Output options

- `-o, --output-dir`: Output directory. Default: `./`
- `-f, --format`: Output format. Default: `markdown`

### Hybrid options

- `--enrich-formula`: Enable formula enrichment on the backend. Default: on.
- `--no-enrich-formula`: Disable formula enrichment.
- `--hybrid-timeout`: Hybrid backend read timeout in milliseconds. Default: `180000`.
- `--hybrid-fallback`: Enable Java fallback if the hybrid backend fails. This is on by default.
- `--no-hybrid-fallback`: Disable Java fallback.
- `--backend-startup-timeout`: Seconds to wait for the backend health check. Default: `120`.

## More examples

Convert one PDF without formula enrichment:

```bash
uv run convert.py --no-enrich-formula file.pdf
```

Convert several PDFs with formula enrichment:

```bash
uv run convert.py file1.pdf file2.pdf file3.pdf
```

Convert a folder:

```bash
uv run convert.py papers/
```

Use a longer read timeout for large or slow documents:

```bash
uv run convert.py --hybrid-timeout 300000 file.pdf
```

Disable fallback if you want failures to stop immediately:

```bash
uv run convert.py --no-hybrid-fallback file.pdf
```

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
