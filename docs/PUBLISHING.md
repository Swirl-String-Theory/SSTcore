# Publishing SSTcore to PyPI

This guide walks you through publishing the `SSTcore` package to PyPI.

## Important: Python Version Compatibility

**Pybind11 extensions are compiled for specific Python versions.** A wheel built for Python 3.12 will NOT work with Python 3.11 or 3.13.

You need to build separate wheels for each Python version you want to support:
- Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Platforms: Linux, macOS, Windows

**Recommended**: Use the GitHub Actions workflow (`.github/workflows/build-wheels.yml`) to automatically build wheels for all platforms and Python versions.

See `BUILDING_WHEELS.md` for detailed instructions.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (recommended for testing): https://test.pypi.org/account/register/
3. **Build Tools**: Install required tools:
   ```bash
   pip install build twine
   ```

## Pre-Publishing Checklist

Before publishing, make sure to:

- [x] Update `setup.py` with your actual:
  - [x] Author name: Omar Iskandarani
  - [ ] Author email (optional - add if you want it public)
  - [x] Repository URL: https://github.com/Swirl-String-Theory/SSTcore
  - [ ] License information (add LICENSE file if missing)
  - [x] Project URLs
- [x] Update `pyproject.toml` with the same information
- [ ] Update version number in `setup.py` (currently `0.1.0`)
- [ ] Add a `LICENSE` file to the repository
- [ ] Ensure `Readme.md` is complete and well-formatted
- [ ] Test the build locally:
  ```bash
  python -m build
  ```
- [ ] Test installation from the built wheel:
  ```bash
  pip install dist/SSTcore-*.whl
  ```

## Step 1: Update Package Metadata

Edit `setup.py` and `pyproject.toml` to replace placeholder values:

- `author_email`: Your email address
- `url`: Your GitHub repository URL
- `license`: Your license type (MIT, Apache, etc.)

## Step 2: Build the Package

Build both source distribution and wheel:

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/SSTcore-0.1.0.tar.gz` (source distribution)
- `dist/SSTcore-0.1.0-cp3X-cp3X-*.whl` (wheel for your platform)

### Source ZIP bundle (audit / evidence)

CI and local release builds also produce a compact **`dist/SSTcore_source_vX.Y.Z.zip`** for Canon evidence and manual review. Large resource trees are nested as `resources/*.zip` (no `*.stl` meshes).

```bash
python -m build --sdist
python scripts/make_source_zip.py
# -> dist/SSTcore_source_v0.8.13.zip
```

After extracting that ZIP:

```bash
python scripts/unpack_source_resources.py
pip install -e .
python -m pytest tests/ -q
```

See [`resources/README.md`](../resources/README.md) for archive layout and exclusions. PyPI wheels already embed unpacked resources; this step is only for the source ZIP download path.

## Step 3: Test on TestPyPI (Recommended)

First, test on TestPyPI to ensure everything works:

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ SSTcore
```

## Step 4: Publish to PyPI

Once tested, publish to the real PyPI:

```bash
# Upload to PyPI
twine upload dist/*
```

You'll be prompted for your PyPI username and password. For better security, use an API token:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use the token as the password (username stays as `__token__`)

## Step 5: Verify Installation

After publishing, verify the package can be installed:

```bash
# Wait a few minutes for PyPI to process
pip install SSTcore

# Test import
python -c "import SSTcore; print('Success!')"
```

## Version Management

For future releases:

1. Update `__version__` in `setup.py`
2. Update `version` in `pyproject.toml`
3. Create a git tag: `git tag v0.1.0`
4. Build and upload: `python -m build && twine upload dist/*`

## Troubleshooting

### Build Errors

- **C++ compiler not found**: Install a C++ compiler (MSVC on Windows, GCC/Clang on Linux/Mac)
- **pybind11 not found**: `pip install pybind11`
- **Embedded files not generated**: Check that `src/knot_fseries/` exists and contains `.fseries` files

### Upload Errors

- **Package already exists**: Increment the version number
- **Authentication failed**: Check your PyPI credentials or API token
- **File too large**: PyPI has a 100MB limit per file. If your package is too large, consider:
  - Removing unnecessary files
  - Using git LFS for large data files
  - Splitting into multiple packages

## Post-Publishing

After successful publication:

1. Update your repository README with installation instructions:
   ```bash
   pip install SSTcore
   ```
2. Create a GitHub release with the version tag
3. Update documentation with PyPI badge:
   ```markdown
   [![PyPI version](https://badge.fury.io/py/SSTcore.svg)](https://badge.fury.io/py/SSTcore)
   ```

## Continuous Integration

Consider setting up GitHub Actions to automatically build and publish on tags:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [created]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

