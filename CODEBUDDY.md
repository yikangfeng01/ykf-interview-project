# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## Project Overview

This is a Python project (`ykf-interview-project`) managed with IntelliJ IDEA. The Python SDK is Anaconda3 located at `$USER_HOME$/anaconda3`. Version control uses Git.

The project is currently in its initial setup phase with no source code yet.

## Common Commands

### Running Python Scripts
```bash
# Run a single Python script
python <script_name>.py

# Run with Anaconda Python explicitly
$USER_HOME$/anaconda3/bin/python <script_name>.py
```

### Package Management
```bash
# Install packages with conda
conda install <package_name>

# Install packages with pip
pip install <package_name>

# Create requirements.txt from current environment
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

### Git
```bash
git status
git add .
git commit -m "message"
```

## Architecture

The project is a Python module (`PYTHON_MODULE` type in IntelliJ IDEA). Source code should be placed directly in the project root or organized into Python packages (directories with `__init__.py` files). The compiler output directory is `out/`, which is excluded from version control.

### Key Configuration Files

- **`ykf-interview-project.iml`**: IntelliJ IDEA module file defining the Python module structure and SDK reference.
- **`.idea/misc.xml`**: Project-level settings including JDK/SDK configuration pointing to Anaconda3.
- **`.idea/vcs.xml`**: VCS configuration, set to Git.

### Development Environment

- **Language**: Python (via Anaconda3)
- **IDE**: IntelliJ IDEA
- **VCS**: Git
- **Output directory**: `out/` (not tracked by Git)
