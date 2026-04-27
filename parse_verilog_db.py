"""

Parses all JSON files in the `verilog-db` directory.
For each JSON file, creates a folder named after `module_name` and writes:
  - <module_name>.txt   → the description
  - <module_name>.v     → the verilog_code

Usage:
    python parse_verilog_db.py [--db-dir verilog-db] [--out-dir output]
    
"""

import argparse
import json
import os
import sys
from tqdm import tqdm

def parse_json_file(json_path: str) -> dict:
    """Load and return the parsed JSON from the given path."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_module_files(data: dict, out_base: str) -> None:
    """
    Given a parsed JSON dict and a base output directory, create:
      <out_base>/<module_name>/<module_name>.txt
      <out_base>/<module_name>/<module_name>.v
    """
    module_name = data.get("module_name")
    if not module_name:
        raise ValueError("JSON is missing 'module_name' field.")

    description = data.get("description", "")
    verilog_code = data.get("verilog_code", "")

    # Create the module directory
    module_dir = os.path.join(out_base, module_name)
    os.makedirs(module_dir, exist_ok=True)

    try:
        # Write description .txt
        txt_path = os.path.join(module_dir, f"{module_name}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(description)

        # Write verilog .v
        v_path = os.path.join(module_dir, f"{module_name}.v")
        with open(v_path, "w", encoding="utf-8") as f:
            f.write(verilog_code)

    except Exception as e:
        print(f"[ERROR] Failed to write module '{module_name}': {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Parse verilog-db JSON files into module folders."
    )
    parser.add_argument(
        "--db-dir",
        default="verilog-db",
        help="Path to the directory containing JSON files (default: verilog-db)",
    )
    parser.add_argument(
        "--out-dir",
        default="verilog-db-parsing",
        help="Base output directory for module folders (default: verilog-db-parsing)",
    )
    args = parser.parse_args()

    db_dir = args.db_dir
    out_dir = args.out_dir

    if not os.path.isdir(db_dir):
        print(f"[ERROR] DB directory not found: '{db_dir}'", file=sys.stderr)
        sys.exit(1)

    json_files = [f for f in os.listdir(db_dir) if f.lower().endswith(".json")]

    if not json_files:
        print(f"[WARN] No JSON files found in '{db_dir}'.")
        sys.exit(0)

    print(f"Found {len(json_files)} JSON file(s) in '{db_dir}'.\n")

    success, failed = 0, 0

    for filename in tqdm(sorted(json_files), desc="Processing files", unit="file"):
        json_path = os.path.join(db_dir, filename)
        try:
            data = parse_json_file(json_path)
            write_module_files(data, out_dir)
            success += 1
        except Exception as e:
            tqdm.write(f"[ERROR] Failed to process '{filename}': {e}")
            failed += 1

    print("\nDone.")
    print(f"{success} succeeded, {failed} failed.")
    print(f"Output written to: '{os.path.abspath(out_dir)}'")


if __name__ == "__main__":
    main()