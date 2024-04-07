"""
    This script simplifies the use of the space ranger software tool
    that processes the raw data of 10X Visium experiments. Run the
    command ``python3 sr-helper.py help`` to view its usage.

    The script can:

    - Download space ranger and reference genomes with
      ``install-dependencies``.
    - Write Slurm scripts to download and process raw FASTQ files with
      ``generate-scripts``.
    - Execute the Slurm scripts with ``run-scripts``.

    Copyright information:

    - Author: Vincent Therrien (therrien.vincent.2@courrier.uqam.ca)
    - Affiliation: Département d'informatique, UQÀM
    - File creation date: March 2024
    - License: MIT
"""


import argparse
import datetime
import json
from pathlib import Path
from shutil import which
import subprocess
from os import listdir
from time import sleep


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


def _get_script_header(account: str, time: str, mem: int, cpus: int) -> str:
    """Write a Slurm script header."""
    return (
        "#!/bin/bash\n"
        + f"#SBATCH --account={account}\n"
        + f"#SBATCH --time={time}\n"
        + f"#SBATCH --mem={mem}G\n"
        + f"#SBATCH --cpus-per-task={cpus}\n\n"
    )


def _wait_until_clear() -> None:
    """Wait until all jobs are completed."""
    for _ in range(60):
        p = subprocess.run(["sq"], capture_output=True)
        n_jobs = len(p.stdout.split("\n")) - 1
        print(f"Number of ongoing jobs: {n_jobs}")
        if n_jobs < 1:
            break
        sleep(60)


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
            "File generation date": str(datetime.datetime.now()),
            "Information": "Edit this file to add references to the 10X Visium data to process. Run `python3 sr-helper.py help create-config` to se how to edit it."  # nopep8
        },
        "pipeline name": "TEST_PIPELINE",
        "sratoolkit activation": "module load mugqic/sratoolkit/2.10.5",
        "space ranger directory": "~/visium/spaceranger-3.0.0",
        "genome directory": "~/visium/references",
        "reference": "human",
        "raw data directory": "~/visium/data",
        "script directory": "~/visium/scripts",
        "result directory": "~/visium/results",
        "version": "visium-2",
        "samples": [
            {
                "name": "A1",
                "FASTQ": "SRR REFERENCE NUMBER",
                "image": "A1_high_res.tiff",
                "slide": None,
                "area": None
            }
        ]
    }
    with open(output, "w") as file:
        json.dump(empty_config, file, indent=4)
    print(f"Created the empty configuration file `{output}`.")


def generate_scripts(args):
    """Generate Slurm scripts to download and process files.

    Args:
        configuration (str): Filepath to the configuration file.
    """
    with open(args.configuration, "r") as file:
        configuration = json.load(file)
    out = configuration['raw data directory']
    fastqs = f"{out}/fastq"
    images = f"{out}/images"
    results = f"{configuration['result directory']}"
    for p in (out, fastqs, images, results):
        Path(p).mkdir(parents=True, exist_ok=True)
    Path(configuration["script directory"]).mkdir(parents=True, exist_ok=True)
    for i, sample in enumerate(configuration["samples"]):
        # Download script
        path = f"{fastqs}/{sample['name']}"
        Path(path).mkdir(parents=True, exist_ok=True)
        name_root = f"{path}/{configuration['pipeline name']}_S1_L001_"
        download_script = (
            _get_script_header(args.account, "00:30:00", 16, 1)
            + configuration["sratoolkit activation"] + "\n\n"
            + f"fasterq-dump {path}\n\n"
            + f'search_dir={path}\n'
            + 'for file in $search_dir/*; do\n'
            + '    echo $file\n'
            + '    if [[ $file == *"_1.fastq" ]]; then\n'
            + f'        mv $file {name_root}_R1_001.fastq\n'
            + '    elif [[ $file == *"_2.fastq" ]]; then\n'
            + f'        mv $file {name_root}_R2_001.fastq\n'
            + '    else\n'
            + f'        mv $file {name_root}_R1_001.fastq\n'
            + '    fi\n'
            + 'done\n\n'
            + f'cp {sample["image"]} {path}/image.tiff\n'
        )
        # space ranger script
        sr_source = f"{configuration['space ranger directory']}/sourceme.bash"
        if configuration["reference"] == "human":
            transcriptome = HUMAN_REFERENCE_VERSION
        else:
            transcriptome = MOUSE_REFERENCE_VERSION
        transcriptome_path = f"{configuration['genome directory']}/{transcriptome}"
        if sample["slide"] == None or sample["area"] == None:
            slide = f"  --unknown-slide={configuration['version']}"
        else:
            slide = (
                f"  --slide={sample['slide']} \\\n"
                + f"  --area={sample['area']}"
            )
        process_script = (
            _get_script_header(args.account, "00:55:00", 64, 8)
            + f"source {sr_source}\n\n"
            + "spaceranger count \\\n"
            + f"  --id={results} \\\n"
            + f"  --transcriptome={transcriptome_path} \\\n"
            + f"  --fastqs={path} \\\n"
            + f"  --sample={sample['name']} \\\n"
            + f"  --image={sample['image']} \\\n"
            + "  --localcores=8 \\\n"
            + "  --localmem=64 \\\n"
            + "  -create-bam=false \\\n"
            + slide
        )
        # Write files.
        out = configuration["script directory"]
        download_name = f'{out}/download_{i}.sh'
        with open(download_name, "w") as file:
            file.write(download_script)
        process_name = f'{out}/process_{i}.sh'
        with open(process_name, "w") as file:
            file.write(process_script)
        print(f"Script files written at `{out}`.")


def run_scripts(args) -> None:
    """Run all script files.

    Args:
        dir (str): Directory in which scripts are stored.
    """
    scripts = listdir(args.dir)
    for script in scripts:
        if "download" in script:
            subprocess.run(["sbatch", f"{args.dir}/{script}"])
    _wait_until_clear()
    for script in scripts:
        if "process" in script:
            subprocess.run(["sbatch", f"{args.dir}/{script}"])


# Command line argument parsing.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Space ranger wrapper.')
    subparsers = parser.add_subparsers(dest='command')

    install = subparsers.add_parser(
        'get-dependencies',
        help='Install required programs and reference files.',
    )
    install.add_argument('dir', type=str, help='Installation directory.')
    install.set_defaults(func=install_dependencies)

    create_file = subparsers.add_parser(
        'create-config',
        help='Create an empty configuration file.',
    )
    create_file.add_argument('output',
                             type=str, help='Configuration file name.')
    create_file.set_defaults(func=create_config)

    create_scripts = subparsers.add_parser(
        'generate-scripts',
        help='Generate Slurm scripts.',
    )
    create_scripts.add_argument('configuration', type=str,
                                help='Configuration file name.')
    create_scripts.add_argument('account', type=str,
                                help='User account.')
    create_scripts.set_defaults(func=generate_scripts)

    run = subparsers.add_parser(
        'run-scripts',
        help='Run the Slurm scripts.',
    )
    run.add_argument('dir', type=str, help='script directory.')
    run.set_defaults(func=install_dependencies)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
