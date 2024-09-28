# download libsimple release from github
import os
import shutil
import sys
import zipfile
from pathlib import Path

import requests


def download_libsimple():
    # Dictionary containing the target libraries and their download URLs
    url_dict = {
        "libsimple-aarch64-linux-gnu-gcc-9": "https://github.com/wangfenjin/simple/releases/download/v0.4.0/libsimple-aarch64-linux-gnu-gcc-9.zip",
        "libsimple-linux-ubuntu-latest": "https://github.com/wangfenjin/simple/releases/download/v0.4.0/libsimple-linux-ubuntu-latest.zip",
        "libsimple-windows-x64": "https://github.com/wangfenjin/simple/releases/download/v0.4.0/libsimple-windows-x64.zip",
    }
    # get platform and architecture
    if sys.platform.startswith("win"):
        # check if the system is 32 or 64 bit
        lib_to_download = "libsimple-windows-x64"
    elif sys.platform.startswith("linux"):
        # check if the system is arm or x86
        if "aarch64" in os.uname().machine:
            lib_to_download = "libsimple-aarch64-linux-gnu-gcc-9"
        else:
            lib_to_download = "libsimple-linux-ubuntu-latest"
    else:
        # exit if the platform is not supported
        print(f"Unsupported OS: {sys.platform}")
        # Download and extract the libraries
    if lib_to_download in url_dict:
        url = url_dict[lib_to_download]
        lib_dir_name = lib_to_download
        try:
            print(f"Downloading {url}...")
            r = requests.get(url)
            r.raise_for_status()  # Check if the request was successful
            with open("libsimple.zip", "wb") as f:
                f.write(r.content)
            with zipfile.ZipFile("libsimple.zip", "r") as zip_ref:
                zip_ref.extractall("libsimple")
            os.remove("libsimple.zip")
            dest_path = Path("../backend/libsimple") / lib_dir_name
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.move(Path("libsimple") / lib_dir_name, dest_path)
            shutil.rmtree("libsimple")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
        except zipfile.BadZipFile as e:
            print(f"Failed to extract libsimple.zip: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_libsimple()
