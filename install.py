import glob
import subprocess
import sys
from rich import print

for package in glob.glob("dist/*.whl"):
    print(f":construction: [yellow]Installing {package}...[/yellow]")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", package]
    )

print(f":white_check_mark: [bold green]DONE Installing.[/bold green]")
