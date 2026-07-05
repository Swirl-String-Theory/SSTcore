# Version Management

## Current Version

The package version is defined in two places:
- `setup.py`: `__version__ = "0.8.13"`
- `src/SSTcore/__init__.py`: `__version__ = "0.8.13"`

**Always update both files when changing the version!** (`pyproject.toml` has no `[project]` version; metadata lives in `setup.py`.)

## Incrementing Version

When you need to publish a new version:

1. **Update version in both files:**
   ```python
   # setup.py
   __version__ = "0.1.2"  # or 0.2.0, 1.0.0, etc.
   ```
   
   ```toml
   # pyproject.toml
   version = "0.1.2"
   ```

2. **Rebuild wheels:**
   ```bash
   # For current Python version
   python -m build --wheel
   
   # Or rebuild all versions
   python scripts/build_wheels_conda.py
   ```

3. **Build source distribution:**
   ```bash
   python -m build --sdist
   ```

4. **Upload to PyPI:**
   ```bash
   twine upload dist/*.whl dist/*.tar.gz
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Examples:
- `0.1.0` → `0.1.1` (bug fix)
- `0.1.1` → `0.2.0` (new feature)
- `0.2.0` → `1.0.0` (major release, breaking changes)

## Error: "File already exists"

If you get this error when uploading:
```
ERROR: File already exists ('SSTcore-0.1.0-...')
```

**Solution**: Increment the version number and rebuild.

**You cannot overwrite existing files on PyPI!** Each version is immutable.

## Checking Current Version on PyPI

Visit: https://pypi.org/project/SSTcore/

Or check via pip:
```bash
pip index versions SSTcore
```

## Git Tags

After publishing, create a git tag:

```bash
git tag v0.1.1
git push origin v0.1.1
```

This helps track releases and can trigger GitHub Actions workflows.

