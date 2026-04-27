"""
classify_verilog.py

Scans all module folders produced by parse_verilog_db.py under `verilog-db-parsing`,
uses Yosys to classify each Verilog file as COMBINATIONAL or SEQUENTIAL,
then copies the module folder into the appropriate sub-folder under `verilog-db-categories`:

A module is SEQUENTIAL if Yosys detects any flip-flop or latch cells after
running `proc` + `opt` on it. All other synthesisable modules are COMBINATIONAL.

Usage:
    python classify_verilog.py [--parsing-dir verilog-db-parsing] \
                               [--categories-dir verilog-db-categories] \
                               [--yosys yosys]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Cell-type patterns that indicate sequential (stateful) elements
# ---------------------------------------------------------------------------
# Yosys internal cell names after proc+opt:
#   $dff, $adff, $dffe, $adffe, $sdff, $sdffe, $sdffce,
#   $dlatch, $adlatch, $dlatchsr,
#   $mem, $memrd, $memwr  (memory – treated as sequential)
# After techmap (simple_map / full synth), names become e.g. $_DFF_P_, $_DLATCH_N_
SEQUENTIAL_CELL_RE = re.compile(
    r"^\$(adff|dff|sdff|dlatch|adlatch|dlatchsr|mem)"   # internal cells
    r"|^\$_DFF_"                                         # tech-mapped DFFs
    r"|^\$_DLATCH_",                                     # tech-mapped latches
    re.IGNORECASE,
)


def is_sequential(cell_types: dict[str, int]) -> bool:
    """Return True if any cell in the stat report is a sequential element."""
    return any(SEQUENTIAL_CELL_RE.match(cell) for cell in cell_types)


def run_yosys(verilog_path: str, module_name: str, yosys_bin: str) -> tuple[dict | None, str | None]:
    
    verilog_files = [
        os.path.join(os.path.dirname(verilog_path), f)
        for f in os.listdir(os.path.dirname(verilog_path))
        if f.endswith(".v")
    ]

    read_cmd = " ".join(verilog_files)
    
    ys_script = (
        f"read_verilog {read_cmd}\n"
        f"hierarchy -check -top {module_name}\n"
        f"proc\n"
        f"opt\n"
        f"stat -json\n"
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ys", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(ys_script)
        script_path = tmp.name

    try:
        result = subprocess.run(
            [yosys_bin, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
    finally:
        os.unlink(script_path)

    if result.returncode != 0:
        return None, result.stderr.strip()

    stdout = result.stdout
    json_match = re.search(r"^(\{.*?^\})", stdout, re.MULTILINE | re.DOTALL)
    if not json_match:
        return None, "Failed to extract JSON from Yosys output"

    try:
        return json.loads(json_match.group(1)), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {e}"


def classify_module(verilog_path: str, module_name: str, yosys_bin: str) -> tuple[str, str | None]:
    stat, err = run_yosys(verilog_path, module_name, yosys_bin)

    if stat is None:
        return "error", err

    modules = stat.get("modules", {})
    if not modules:
        return "error", "No modules found in Yosys output"

    all_cells: dict[str, int] = {}
    for mod_stat in modules.values():
        for cell, count in mod_stat.get("num_cells_by_type", {}).items():
            all_cells[cell] = all_cells.get(cell, 0) + count

    return (
        "sequential" if is_sequential(all_cells) else "combinational",
        None,
    )


def copy_module_folder(src_folder: str, dst_base: str, module_name: str) -> None:
    """Copy the entire module folder into dst_base/<module_name>."""
    dst = os.path.join(dst_base, module_name)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src_folder, dst)


def main():

    parser = argparse.ArgumentParser(
        description="Classify Verilog modules (combinational vs sequential) using Yosys."
    )
    parser.add_argument(
        "--parsing-dir",
        default="verilog-db-parsing",
        help="Input directory produced by parse_verilog_db.py",
    )
    parser.add_argument(
        "--categories-dir",
        default="verilog-db-categories",
        help="Output directory for categorised modules",
    )
    parser.add_argument(
        "--yosys",
        default="yosys",
        help="Path to the Yosys executable",
    )
    args = parser.parse_args()

    parsing_dir = args.parsing_dir
    categories_dir = args.categories_dir
    yosys_bin = args.yosys

    # Validate inputs
    if not shutil.which(yosys_bin):
        print(f"[ERROR] Yosys not found: '{yosys_bin}'", file=sys.stderr)
        print("        Install with: sudo apt install yosys or brew install yosys", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(parsing_dir):
        print(f"[ERROR] Parsing directory not found: '{parsing_dir}'", file=sys.stderr)
        sys.exit(1)

    # Prepare output directories
    comb_dir = os.path.join(categories_dir, "combinational")
    seq_dir  = os.path.join(categories_dir, "sequential")
    os.makedirs(comb_dir, exist_ok=True)
    os.makedirs(seq_dir,  exist_ok=True)

    # Discover modules
    module_folders = sorted(
        entry.name
        for entry in os.scandir(parsing_dir)
        if entry.is_dir()
    )

    if not module_folders:
        print(f"[WARN] No module folders found in '{parsing_dir}'.")
        sys.exit(0)

    print(f"Found {len(module_folders)} module(s) in '{parsing_dir}'.\n")

    counts = {"combinational": 0, "sequential": 0, "error": 0}

    # Progress bar
    pbar = tqdm(module_folders, desc="Processing modules", unit="module")

    def update_bar():
        pbar.set_postfix({
            "comb": counts["combinational"],
            "seq": counts["sequential"],
            "err": counts["error"],
        })

    for module_name in pbar:
        module_dir = os.path.join(parsing_dir, module_name)
        verilog_file = os.path.join(module_dir, f"{module_name}.v")

        # Missing file
        if not os.path.isfile(verilog_file):
            tqdm.write(f"  {module_name:<35} {'—':<15} [SKIP] No .v file found")
            counts["error"] += 1
            update_bar()
            continue

        # Classify
        category, err = classify_module(verilog_file, module_name, yosys_bin)

        if category in counts:
            counts[category] += 1
        else:
            counts["error"] += 1

        # Route result
        if category == "combinational":
            dst_base = comb_dir
        elif category == "sequential":
            dst_base = seq_dir
        else:
            tqdm.write(
                f"  {module_name:<35} {'error':<15} [FAIL]\n"
                f"    Reason: {err or 'Unknown error'}\n"
                f"    File: {verilog_file}"
            )
            update_bar()
            continue

        copy_module_folder(module_dir, dst_base, module_name)

        # Update progress stats
        update_bar()

    # Summary
    print()
    print("=" * 60)
    print(f"  Sequential    : {counts['sequential']}")
    print(f"  Combinational : {counts['combinational']}")
    print(f"  Errors/Skipped: {counts['error']}")
    print(f"\nOutput written to: '{os.path.abspath(categories_dir)}'")
    print(f"  {os.path.abspath(comb_dir)}")
    print(f"  {os.path.abspath(seq_dir)}")


if __name__ == "__main__":
    main()