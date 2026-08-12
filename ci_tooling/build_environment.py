"""Fail-closed verification for the v2.0 application build environment."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import sysconfig

from pathlib import Path


EXPECTED_PYTHON = (3, 14, 3)
EXPECTED_PIP = "25.3"
EXPECTED_ARCHITECTURE = "x86_64"
EXPECTED_PYTHON_HASH_SEED = "0"
EXPECTED_PYTHON_FRAMEWORK_SHA256 = "131f5211d7a7ec6279abcc2e4b0b97f8559d8eb77d5a28c22771f9ced084360f"
LOCK_FILE = Path(__file__).resolve().parents[1] / "requirements-lock.txt"
PYTHON_VERSION_FILE = Path(__file__).resolve().parents[1] / ".python-version"


def _canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _logical_lock_entries() -> list[str]:
    entries = []
    current = ""
    for raw_line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        continuation = line.endswith("\\")
        current += line[:-1].strip() + " " if continuation else line
        if continuation:
            continue
        entries.append(current.strip())
        current = ""
    if current:
        raise RuntimeError("Incomplete continuation in requirements-lock.txt")
    return entries


def locked_distributions() -> dict[str, str]:
    locked = {}
    for entry in _logical_lock_entries():
        match = re.match(r"^([A-Za-z0-9_.-]+)==([^ ]+)", entry)
        if match is None:
            raise RuntimeError(f"Unparseable lock entry: {entry}")
        hashes = re.findall(r"--hash=sha256:([0-9a-f]{64})(?:\s|$)", entry)
        if len(hashes) != 1:
            raise RuntimeError(f"Lock entry must accept exactly one SHA-256: {entry}")
        name = _canonical_name(match.group(1))
        if name in locked:
            raise RuntimeError(f"Duplicate locked distribution: {name}")
        locked[name] = match.group(2)
    return locked


def installed_distributions() -> dict[str, str]:
    installed = {}
    for distribution in importlib.metadata.distributions():
        name = _canonical_name(distribution.metadata["Name"])
        if name in installed and installed[name] != distribution.version:
            raise RuntimeError(f"Conflicting installed versions for {name}")
        installed[name] = distribution.version
    return installed


def _base_python_sha256() -> str | None:
    base_python = Path(sys.base_prefix) / "Python"
    if not base_python.is_file():
        return None
    return hashlib.sha256(base_python.read_bytes()).hexdigest()


def normalized_manifest() -> dict:
    locked = locked_distributions()
    installed = installed_distributions()
    return {
        "architecture": platform.machine(),
        "implementation": platform.python_implementation(),
        "lock_sha256": hashlib.sha256(LOCK_FILE.read_bytes()).hexdigest(),
        "packages": {name: installed[name] for name in sorted(locked)},
        "pip": installed.get("pip"),
        "python": platform.python_version(),
        "python_base_binary_sha256": _base_python_sha256(),
        "python_framework": sysconfig.get_config_var("PYTHONFRAMEWORK") or None,
        "python_hash_seed": os.environ.get("PYTHONHASHSEED"),
    }


def verify(require_official_interpreter: bool = True) -> dict:
    errors = []
    expected_python_text = ".".join(str(part) for part in EXPECTED_PYTHON)

    if sys.version_info[:3] != EXPECTED_PYTHON:
        errors.append(f"Python {platform.python_version()} != {expected_python_text}")
    if platform.python_implementation() != "CPython":
        errors.append(f"Interpreter {platform.python_implementation()} != CPython")
    if platform.system() != "Darwin":
        errors.append(f"Platform {platform.system()} != Darwin")
    if platform.machine() != EXPECTED_ARCHITECTURE:
        errors.append(f"Architecture {platform.machine()} != {EXPECTED_ARCHITECTURE}")
    if sys.prefix == sys.base_prefix:
        errors.append("Build interpreter is not running in an isolated virtual environment")
    if os.environ.get("PYTHONHASHSEED") != EXPECTED_PYTHON_HASH_SEED:
        errors.append(f"PYTHONHASHSEED must be {EXPECTED_PYTHON_HASH_SEED} before interpreter startup")
    if PYTHON_VERSION_FILE.read_text(encoding="utf-8").strip() != expected_python_text:
        errors.append(".python-version does not match the enforced interpreter")

    locked = locked_distributions()
    installed = installed_distributions()
    for name, version in locked.items():
        if installed.get(name) != version:
            errors.append(f"{name} {installed.get(name, 'missing')} != {version}")

    allowed = set(locked) | {"pip"}
    unexpected = sorted(set(installed) - allowed)
    if unexpected:
        errors.append(f"Unexpected distributions: {', '.join(unexpected)}")
    if installed.get("pip") != EXPECTED_PIP:
        errors.append(f"pip {installed.get('pip', 'missing')} != {EXPECTED_PIP}")

    if require_official_interpreter:
        if sysconfig.get_config_var("PYTHONFRAMEWORK") != "Python":
            errors.append("Artifact builds require the official Python framework distribution")
        base_python_sha256 = _base_python_sha256()
        if base_python_sha256 != EXPECTED_PYTHON_FRAMEWORK_SHA256:
            errors.append(
                "Python framework binary SHA-256 "
                f"{base_python_sha256 or 'missing'} != {EXPECTED_PYTHON_FRAMEWORK_SHA256}"
            )

    if errors:
        raise RuntimeError("Invalid build environment:\n- " + "\n- ".join(errors))
    return normalized_manifest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    parser.add_argument(
        "--validation-only",
        action="store_true",
        help="Verify the exact ABI/dependency set without requiring the release interpreter artifact",
    )
    args = parser.parse_args()

    manifest = verify(require_official_interpreter=not args.validation_only)
    rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
