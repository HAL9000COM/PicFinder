# %%
# download libsimple release from github
import os
import shutil
import zipfile
from pathlib import Path

import requests


def download_libsimple():
    # Dictionary containing the target libraries and their download URLs
    download_target = {
        "libsimple-linux-ubuntu-latest": "https://github.com/wangfenjin/simple/releases/download/v0.4.0/libsimple-linux-ubuntu-latest.zip",
        "libsimple-windows-x64": "https://github.com/wangfenjin/simple/releases/download/v0.4.0/libsimple-windows-x64.zip",
    }
    for lib_dir_name, url in download_target.items():
        try:
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


# %%
download_libsimple()
# %%
