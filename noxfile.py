#!/usr/bin/env -S uv run
"""Build steps for presentation-example."""
# /// script
# dependencies = [
#   "black",
#   "codespell",
#   "mypy",
#   "nox",
#   "reuse",
#   "ruff",
#   "usort",
#   "yamllint",
# ]
# requires-python = ">=3.13"
# ///

# SPDX-License-Identifier: MPL-2.0
# SPDX-FileCopyrightText: 2023 Keith Maxwell
from pathlib import Path

import nox
from nox.sessions import Session

MARP_CLI = (
    "npm",
    "exec",
    "--prefer-offline",
    "--yes",
    "--",
    "@marp-team/marp-cli@latest",
    "--html",
    "--allow-local-files",
)
SITE = Path("_site")
VENV = ".venv"
PYTHON = Path(VENV).absolute() / "bin" / "python"

nox.options.stop_on_first_error = True
nox.options.default_venv_backend = "none"


@nox.session()
def dev(session: Session) -> None:
    """Set up a virtual environment for noxfile.py."""
    metadata = nox.project.load_toml(__file__)
    session.run("uv", "venv", "--python", metadata["requires-python"], VENV)
    env = {"VIRTUAL_ENV": VENV}
    session.run("uv", "pip", "install", *metadata["dependencies"], env=env)


@nox.session(venv_backend="none", requires=["dev"])
def static(session: Session) -> None:
    """Run static analysis tools."""
    session.run(
        "npm",
        "exec",
        "pyright@1.1.408",
        "--yes",
        "--",
        f"--pythonpath={PYTHON}",
    )

    def run(cmd: str) -> None:
        session.run(PYTHON, "-m", *cmd.split())

    run("reuse lint")
    run("usort check src noxfile.py")
    run("black --check .")
    run("ruff check .")
    run("codespell_lib")
    run("mypy .")
    run("yamllint --strict .github")


@nox.session()
def html(session: Session) -> None:
    """Render as index.html."""
    session.run(
        *MARP_CLI,
        f"--output={SITE}/index.html",
        "index.md",
    )


@nox.session()
def pdf(session: Session) -> None:
    """Render as index.pdf."""
    session.run(
        *MARP_CLI,
        "--pdf",
        "--theme=a4.css",
        f"--output={SITE}/index.pdf",
        "index.md",
    )


@nox.session(default=False)
def serve(session: Session) -> None:
    """Serve at http://localhost:8080/."""
    session.run(
        "npm",
        "exec",
        "--prefer-offline",
        "--yes",
        "--",
        "@marp-team/marp-cli@latest",
        "--html",
        "--watch",
        "--server",
        ".",
    )


if __name__ == "__main__":
    nox.main()
