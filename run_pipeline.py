"""Rebuild every cleaned and joined data file with one command.

Runs the data-preparation notebooks in order:

1. cleaning_waste_datasets.ipynb   (package B)  -> 3 waste CSVs
2. cleaning_population.ipynb       (package C)  -> population + region lookup CSVs
3. merging_datasets.ipynb          (package A)  -> panel_country_year.csv, treatment_latest_joined.csv

All outputs go to team2_waste_data/processed/. The notebooks themselves are executed in memory and are
not overwritten, so running this does not change any file tracked by Git except the CSV outputs.

Usage (from the repository root):
    python run_pipeline.py              # use the raw files already in the repo
    python run_pipeline.py --download   # download the raw files again first
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "team2_waste_data" / "scripts"
PROCESSED = ROOT / "team2_waste_data" / "processed"

STEPS = [
    ("B: clean waste data", "cleaning_waste_datasets.ipynb"),
    ("C: clean population data", "cleaning_population.ipynb"),
    ("A: join waste and population", "merging_datasets.ipynb"),
]


def run_notebook(path):
    """Execute a notebook top to bottom inside its own folder, without saving it back to disk."""
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(notebook, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}})
    client.execute()


def download_raw_data():
    """Run the download script that fetches the raw UNSD and WPP files again."""
    script = SCRIPTS / "download_data.py"
    subprocess.run([sys.executable, str(script)], cwd=script.parent.parent, check=True)


def main():
    """Run all steps in order and stop at the first one that fails."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--download", action="store_true", help="download the raw data again before cleaning")
    args = parser.parse_args()

    if args.download:
        print("Downloading raw data ...")
        download_raw_data()

    PROCESSED.mkdir(exist_ok=True)
    for label, file_name in STEPS:
        start = time.time()
        print(f"Running {label} ({file_name}) ...", end=" ", flush=True)
        try:
            run_notebook(SCRIPTS / file_name)
        except CellExecutionError as error:
            print("FAILED")
            print(f"\nThe notebook {file_name} stopped with an error. Open it in Jupyter to see the cell:\n")
            print(error)
            sys.exit(1)
        print(f"done in {time.time() - start:.0f} s")

    print("\nAll steps finished. Files in", PROCESSED.relative_to(ROOT), ":")
    for csv in sorted(PROCESSED.glob("*.csv")):
        print("  ", csv.name)


if __name__ == "__main__":
    main()
