# Isaac Lab Extensions for Custom Project

## Overview

This repository serves as a template for building projects or extensions based on Isaac Lab. It allows you to develop in an isolated environment, outside of the core Isaac Lab repository. It is adapted from [IsaacLabExtensionTemplate](https://github.com/isaac-sim/IsaacLabExtensionTemplate) and is built to run offline on local machine as well as HPC using local assets.

## IsaacLab Extensions

Isaac Lab extensions are modular Python packages that extend the functionality of Isaac Sim, providing reusable components for simulation tasks such as actuators, assets, environments, sensors, and more. They can be loaded dynamically into Isaac Sim applications, allowing you to mix and match them for custom workflows (e.g., training RL agents or running simulations). They are built using setuptools for easy packaging and installation. Each extension is self-contained, with its own setup.py for building, dependencies, and Python modules that can be loaded dynamically into Isaac Sim applications.

- **Organization**: Extensions are organized in the `source` directory of the main repository (e.g., `isaaclab` for core interfaces, `isaaclab_assets` for pre-configured assets). 

They follow a standard structure:

```
<extension-name>
├── config
│   └── extension.toml
├── docs
│   ├── CHANGELOG.md
│   └── README.md
├── <extension-name>
│   ├── __init__.py
│   ├── ....
│   └── scripts
├── setup.py
└── tests
```

The repository's root has a `pyproject.toml` for overall project configuration (e.g., for tools like `flake8` or `black`).

### Building the Package
Isaac Lab recommends using setuptools directly for simplicity.
To build an extension, you run `python setup.py build_ext --inplace` or similar from the extension's directory. This compiles any C++ components (if present) and prepares the Python package.

### Dependencies
- **Python dependencies**: Specified in `setup.py` (e.g., `install_requires=['numpy', 'torch']`). These are installed automatically via pip.
- **Non-Python dependencies**: Handled via `extension.toml` (e.g., `apt_deps = ["libboost-all-dev"]` for apt packages or `ros_ws` for ROS workspaces). These are installed separately using a script like `tools/install_deps.py` from the repo root:
  ```
  python tools/install_deps.py --type apt --extensions source
  ```
  This ensures things like system libraries or ROS packages are available before using the extension.

## Extensions in Practice

### Loading and Usage
- Extensions are enabled/disabled programmatically.
- import them like any Python package: e.g., `import isaaclab.envs` for environment definitions, or `from isaaclab.assets import Articulation` for robot assets.
- They provide high-level APIs for simulation tasks (e.g., creating terrains, spawning robots, running physics steps).
- Workflows: Run extensions in "standalone" mode (via scripts in `scripts/` like `scripts/environments/cartpole.py`) or build custom apps on top.

### Creating Custom Extensions
If building your own (e.g., for a new task in your project):
- Create a new directory under `source/` (e.g., `my_extension`).
- Add `setup.py`, `__init__.py`, and `extension.toml`.
- Define your classes/modules (e.g., inheriting from `isaaclab.envs.BaseEnv` for a custom environment).
- Specify dependencies in `setup.py` and `extension.toml`.
- Build and install via pip or include it in your project's experience file.
- For larger projects, create a new repo that depends on Isaac Lab via pip, then add your own extensions.

----
## Installation

1. In the project root dir clone Isaac Lab repo with the specific branch:

```bash
git clone -b pareshrchaudhary/isaaclab-offline https://github.com/pareshrchaudhary/IsaacLab.git IsaacLab
```

2.  Clone this repository separately from the Isaac Lab installation (i.e. outside the `IsaacLab` directory):

```bash
git clone https://github.com/pareshrchaudhary/IsaacLabExtensions
```

3. We need to populate local assets by downloading them to `docker_volumes/assets` located at project root dir. Run `assets.sh` that will download and format them according to IsaacLab requirements.

```bash 
# run asset mangement script
bash IsaacLabExtensions/docker/utils/assets.sh
```
4. Add custom RL library in `libraries` directory:

```bash
# create libraries dir
mkdir libraries && cd libraries

# clone skrl v1.4.3 
git clone --branch 1.4.3 --single-branch --depth 1 https://github.com/Toni-SM/skrl.git
```

5. Add any extensions you want in the source and run/re-run the docker/container.py to install all the extensions automatically.

    - Throughout the repository, the name `test` only serves as an example

```python 
# run docker management utility container.py
python3 IsaacLabExtensions/docker/container.py start        # Build the docker image and create container

python3 IsaacLabExtensions/docker/container.py enter        # Begin a new bash process within an existing Isaac Lab container

python3 IsaacLabExtensions/docker/container.py stop         # Stop the docker container and remove it

python3 IsaacLabExtensions/docker/container.py hard_stop    # Stop the docker container and remove all associated volumes

python3 IsaacLabExtensions/docker/container.py cleanup      # Stop the container, and remove networks, volumes, and images

python3 IsaacLabExtensions/docker/container.py deep_cleanup # Perform a deep cleanup of all resources including docker_volumes directory (preserving assets)
```

5. Once starting the container verify that the extension is correctly installed by running the following command:

```bash
python scripts/rsl_rl/train.py --task=Template-Isaac-Velocity-Rough-Anymal-D-v0
```

---

## Working with Hyak

1. Sync Local machine with Hyak 

    - Create local `isaac-lab-base.tar` file in `hyak_transfer` for HPC deployment:

```bash
# Create tar file and optionally sync to HPC
bash IsaacLabExtensions/docker/cluster/create_tar.sh

# Or just sync docker volumes without creating tar (for syncing cache and other files)
bash IsaacLabExtensions/docker/cluster/create_tar.sh --docker-volumes
```

2. SSH into hyak and convert Docker tar to Apptainer SIF format:

```bash
# Convert the tar file to SIF format for Apptainer/Singularity
bash IsaacLabExtensions/docker/cluster/create_sif.sh
```

This script will:
- Check for the `isaac-lab-base.tar` file in `hyak_transfer` directory
- Create an Apptainer cache directory at repository root level
- Build the SIF file in `/tmp` to avoid GPFS permission issues
- Copy the final SIF file to `hyak_transfer/isaac-lab-base.sif`

3. Running container on Hyak

This is equivalent to point 4 in the installation section above, as `container.py` automatically detects and selects container runtime.

---

## Custom Extensions

This section describes how to create and manage custom extensions in this repository.

### Creating a New Extension

To create a new extension, use the provided generation script:

```bash
# Create extension in default location (source/<extension_name>)
python scripts/generate_extension.py --name <extension_name>

# Create extension in custom path
python scripts/generate_extension.py --name <extension_name> --path <custom_path>
```

Example:
```bash
python scripts/generate_extension.py --name my_robot_env
```

This will create a complete extension structure with:
- Configuration files (`extension.toml`, `setup.py`)
- Python package structure with `__init__.py` files
- Example task implementation
- Documentation templates
- Test files

### Installing Custom Extensions

After creating an extension, install it in development mode, for example:

```bash
cd source/<extension_name>
python -m pip install -e source/my_robot_env
```
