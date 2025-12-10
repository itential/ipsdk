# Third-Party License Attributions

This document lists all third-party dependencies used in the Itential Python SDK and their respective licenses.

## Runtime Dependencies

### httpx (>=0.28.1)
- **License**: BSD-3-Clause
- **Copyright**: Copyright © 2019 Encode OSS Ltd.
- **Description**: A next-generation HTTP client for Python
- **Homepage**: https://www.python-httpx.org/
- **PyPI**: https://pypi.org/project/httpx/

#### httpx Dependencies

**anyio (4.12.0)**
- **License**: MIT
- **Description**: High level compatibility layer for multiple asynchronous event loop implementations
- **PyPI**: https://pypi.org/project/anyio/

**certifi (2025.11.12)**
- **License**: Mozilla Public License 2.0 (MPL 2.0)
- **Description**: Python package for providing Mozilla's CA Bundle
- **PyPI**: https://pypi.org/project/certifi/

**httpcore (1.0.9)**
- **License**: BSD-3-Clause
- **Description**: The HTTP Core package provides a minimal low-level HTTP client
- **PyPI**: https://pypi.org/project/httpcore/

**idna (3.11)**
- **License**: BSD-3-Clause
- **Description**: Internationalized Domain Names in Applications (IDNA)
- **PyPI**: https://pypi.org/project/idna/

**sniffio (1.3.1)**
- **License**: MIT License or Apache License 2.0
- **Description**: Sniff out which async library your code is running under
- **PyPI**: https://pypi.org/project/sniffio/

**typing-extensions (4.15.0)**
- **License**: Python Software Foundation License
- **Description**: Backported and Experimental Type Hints for Python
- **PyPI**: https://pypi.org/project/typing-extensions/

**h11 (0.16.0)**
- **License**: MIT
- **Description**: A pure-Python, bring-your-own-I/O implementation of HTTP/1.1
- **PyPI**: https://pypi.org/project/h11/

**mdurl (0.1.2)**
- **License**: MIT
- **Description**: Markdown URL utilities
- **PyPI**: https://pypi.org/project/mdurl/

## Development Dependencies

### Testing Framework

**pytest (9.0.2)**
- **License**: MIT
- **Description**: The pytest framework makes it easy to write small tests
- **PyPI**: https://pypi.org/project/pytest/

**pytest-asyncio (1.3.0)**
- **License**: Apache License 2.0
- **Description**: Pytest support for asyncio
- **PyPI**: https://pypi.org/project/pytest-asyncio/

**pytest-cov (7.0.0)**
- **License**: MIT
- **Description**: Pytest plugin for measuring coverage
- **PyPI**: https://pypi.org/project/pytest-cov/

**coverage (7.13.0)**
- **License**: Apache License 2.0
- **Description**: Code coverage measurement for Python
- **PyPI**: https://pypi.org/project/coverage/

**tox (4.32.0)**
- **License**: MIT
- **Description**: Tox is a generic virtual environment management and test command line tool
- **PyPI**: https://pypi.org/project/tox/

**tox-uv (1.29.0)**
- **License**: MIT
- **Description**: Use uv with tox for faster virtual environment management
- **PyPI**: https://pypi.org/project/tox-uv/

### Code Quality and Linting

**ruff (0.14.8)**
- **License**: MIT
- **Description**: An extremely fast Python linter and code formatter
- **PyPI**: https://pypi.org/project/ruff/

**mypy (1.19.0)**
- **License**: MIT
- **Description**: Optional static typing for Python
- **PyPI**: https://pypi.org/project/mypy/

**mypy-extensions (1.1.0)**
- **License**: MIT
- **Description**: Experimental type system extensions for programs checked with mypy
- **PyPI**: https://pypi.org/project/mypy-extensions/

### Security Analysis

**bandit (1.9.2)**
- **License**: Apache License 2.0
- **Description**: Security oriented static analyser for python code
- **PyPI**: https://pypi.org/project/bandit/

### Development Tools

**pre-commit (4.5.0)**
- **License**: MIT
- **Description**: A framework for managing and maintaining multi-language pre-commit hooks
- **PyPI**: https://pypi.org/project/pre-commit/

**build (1.3.0)**
- **License**: MIT
- **Description**: A simple, correct Python build frontend
- **PyPI**: https://pypi.org/project/build/

**q (2.7)**
- **License**: Apache License 2.0
- **Description**: Quick and dirty debugging output for tired programmers
- **PyPI**: https://pypi.org/project/q/

### Utility Dependencies

**packaging (25.0)**
- **License**: Apache License 2.0 or BSD License
- **Description**: Core utilities for Python packages
- **PyPI**: https://pypi.org/project/packaging/

**pyproject-hooks (1.2.0)**
- **License**: MIT
- **Description**: Wrappers to call pyproject.toml-based build backend hooks
- **PyPI**: https://pypi.org/project/pyproject-hooks/

**pyproject-api (1.10.0)**
- **License**: MIT
- **Description**: API to interact with the python pyproject.toml based projects
- **PyPI**: https://pypi.org/project/pyproject-api/

**pathspec (0.12.1)**
- **License**: Mozilla Public License 2.0 (MPL 2.0)
- **Description**: Utility library for gitignore style pattern matching of file paths
- **PyPI**: https://pypi.org/project/pathspec/

**pluggy (1.6.0)**
- **License**: MIT
- **Description**: Plugin and hook calling mechanisms for python
- **PyPI**: https://pypi.org/project/pluggy/

**iniconfig (2.3.0)**
- **License**: MIT
- **Description**: Brain-dead simple parsing of ini files
- **PyPI**: https://pypi.org/project/iniconfig/

**tomli (2.3.0)**
- **License**: MIT
- **Description**: A lil' TOML parser for Python
- **PyPI**: https://pypi.org/project/tomli/

**cachetools (6.2.2)**
- **License**: MIT
- **Description**: Extensible memoizing collections and decorators
- **PyPI**: https://pypi.org/project/cachetools/

**cfgv (3.5.0)**
- **License**: MIT
- **Description**: Validate configuration and produce human readable error messages
- **PyPI**: https://pypi.org/project/cfgv/

**identify (2.6.15)**
- **License**: MIT
- **Description**: File identification library for Python
- **PyPI**: https://pypi.org/project/identify/

**chardet (5.2.0)**
- **License**: LGPL-2.1
- **Description**: Universal character encoding detector for Python
- **PyPI**: https://pypi.org/project/chardet/

**colorama (0.4.6)**
- **License**: BSD-3-Clause
- **Description**: Cross-platform colored terminal text
- **PyPI**: https://pypi.org/project/colorama/

**exceptiongroup (1.3.1)**
- **License**: MIT or Apache License 2.0
- **Description**: Backport of PEP 654 (exception groups)
- **PyPI**: https://pypi.org/project/exceptiongroup/

**backports.asyncio.runner (1.2.0)**
- **License**: Python Software Foundation License (PSF-2.0)
- **Description**: Backport of Python 3.11 asyncio.Runner for older Python versions
- **PyPI**: https://pypi.org/project/backports.asyncio.runner/

**nodeenv (1.9.1)**
- **License**: BSD License
- **Description**: Node.js virtual environment builder
- **PyPI**: https://pypi.org/project/nodeenv/

**virtualenv (20.35.4)**
- **License**: MIT
- **Description**: Virtual Python Environment builder
- **PyPI**: https://pypi.org/project/virtualenv/

**distlib (0.4.0)**
- **License**: Python Software Foundation License
- **Description**: Distribution utilities for Python
- **PyPI**: https://pypi.org/project/distlib/

**filelock (3.20.0)**
- **License**: The Unlicense (Unlicense)
- **Description**: A platform independent file lock
- **PyPI**: https://pypi.org/project/filelock/

**platformdirs (4.5.1)**
- **License**: MIT
- **Description**: A small Python module for determining appropriate platform-specific dirs
- **PyPI**: https://pypi.org/project/platformdirs/

**librt (0.7.3)**
- **License**: MIT AND PSF-2.0
- **Description**: Mypyc runtime library with C implementations of Python standard library classes
- **PyPI**: https://pypi.org/project/librt/

### Bandit Dependencies

**rich (14.2.0)**
- **License**: MIT
- **Description**: Render rich text, tables, progress bars, syntax highlighting, markdown and more to the terminal
- **PyPI**: https://pypi.org/project/rich/

**markdown-it-py (4.0.0)**
- **License**: MIT
- **Description**: Python port of markdown-it
- **PyPI**: https://pypi.org/project/markdown-it-py/

**pygments (2.19.2)**
- **License**: BSD License
- **Description**: Pygments is a syntax highlighting package written in Python
- **PyPI**: https://pypi.org/project/pygments/

**pyyaml (6.0.3)**
- **License**: MIT
- **Description**: YAML parser and emitter for Python
- **PyPI**: https://pypi.org/project/pyyaml/

**stevedore (5.6.0)**
- **License**: Apache License 2.0
- **Description**: Manage dynamic plugins for Python applications
- **PyPI**: https://pypi.org/project/stevedore/

## License Categories Summary

### MIT Licensed (Most Permissive)
- anyio, sniffio, h11, mdurl, pytest, pytest-cov, ruff, mypy, mypy-extensions
- pre-commit, build, pyproject-hooks, pyproject-api, pluggy, iniconfig, cfgv, identify
- virtualenv, platformdirs, rich, markdown-it-py, pyyaml, tox, tox-uv, tomli, cachetools

### BSD Licensed
- httpx (BSD-3-Clause), httpcore (BSD-3-Clause), idna (BSD-3-Clause)
- nodeenv (BSD License), pygments (BSD License), colorama (BSD-3-Clause)

### Apache License 2.0
- pytest-asyncio, coverage, bandit, q, packaging (dual), stevedore

### Mozilla Public License 2.0 (MPL 2.0)
- certifi, pathspec

### Python Software Foundation License
- typing-extensions, distlib, backports.asyncio.runner (PSF-2.0)

### The Unlicense
- filelock

### LGPL-2.1
- chardet

### Dual Licensed (MIT or Apache 2.0)
- sniffio (MIT or Apache 2.0), exceptiongroup (MIT or Apache 2.0)

### Multiple Licenses
- librt (MIT AND PSF-2.0)

## Compatibility

All dependencies are compatible with the GPL-3.0-or-later license used by the Itential Python SDK. The GPL-3.0-or-later license allows linking with libraries under more permissive licenses (MIT, BSD, Apache 2.0, etc.) without restriction. The GPL-3.0-or-later is also compatible with LGPL-2.1 licensed libraries like chardet.

## Acknowledgments

We gratefully acknowledge the contributions of all open source projects that make this SDK possible. Special thanks to:

- The **HTTPX** project team for providing a modern, async-capable HTTP client
- The **Python** core development team and community
- The **pytest** and **tox** projects for excellent testing frameworks
- The **Ruff** project for fast and comprehensive linting
- The **uv** and **tox-uv** projects for modern Python package management
- All other maintainers and contributors of the dependencies listed above

## License Information Updates

This file was last updated on: 2025-12-10

For the most current license information, please check the individual project pages linked above. License information is subject to change with new versions of dependencies.

If you notice any outdated or incorrect license information, please open an issue in the project repository.