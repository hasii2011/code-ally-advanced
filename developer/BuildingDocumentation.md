# Building and Viewing Documentation Locally

This guide explains how to build and view the Sphinx documentation locally for `code-ally-advanced`.

---

## Prerequisites

Ensure you have activated the root virtual environment:

```bash
source pyenv-3.13.9/bin/activate
```

Alternatively, you can run commands directly using `pyenv-3.13.9/bin/` (e.g., `pyenv-3.13.9/bin/sphinx-build`).

---

## Step 1: Install Documentation Dependencies

Install the `docs` optional dependency group defined in `pyproject.toml`:

```bash
pip install -e .[docs]
```

This installs:
* `sphinx`
* `sphinx-rtd-theme` (Read the Docs theme)
* `sphinx-autoapi` (automatic API reference generation from `src/codeallyadvanced`)

---

## Step 2: Build the HTML Documentation

Run `sphinx-build` to generate static HTML from `docs/` into `docs/build/html`:

```bash
sphinx-build -b html docs docs/build/html
```

`sphinx-autoapi` will automatically scan `src/codeallyadvanced` and generate full API documentation pages.

---

## Step 3: View in Your Browser

### Option A: Open directly
Open the generated `index.html` in your default macOS browser:

```bash
open docs/build/html/index.html
```

### Option B: Local HTTP Server
Run Python's built-in HTTP server to browse the documentation locally:

```bash
python -m http.server --directory docs/build/html 8000
```

Then visit [http://localhost:8000](http://localhost:8000) in your web browser.

---

## Step 4: Cleanup Builds

To wipe the generated documentation cache and build clean:

```bash
rm -rf docs/build docs/autoapi
sphinx-build -b html docs docs/build/html
```
