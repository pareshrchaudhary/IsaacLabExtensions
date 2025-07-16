#!/usr/bin/env python3

"""
Script to automatically generate a new Isaac Lab extension.

This script creates the complete directory structure and boilerplate files
for a new Isaac Lab extension based on the provided name.

Usage:
    python scripts/generate_extension.py --name <extension_name> [--path <custom_path>]

Example:
    python scripts/generate_extension.py --name my_robot_env
    python scripts/generate_extension.py --name custom_sensors --path source/sensors
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


def create_directory_structure(extension_name: str, base_path: Path) -> None:
    """Create the directory structure for the extension."""
    extension_path = base_path / extension_name
    
    # Create main directories
    directories = [
        extension_path,
        extension_path / "config",
        extension_path / "docs", 
        extension_path / extension_name,
        extension_path / extension_name / "tasks",
        extension_path / extension_name / "scripts",
        extension_path / "tests"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


def create_setup_py(extension_name: str, extension_path: Path) -> None:
    """Create the setup.py file."""
    setup_content = f'''"""Installation script for the '{extension_name}' python package."""

import os
import toml

from setuptools import setup

# Obtain the extension data from the extension.toml file
EXTENSION_PATH = os.path.dirname(os.path.realpath(__file__))
# Read the extension.toml file
EXTENSION_TOML_DATA = toml.load(os.path.join(EXTENSION_PATH, "config", "extension.toml"))

# Minimum dependencies required prior to installation
INSTALL_REQUIRES = [
    # NOTE: Add dependencies
    "psutil",
]

# Installation operation
setup(
    name="{extension_name}",
    packages=["{extension_name}"],
    author=EXTENSION_TOML_DATA["package"]["author"],
    maintainer=EXTENSION_TOML_DATA["package"]["maintainer"],
    url=EXTENSION_TOML_DATA["package"]["repository"],
    version=EXTENSION_TOML_DATA["package"]["version"],
    description=EXTENSION_TOML_DATA["package"]["description"],
    keywords=EXTENSION_TOML_DATA["package"]["keywords"],
    install_requires=INSTALL_REQUIRES,
    license="Apache 2.0",
    include_package_data=True,
    python_requires=">=3.10",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
        "Isaac Sim :: 4.5.0",
    ],
    zip_safe=False,
)
'''
    
    setup_file = extension_path / "setup.py"
    setup_file.write_text(setup_content)
    print(f"Created file: {setup_file}")


def create_pyproject_toml(extension_path: Path) -> None:
    """Create the pyproject.toml file."""
    pyproject_content = '''[build-system]
requires = ["setuptools", "wheel", "toml"]
build-backend = "setuptools.build_meta"
'''
    
    pyproject_file = extension_path / "pyproject.toml"
    pyproject_file.write_text(pyproject_content)
    print(f"Created file: {pyproject_file}")


def create_extension_toml(extension_name: str, extension_path: Path) -> None:
    """Create the extension.toml configuration file."""
    extension_title = extension_name.replace("_", " ").title()
    
    toml_content = f'''[package]

# Semantic Versioning is used: https://semver.org/
version = "0.1.0"

# Description
category = "isaaclab"
readme  = "README.md"

title = "{extension_title}"
author = "Isaac Lab Project Developers"
maintainer = "Isaac Lab Project Developers"
description="{extension_title} Extension for Isaac Lab"
repository = "https://github.com/isaac-sim/IsaacLabExtensionTemplate.git"
keywords = ["extension", "{extension_name}", "isaaclab"]

[dependencies]
"isaaclab" = {{}}
"isaaclab_assets" = {{}}
"isaaclab_mimic" = {{}}
"isaaclab_rl" = {{}}
"isaaclab_tasks" = {{}}
# NOTE: Add additional dependencies here

[[python.module]]
name = "{extension_name}"

[isaaclab_settings]
# TODO: Uncomment and list any apt dependencies here.
#       If none, leave it commented out.
# apt_deps = ["example_package"]
# TODO: Uncomment and provide path to a ros_ws
#       with rosdeps to be installed. If none,
#       leave it commented out.
# ros_ws = "path/from/extension_root/to/ros_ws"
'''
    
    config_file = extension_path / "config" / "extension.toml"
    config_file.write_text(toml_content)
    print(f"Created file: {config_file}")


def create_init_py(extension_name: str, extension_path: Path) -> None:
    """Create the main __init__.py file."""
    init_content = f'''"""
Python module for {extension_name} extension.
"""

# Register Gym environments.
from .tasks import *

# Register scripts.
from .scripts import *
'''
    
    init_file = extension_path / extension_name / "__init__.py"
    init_file.write_text(init_content)
    print(f"Created file: {init_file}")


def create_tasks_init(extension_name: str, extension_path: Path) -> None:
    """Create the tasks __init__.py file."""
    tasks_init_content = f'''"""
Task definitions for {extension_name} extension.
"""

# Import task configurations and environments here
# Example:
# from .my_env import MyEnvCfg, MyEnv

__all__ = [
    # Add your task exports here
]
'''
    
    tasks_init_file = extension_path / extension_name / "tasks" / "__init__.py"
    tasks_init_file.write_text(tasks_init_content)
    print(f"Created file: {tasks_init_file}")


def create_scripts_init(extension_name: str, extension_path: Path) -> None:
    """Create the scripts __init__.py file."""
    scripts_init_content = f'''"""
Scripts for {extension_name} extension.
"""

# Import scripts here
# Example:
# from .train import main as train_main

__all__ = [
    # Add your script exports here
]
'''
    
    scripts_init_file = extension_path / extension_name / "scripts" / "__init__.py"
    scripts_init_file.write_text(scripts_init_content)
    print(f"Created file: {scripts_init_file}")


def create_example_task(extension_name: str, extension_path: Path) -> None:
    """Create an example task file."""
    task_content = f'''"""
Example task for {extension_name} extension.

This is a template for creating custom tasks in Isaac Lab.
"""

from isaaclab.envs import BaseEnv, BaseEnvCfg
from isaaclab.utils import configclass


@configclass
class ExampleTaskCfg(BaseEnvCfg):
    """Configuration for the example task."""

    # Add task-specific configurations here
    pass


class ExampleTask(BaseEnv):
    """Example task implementation."""

    cfg: ExampleTaskCfg

    def __init__(self, cfg: ExampleTaskCfg, **kwargs):
        """Initialize the example task."""
        super().__init__(cfg, **kwargs)

    def _setup_scene(self):
        """Set up the scene for the task."""
        # Implement scene setup here
        pass

    def _pre_physics_step(self, actions):
        """Pre-process actions before physics step."""
        # Implement action pre-processing here
        pass

    def _apply_action(self):
        """Apply actions to the environment."""
        # Implement action application here
        pass

    def _get_observations(self):
        """Get observations from the environment."""
        # Implement observation collection here
        return {{}}

    def _get_rewards(self):
        """Calculate rewards for the current step."""
        # Implement reward calculation here
        return 0.0

    def _get_dones(self):
        """Check if episodes are done."""
        # Implement done condition checking here
        return False

    def _reset_idx(self, env_ids):
        """Reset specific environments."""
        # Implement environment reset logic here
        pass
'''
    
    task_file = extension_path / extension_name / "tasks" / "example_task.py"
    task_file.write_text(task_content)
    print(f"Created file: {task_file}")


def create_changelog(extension_path: Path) -> None:
    """Create the CHANGELOG.rst file."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    changelog_content = f'''Changelog
=========

[0.1.0] - {current_date}
----------------------

Added
^^^^^

* Initial extension setup
* Basic project structure
* Example task template
'''
    
    changelog_file = extension_path / "docs" / "CHANGELOG.rst"
    changelog_file.write_text(changelog_content)
    print(f"Created file: {changelog_file}")


def create_extension_readme(extension_name: str, extension_path: Path) -> None:
    """Create the README.md file for the extension."""
    extension_title = extension_name.replace("_", " ").title()
    
    readme_content = f'''# {extension_title}

This extension provides {extension_title.lower()} functionality for Isaac Lab.

## Overview

Describe your extension here. Include:
- What this extension does
- Key features
- Use cases

## Installation

Install the extension using pip:

```bash
python -m pip install -e .
```

## Usage

Describe how to use your extension:

```python
# Example usage
from {extension_name}.tasks import ExampleTaskCfg, ExampleTask

# Create task configuration
cfg = ExampleTaskCfg()

# Create and run task
task = ExampleTask(cfg)
```

## Configuration

Describe configuration options and parameters.

## Examples

Provide examples of how to use your extension.

## Contributing

Guidelines for contributing to this extension.
'''
    
    readme_file = extension_path / "docs" / "README.md"
    readme_file.write_text(readme_content)
    print(f"Created file: {readme_file}")


def create_test_file(extension_name: str, extension_path: Path) -> None:
    """Create a basic test file."""
    test_content = f'''"""
Tests for {extension_name} extension.
"""

import unittest


class Test{extension_name.title().replace("_", "")}(unittest.TestCase):
    """Test cases for {extension_name} extension."""

    def test_import(self):
        """Test that the extension can be imported."""
        try:
            import {extension_name}
            self.assertTrue(True)
        except ImportError:
            self.fail(f"Failed to import {extension_name}")


if __name__ == "__main__":
    unittest.main()
'''
    
    test_file = extension_path / "tests" / f"test_{extension_name}.py"
    test_file.write_text(test_content)
    print(f"Created file: {test_file}")





def main():
    """Main function to generate the extension."""
    parser = argparse.ArgumentParser(
        description="Generate a new Isaac Lab extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--name", 
        type=str, 
        required=True,
        help="Name of the extension to create"
    )
    parser.add_argument(
        "--path",
        type=str,
        default="source",
        help="Base path where to create the extension (default: source)"
    )
    
    args = parser.parse_args()
    
    # Validate extension name
    extension_name = args.name.lower().replace("-", "_")
    if not extension_name.isidentifier():
        print(f"Error: '{extension_name}' is not a valid Python identifier")
        sys.exit(1)
    
    # Determine the base path
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    base_path = repo_root / args.path
    extension_path = base_path / extension_name
    
    # Check if extension already exists
    if extension_path.exists():
        print(f"Error: Extension '{extension_name}' already exists at {extension_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Aborting extension generation")
            sys.exit(1)
    
    print(f"Generating extension '{extension_name}' at {extension_path}")
    
    try:
        # Create the extension
        create_directory_structure(extension_name, base_path)
        create_setup_py(extension_name, extension_path)
        create_pyproject_toml(extension_path)
        create_extension_toml(extension_name, extension_path)
        create_init_py(extension_name, extension_path)
        create_tasks_init(extension_name, extension_path)
        create_scripts_init(extension_name, extension_path)
        create_example_task(extension_name, extension_path)
        create_changelog(extension_path)
        create_extension_readme(extension_name, extension_path)
        create_test_file(extension_name, extension_path)
        
        print(f"\nSuccessfully generated extension '{extension_name}'!")
        print(f"Location: {extension_path}")
        print("\nNext steps:")
        print(f"1. Navigate to the extension directory: cd {extension_path}")
        print("2. Install the extension: python -m pip install -e .")
        print("3. Customize the extension files as needed")
        print("4. Add your tasks, environments, and scripts")
        
    except Exception as e:
        print(f"Error generating extension: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 