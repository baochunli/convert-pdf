# PDF Converter

This shows how we can convert a PDF file using Docling, Apple Silicon GPU, and the Granite Docling model, with mathematical formulas converted to LaTeX.

## Quick Start

To prepare the Python virtual environment:

```bash
cd convert-pdf
uv sync
source .venv/bin/activate
```

Run a single PDF:

```bash
docling --enrich-formula --pipeline vlm --vlm-model granite_docling file.pdf
```
