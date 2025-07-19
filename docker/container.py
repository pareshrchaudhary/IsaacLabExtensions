#!/usr/bin/env python3

# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import shutil
from pathlib import Path

from utils import ContainerInterface, ApptainerInterface, x11_utils

def detect_container_runtime():
    """Detect available container runtime."""
    if shutil.which("docker"):
        return "docker"
    elif shutil.which("apptainer") or shutil.which("singularity"):
        return "apptainer"
    else:
        raise RuntimeError("Neither Docker nor Apptainer/Singularity found!")


def parse_cli_args() -> argparse.Namespace:
    """Parse command line arguments.

    This function creates a parser object and adds subparsers for each command. The function then parses the
    command line arguments and returns the parsed arguments.

    Returns:
        The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="Utility for using Docker with Isaac Lab.")

    # We have to create separate parent parsers for common options to our subparsers
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "profile", nargs="?", default="base", help="Optional container profile specification. Example: 'base' or 'ros'."
    )
    parent_parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help=(
            "Allows additional '.yaml' files to be passed to the docker compose command. These files will be merged"
            " with 'docker-compose.yaml' in their provided order."
        ),
    )
    parent_parser.add_argument(
        "--env-files",
        nargs="*",
        default=None,
        help=(
            "Allows additional '.env' files to be passed to the docker compose command. These files will be merged with"
            " '.env.base' in their provided order."
        ),
    )

    # Actual command definition begins here
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "start",
        help="Build the docker image and create the container in detached mode.",
        parents=[parent_parser],
    )
    subparsers.add_parser(
        "enter", help="Begin a new bash process within an existing Isaac Lab container.", parents=[parent_parser]
    )
    config = subparsers.add_parser(
        "config",
        help=(
            "Generate a docker-compose.yaml from the passed yamls, .envs, and either print to the terminal or create a"
            " yaml at output_yaml"
        ),
        parents=[parent_parser],
    )
    config.add_argument(
        "--output-yaml", nargs="?", default=None, help="Yaml file to write config output to. Defaults to None."
    )
    subparsers.add_parser(
        "copy", help="Copy build and logs artifacts from the container to the host machine.", parents=[parent_parser]
    )
    subparsers.add_parser("stop", help="Stop the docker container and remove it.", parents=[parent_parser])
    subparsers.add_parser(
        "hard_stop", help="Stop the docker container and remove all associated volumes.", parents=[parent_parser]
    )
    subparsers.add_parser(
        "cleanup",
        help="Stop the container, and remove networks, volumes, and images.",
        parents=[parent_parser],
    )
    subparsers.add_parser(
        "deep_cleanup",
        help="Perform a deep cleanup of all resources including docker_volumes directory (preserving assets).",
        parents=[parent_parser],
    )

    # parse the arguments to determine the command
    args = parser.parse_args()

    return args


def main(args: argparse.Namespace):
    """Main function for the Docker utility."""
    # check if docker is installed
    runtime = detect_container_runtime()
    
    if runtime == "docker":
        if not shutil.which("docker"):
            raise RuntimeError(
            "Docker is not installed! Please check the 'Docker Guide' for instruction: "
            "https://isaac-sim.github.io/IsaacLab/source/deployment/docker.html"
        )
        
        # creating container interface
        ci = ContainerInterface(
            context_dir=Path(__file__).resolve().parent,
            profile=args.profile,
            yamls=args.files,
            envs=args.env_files,
        )
        
    elif runtime == "apptainer":
        ci = ApptainerInterface(
            context_dir=Path(__file__).resolve().parent,
            profile=args.profile,
            envs=args.env_files,
        )

    print(f"[INFO] Using {runtime} with profile: {ci.profile}")
    
    if args.command == "start":
        # check if x11 forwarding is enabled
        x11_outputs = x11_utils.x11_check(ci.statefile)
        # if x11 forwarding is enabled, add the x11 yaml and environment variables
        if x11_outputs is not None:
            if runtime == "docker":
                (x11_yaml, x11_envar) = x11_outputs
                ci.add_yamls += x11_yaml
                ci.environ.update(x11_envar)
            else:  # apptainer
                (_, x11_envar) = x11_outputs
                ci.environ.update(x11_envar)
        # start the container
        ci.start()
    elif args.command == "enter":
        # refresh the x11 forwarding
        x11_utils.x11_refresh(ci.statefile)
        # enter the container
        ci.enter()
    elif args.command == "config":
        if runtime == "docker":
            ci.config(args.output_yaml)
        else:
            print("[WARNING] Config command not supported with Apptainer.")
            
    elif args.command == "copy":
        ci.copy()
    elif args.command == "stop":
        # stop the container
        ci.stop()
        # cleanup the x11 forwarding
        x11_utils.x11_cleanup(ci.statefile)
    elif args.command == "hard_stop":
        # hard stop the container
        ci.hard_stop()
        # cleanup the x11 forwarding
        x11_utils.x11_cleanup(ci.statefile)
    elif args.command == "cleanup":
        # cleanup the container
        ci.cleanup()
        # cleanup the x11 forwarding
        x11_utils.x11_cleanup(ci.statefile)
    elif args.command == "deep_cleanup":
        # deep cleanup the container
        ci.deep_cleanup()
        # cleanup the x11 forwarding
        x11_utils.x11_cleanup(ci.statefile)
    else:
        raise RuntimeError(f"Invalid command provided: {args.command}. Please check the help message.")


if __name__ == "__main__":
    args_cli = parse_cli_args()
    main(args_cli)
