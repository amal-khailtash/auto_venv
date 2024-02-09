"""Automatically Creates Virtual Environment and Installs Requirements."""

__version__ = "0.1.0"

def init(filename: str, requires: list[str], fancy=False, quiet=False, dot_pth=False) -> None:
    """Create virtual environment and install dependencies.

    Args:
        filename (str)            : calling script's filename including full path.
        requires (list[str])      : list of requirements to install
        fancy    (bool, optional) : fancy/ANSI printout.  (Defaults to False)
        quiet    (bool, optional) : quiet (no) messages.  (Defaults to False)
        dot_pth  (bool, optional) : create .pth link to the .venv  (Defaults to False)
    """

    import getpass
    import os
    import subprocess
    import site
    import sys
    import uuid
    from pathlib import Path

    def run(*args, **kwargs) -> None:
        """
        _summary_
        """
        try:
            return subprocess.run(*args, **kwargs)
        except KeyboardInterrupt:
            sys.stderr.write("\nCancelled!\n")
            sys.exit()

    def msg(s: str) -> None:
        """
        _summary_

        Args:
            s (str): string to print.
        """
        if quiet:
            return
        sys.stderr.write(s + "\n")

    if "AUTO_VENV_FANCY" in os.environ:
        fancy = (os.environ.get("AUTO_VENV_FANCY", "False").lower() in ("1", "y", "yes", "true"))

    if "AUTO_VENV_QUIET" in os.environ:
        quiet = (os.environ.get("AUTO_VENV_QUIET", "False").lower() in ("1", "y", "yes", "true"))

    if "AUTO_VENV_DOT_PTH" in os.environ:
        dot_pth = (os.environ.get("AUTO_VENV_DOT_PTH", "False").lower() in ("1", "y", "yes", "true"))

    prefix = "│ " if fancy else ""
    arrow = "➜" if fancy else ">"
    check = "✓" if fancy else "*"

    # Name of the virtual environment
    venv_name = ".venv"
    username = getpass.getuser()
    unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{username}:{filename}")
    venv_fullname = f"{venv_name}_{unique_id}_{username}_{Path(filename).name}"

    venv_root = Path(os.environ.get("VENV_AUTO_ROOT", "/tmp"))

    # Path to the virtual environment
    venv_path = venv_root / venv_fullname

    site_packages_path = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"

    sys.path = [path for path in sys.path if "-packages" not in path] + [str(site_packages_path)]

    bin_path = venv_path / "bin"

    os.environ["PATH"] += os.pathsep + str(bin_path)

    msg("╭" + "─" * 80 if fancy else "-" * 80)

    all_requirements_met = False

    # Create the virtual environment if it doesn't exist
    if venv_path.exists():
        msg(f"{prefix}{arrow} Virtual environment already exists ...")
        msg(f"{prefix}    '{venv_path}'")

        result = run(
            [f"{bin_path}/python", "-m", "pip", "freeze"],
            capture_output = True,
            text = True
        )
        all_packages = [package.lower() for package in result.stdout.strip("\n").split("\n")]

        all_requirements_met = set(requires).issubset(set(all_packages))

    if all_requirements_met:
        msg(f"{prefix}{arrow} All requirements are met.")
    else:
        msg(f"{prefix}{arrow} First run or some requirements were not found.  Reinstalling ...")
        msg(f"{prefix}{arrow} Creating virtual environment ...")
        msg(f"{prefix}    '{venv_path}'")

        run([sys.executable, "-m", "venv", "" if all_requirements_met else "--clear", venv_path], check=True, start_new_session=True)

        if dot_pth:
            # Create .pth to point to this venv
            pth_file = Path(f"{site.USER_SITE}") / f"{venv_fullname.removeprefix(".")}.pth"

            msg(f"{prefix}{arrow} Setting up PYTHONPATH ...")
            msg(f"{prefix}    '{pth_file}'")

            pth_file.parent.mkdir(exist_ok=True, parents=True)
            pth_file.write_text(f"{site_packages_path}")

        msg(f"{prefix}{arrow} Upgrading 'pip' ...")

        run(
            [f"{bin_path}/python", "-m", "pip", "install", "--upgrade", "pip"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            start_new_session=True
        )

        # Install the required packages
        msg(f"{prefix}{arrow} Installing requirements:")

        for req in requires:
            run(
                [f"{bin_path}/python", "-m", "pip", "install", req],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                start_new_session=True
            )
            msg(f"{prefix}  {check} {req}")

    msg(f"{prefix}{arrow} Continuing with the script ...")

    msg("╰" + "─" * 80 if fancy else "-" * 80)
