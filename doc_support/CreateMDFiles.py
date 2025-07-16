#!/usr/bin/env python3
import fileinput
import sys
from pathlib import Path


def find_mkdocs_dir(start: Path) -> Path:
    """
    Starting from 'start', walk upward until a directory containing 'mkdocs.yml'
    is found. Returns that directory. If not found, returns None.
    """
    current = start.resolve()
    while current != current.parent:  # stop at filesystem root
        if (current / "mkdocs.yml").exists():
            return current
        current = current.parent
    return None


def create_md_files(input_folder: str):
    """
    Generate .md files for mkdocs documentation from Python files.

    Given an absolute input_folder, finds the nearest parent directory containing
    mkdocs.yml. Then for each .py file under input_folder, the function creates a
    corresponding .md file in the "<mkdocs_dir>/docs/<relative_input_path>" location,
    with content in the format:

         ::: base_package.submodule.module

    The base package is derived from the part of the input folder's path that is
    relative to the mkdocs directory: path separators are replaced with dots.
    """
    input_path = Path(input_folder).resolve()
    mkdocs_dir = find_mkdocs_dir(input_path)
    if mkdocs_dir is None:
        print(
            "Error: Could not find a mkdocs.yml file in any parent directory of the input folder."
        )
        sys.exit(1)

    # Derive the relative path from the found mkdocs_dir.
    try:
        relative_input = input_path.relative_to(mkdocs_dir)
    except ValueError:
        # If for some reason the input_path is not under mkdocs_dir, exit.
        print("Error: The input folder must be under the mkdocs directory.")
        sys.exit(1)

    # Derive the output folder as: <mkdocs_dir>/docs/<relative_input>
    output_path = mkdocs_dir / "docs" / relative_input
    output_path.mkdir(parents=True, exist_ok=True)

    # Derive the base package from the relative path, using forward slashes
    # e.g., "aiweb_common/generate" -> "aiweb_common.generate"
    base_package = relative_input.as_posix().replace("/", ".")

    print(f"Found mkdocs directory: {mkdocs_dir}")
    print(f"Input Folder  : {input_path}")
    print(f"Output Folder : {output_path}")
    print(f"Base Package  : {base_package}\n")

    # Process each .py file in the input folder.
    for py_file in input_path.rglob("*.py"):
        # Get its path relative to input_path.
        rel_path = py_file.relative_to(input_path)

        # Build the corresponding .md file path.
        md_file_path = output_path / rel_path.with_suffix(".md")
        md_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Construct the module path: base_package + relative (without suffix)
        relative_module = rel_path.with_suffix("").as_posix().replace("/", ".")
        module_path = f"{base_package}.{relative_module}" if relative_module else base_package

        md_content = f"::: {module_path}\n"
        md_file_path.write_text(md_content)
        print(f"Created: {md_file_path}")


def get_parameters():
    """
    Retrieve the input folder from sys.argv or from STDIN.
    In this simplified version, we need the input folder path.
    If not provided as a command-line argument, prompt the user.
    """
    try:
        if len(sys.argv) >= 2:
            return sys.argv[1]
        else:
            if sys.stdin.isatty():
                input_folder = input("Enter absolute input folder: ").strip()
                return input_folder
            else:
                print("Reading input folder from STDIN (expecting one line).")
                lines = [line.strip() for line in fileinput.input()]
                if len(lines) < 1:
                    print("Error: Need one parameter: input_folder")
                    sys.exit(1)
                return lines[0]
    except Exception as e:
        print(f"Input error encountered ({e}); exiting.")
        sys.exit(1)


if __name__ == "__main__":
    input_folder = get_parameters()
    create_md_files(input_folder)
    print("\nDone!")
