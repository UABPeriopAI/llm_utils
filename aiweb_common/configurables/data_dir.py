import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_data_dir(
    base_dir: Path,
    devcontainer_config_path: Path,
    user_config_path: Optional[Path] = None,
    target_mount: str = "/data",
) -> Optional[Path]:
    """
    Determines the data directory path based on the environment.

    This function implements the following logic in order:
    1. Check for a Docker environment by looking for the target_mount directory.
    2. If not in Docker, parse the .devcontainer.json file to find the
       host path mounted to target_mount. This handles JSON with comments,
       string or object mount formats, and ${localWorkspaceFolder} expansion.
    3. As a final fallback, check for a user-configurable path in the
       user_config_path file.

    Args:
        base_dir: The base directory of the project.
        devcontainer_config_path: The path to the .devcontainer.json file.
        user_config_path: The path to the user-specific config file.
        target_mount: The target mount point to look for (e.g., '/data').

    Returns:
        The path to the data directory, or None if not found.
    """
    docker_data_path = Path(target_mount)
    if docker_data_path.is_dir():
        logger.info("Docker environment detected. Using %s", docker_data_path)
        return docker_data_path

    if devcontainer_config_path.exists():
        logger.info("Found devcontainer config at %s", devcontainer_config_path)
        with open(devcontainer_config_path, "r") as f:
            try:
                # Read file and remove comments to handle jsonc
                content = f.read()
                content = re.sub(r"//.*", "", content)
                content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
                devcontainer_config = json.loads(content)

                mounts = devcontainer_config.get("mounts", [])
                for mount in mounts:
                    source_path_str = None
                    target_path_str = None

                    if isinstance(mount, str):
                        # Format: "type=bind,source=...,target=/data"
                        mount_parts = dict(
                            part.split("=", 1) for part in mount.split(",") if "=" in part
                        )
                        target_path_str = mount_parts.get("target")
                        source_path_str = mount_parts.get("source")
                    elif isinstance(mount, dict):
                        # Format: {"source": "...", "target": "...", ...}
                        target_path_str = mount.get("target")
                        source_path_str = mount.get("source")

                    if target_path_str == target_mount and source_path_str:
                        # Expand ${localWorkspaceFolder} which is equivalent to base_dir
                        expanded_path = source_path_str.replace(
                            "${localWorkspaceFolder}", str(base_dir)
                        )
                        source_path = Path(expanded_path)
                        if source_path.is_dir():
                            logger.info(
                                "Found and using host path from devcontainer: %s",
                                source_path,
                            )
                            return source_path
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.error("Error parsing %s: %s", devcontainer_config_path, e)

    # Fallback to user-specific config file
    if user_config_path and user_config_path.exists():
        with open(user_config_path, "r") as f:
            try:
                user_config = json.load(f)
                user_data_dir_str = user_config.get("USER_DATA_DIR")
                if user_data_dir_str:
                    user_data_dir = Path(user_data_dir_str)
                    if user_data_dir.is_dir():
                        logger.info("Using user-configured data directory: %s", user_data_dir)
                        return user_data_dir
            except json.JSONDecodeError:
                logger.warning("Could not parse %s.", user_config_path)

    logger.warning(
        "Data directory not found. Please ensure you are in the correct "
        "environment or have set up your user_config.json correctly."
    )
    return None
