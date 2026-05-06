# Release Notes for v0.1.2

## SSTcore v0.1.2

### Features
- Embedded 42 knot `.fseries` files directly in the C++ library
- All knots accessible via `VortexKnotSystem.initialize_knot_from_name()`
- No external `.fseries` files required for Python users

### Improvements
- Canonical Python package/API name `SSTcore`; CMake extension module remains `sstcore`
- Backwards compatibility: deprecated top-level shims `swirl_string_core` / `sstbindings` still ship as thin re-exports
- Optimized C++20 build configuration for better compatibility
- Added Linux compiler flags for cross-platform builds

### Supported Platforms
- Windows: Python 3.9, 3.10, 3.11, 3.12, 3.13
- Linux: Build from source (wheels coming soon)
- macOS: Build from source (wheels coming soon)

### Installation
```bash
pip install SSTcore
```

### Usage
```python
import SSTcore
from SSTcore import VortexKnotSystem

# Initialize any embedded knot
system = VortexKnotSystem()
system.initialize_knot_from_name('3_1', resolution=1000)  # Trefoil
positions = system.get_positions()
```

### Available Knots
All knots from `src/knot_fseries/` are now built-in, including:
- 3_1 (Trefoil/Electron)
- 4_1 (Dark Knot)
- 5_1 (Muon)
- 5_2 (Up Quark)
- 6_1 (Down Quark)
- 7_1 (Tau)
- And 36 more...

### Documentation
- GitHub: https://github.com/Swirl-String-Theory/SSTcore
- PyPI: https://pypi.org/project/SSTcore/

