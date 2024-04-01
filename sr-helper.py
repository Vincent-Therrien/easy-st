"""
    This script simplifies the use of the space ranger software tool
    that processes the raw data of 10X Visium experiments. Run the
    command ``python3 sr-helper.py help` to view its usage.

    The script can:

    - Download space ranger and reference genomes with
      ``install-dependencies``
    - Write Slurm scripts to download and process raw FASTQ files with
      ``generate-scripts``
    - Execute the Slurm scripts with ``run-scripts``

    Copyright information:

    - Author: Vincent Therrien (therrien.vincent.2@courrier.uqam.ca)
    - Affiliation: Département d'informatique, UQÀM
    - File creation date: March 2024
    - License: MIT
"""


import argparse
import json
from pathlib import Path
from shutil import which
import subprocess


SPACE_RANGER_URL = '"https://cf.10xgenomics.com/releases/spatial-exp/spaceranger-3.0.0.tar.gz?Expires=1711892573&Key-Pair-Id=APKAI7S6A5RYOXBWRPDA&Signature=aFYZ9LHh705yiMvx9Qhs4fo~9wvcN0OKbnMKM2pM8UnzCbxaqAJEDZ-mbwm3Azr-Ary9KKMvzSC1fDy2wXI5jv-OySeSIuCh~odZ-1BqQh1xsjzJbVcOSqclzZRQZW5k2e-voXHRCO15uOGYWCEYyooVUwkWFBE5f8bG3UGVe6WDZprs1xp51-7iLD9mxo3KAcbNhDGBMBfTOaHnEK3JHVx7btEdtLZKR1q8FboYv1vEovyFH2Fx0fDRxV5rS9XzIS4GQo5-cicCkGaEPiXdMrpTLYvyKY4mt3h33SrVHujF5v9NOR5lw0~S2UcV7tDG~zRskLvmFwFyCJKaLAUcIw__"'  # nopep8
SPACE_RANGER_VERSION = "3.0.0"
HUMAN_REFERENCE_URL = '"https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-GRCh38-2020-A.tar.gz"'
HUMAN_REFERENCE_VERSION = "refdata-gex-GRCh38-2020-A"
MOUSE_REFERENCE_URL = '"https://cf.10xgenomics.com/supp/spatial-exp/refdata-gex-mm10-2020-A.tar.gz"'
MOUSE_REFERENCE_VERSION = "refdata-gex-mm10-2020-A"


# Utility functions
def _is_tool_installed(name: str) -> bool:
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None


def _configure_directories(root: str) -> None:
    """Create the directories required for processing and storing
    results.

    Args:
        root (str): Root directory.
    """
    pass


def _download_file(url: str, output_name: str) -> None:
    """Download a file with curl.

    Args
        url (str): File URL to use for download.
        output_name (str): Name under which to save the file.
    """
    if not _is_tool_installed("curl"):
        print(f"The program `curl` is not install. Cannot download `{url}`.")
        return
    subprocess.run(["curl", "-o", output_name, url], capture_output=True)


# Command functions
def install_dependencies(args) -> None:
    """Install reference genomes and space ranger.

    Args:
        dir (str): Installation directory.
    """
    dir = args.dir
    download_sr = input("Download space ranger [Y/n]? ")
    download_human = input("Download the human reference genome [Y/n]? ")
    download_mouse = input("Download the mouse reference genome [Y/n]? ")
    Path(dir).mkdir(parents=True, exist_ok=True)
    if download_sr.lower() in ("y", ""):
        archive_name = f"{dir}/spaceranger-{SPACE_RANGER_VERSION}.tar.gz"
        _download_file(SPACE_RANGER_URL, archive_name)
        subprocess.run(["tar", "-xvzf", archive_name], capture_output=True)
    if download_human.lower() in ("y", ""):
        archive_name = f"{dir}/{HUMAN_REFERENCE_VERSION}.tar.gz"
        _download_file(HUMAN_REFERENCE_URL, archive_name)
        subprocess.run(["tar", "-xvzf", archive_name], capture_output=True)
    if download_mouse.lower() in ("y", ""):
        archive_name = f"{dir}/{MOUSE_REFERENCE_VERSION}.tar.gz"
        _download_file(MOUSE_REFERENCE_URL, archive_name)
        subprocess.run(["tar", "-xvzf", archive_name], capture_output=True)


def create_config(args) -> None:
    """Create an empty configuration file.

    Args:
        output (str): Output file name (must be a JSON file name).
    """
    output = args.output
    if not output.endswith(".json"):
        print(f"The file name `{output}` is not a valid JSON name.")
        return
    empty_config = {
        "metadata": {
            "File generation date": "2024-04-01T00:05:51Z",
            "Information": "Edit this file to add references to the 10X Visium data to process. Run `python3 sr-helper.py help create-config` to se how to edit it."  # nopep8
        },
        "pipeline name": "TEST PIPELINE",
        "space ranger directory": "~/visium/spaceranger-3.0.0",
        "genome installation directory": "~/visium/references",
        "output directory": "~/visium/data",
        "samples": [
            {
                "name": "A1",
                "FASTQ": "SRR REFERENCE NUMBER",
                "image": "A1_high_res.tiff"
            }
        ]
    }
    with open(output, "w") as file:
        json.dump(empty_config, file, indent=4)
    print(f"Created the empty configuration file `{output}`.")


def generate_scripts(args):
    pass


def run_scripts(args):
    pass


# Command line argument parsing.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Space ranger wrapper.')
    subparsers = parser.add_subparsers(dest='command')

    install = subparsers.add_parser(
        'install-dependencies',
        help='Install required programs and reference files.',
    )
    install.add_argument('dir', type=str, help='Installation directory.')
    install.set_defaults(func=install_dependencies)

    create = subparsers.add_parser(
        'create-config',
        help='Create an empty configuration file.',
    )
    create.add_argument('output', type=str, help='Configuration file name.')
    create.set_defaults(func=create_config)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
