import subprocess
import sys

from cx_Freeze import Executable, setup

NAME = "PicFinder"
AUTHOR = "HAL9000COM"
DESCRIPTION = (
    "PicFinder is a simple windows application to search for images in a directory."
)
COPYRIGHT = "Copyright (c) 2024, HAL9000COM"
VERSION_BASE = "0.1.0"

try:
    # Get the Git commit hash
    git_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
    )
    # cut the hash to 7 characters
    git_commit = git_commit[:7]
except (subprocess.CalledProcessError, FileNotFoundError):
    git_commit = "unknown"

version = VERSION_BASE + "+" + git_commit

with open("VERSION", "w+", encoding="utf-8") as f:
    f.write(version)

additional_files = [
    "VERSION",
    "models",
    "README.md",
    # "icon.ico",
]
add_packages = [
    # "onnxruntime_directml",
    # "rapidocr_onnxruntime",
]

build_exe_options = {
    "include_msvcr": True,
    # "create_shared_zip": False,
    "build_exe": "build_windows",
    "include_files": additional_files,
    "packages": add_packages,
    "optimize": 0,
}

setup(
    name=NAME,
    version=version,
    author=AUTHOR,
    description=DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            copyright=COPYRIGHT,
            # icon="icon.ico",
            base="Win32GUI",
            # uac_admin=True,
        )
    ],
)
