"""Build a small, deterministic skill archive without contacting any service."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT, output=None):
    root = Path(root).resolve()
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must be a plain semantic version")
    files = {
        "SKILL.md": (root / "SKILL.md").read_bytes(),
        "LICENSE": (root / "LICENSE").read_bytes(),
        "README.md": (root / "docs" / "QUICKSTART.md").read_bytes(),
    }
    manifest = {
        "schema_version": 1,
        "name": "deepseek-efficient",
        "version": version,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
    }
    files["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("deepseek-efficient/" + name, (2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    payload = stream.getvalue()
    filename = "deepseek-efficient-v" + version + ".zip"
    digest = hashlib.sha256(payload).hexdigest()
    result = {"version": version, "filename": filename, "sha256": digest, "size": len(payload)}
    if output is not None:
        output = Path(output).resolve()
        output.mkdir(parents=True, exist_ok=True)
        (output / filename).write_bytes(payload)
        (output / "SHA256SUMS").write_text(digest + "  " + filename + "\n", encoding="utf-8", newline="\n")
    return payload, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    _, result = build(output=args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
