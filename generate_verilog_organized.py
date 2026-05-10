#!/usr/bin/env python3
"""
Generate Verilog and Organize into Full-Adder Collection Structure
- Generate Verilog from .txt descriptions
- Copy ground truth .v files
- Organize into structured folders: modulename/
  ├─ modulename.txt (description)
  ├─ modulename.v (ground truth)
  └─ modulename_generated.v (LLM generated)
"""

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import requests
from datetime import datetime

# Configuration
COLLECTION_PATH = Path("D:/master_learning/thesis/VerilogDB/full-adder-collection")
LMSTUDIO_URL = "http://localhost:1234/v1"
MODEL_NAME = "gemma-3-4b"
OUTPUT_DIR = Path("D:/master_learning/thesis/VerilogDB/generated_collection")

OUTPUT_DIR.mkdir(exist_ok=True)

class VerilogGeneratorOrganized:
    def __init__(self, base_url: str = LMSTUDIO_URL):
        self.base_url = base_url
        self.results = []
        self.generated_count = 0
        self.failed_count = 0

    def call_llm(self, prompt: str, max_tokens: int = 800) -> str:
        """Call LMStudio API to generate Verilog"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": max_tokens,
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"   ❌ LLM Error: {e}")
            return ""

    def extract_verilog(self, response: str) -> str:
        """Extract Verilog code from LLM response"""
        # Try to find code block
        if "```verilog" in response:
            start = response.find("```verilog") + len("```verilog")
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        # If no code block, try to find module definition
        if "module " in response:
            start = response.find("module")
            end = response.rfind("endmodule")
            if end > start:
                return response[start:end+9].strip()

        return response.strip()

    def process_folder(self, folder_path: Path) -> Dict:
        """Process a single folder and generate organized output"""
        txt_files = list(folder_path.glob("*.txt"))
        v_files = list(folder_path.glob("*.v"))

        if not txt_files:
            return {
                "folder": folder_path.name,
                "status": "SKIP",
                "reason": "No .txt file"
            }

        txt_file = txt_files[0]
        with open(txt_file) as f:
            description = f.read().strip()

        if not description:
            return {
                "folder": folder_path.name,
                "status": "SKIP",
                "reason": "Empty description"
            }

        # Get ground truth if available
        ground_truth = ""
        ground_truth_path = None
        if v_files:
            ground_truth_path = v_files[0]
            with open(ground_truth_path) as f:
                ground_truth = f.read().strip()

        print(f"\n{'='*80}")
        print(f"📂 {folder_path.name}")
        print(f"📝 {description[:100]}...")

        # Create output folder structure
        output_folder = OUTPUT_DIR / folder_path.name
        output_folder.mkdir(exist_ok=True)

        # Copy description file
        output_txt = output_folder / f"{folder_path.name}.txt"
        shutil.copy(txt_file, output_txt)
        print(f"   ✅ Copied description")

        # Copy ground truth if exists
        if ground_truth_path:
            output_v = output_folder / f"{folder_path.name}.v"
            shutil.copy(ground_truth_path, output_v)
            print(f"   ✅ Copied ground truth")

        # Generate Verilog
        prompt = f"""You are a Verilog hardware designer. Generate a complete, working Verilog module based on this description:

Description: {description}

IMPORTANT:
1. Return ONLY the module code in ```verilog``` block
2. The module should implement exactly what the description says
3. Use appropriate input/output ports
4. Make the logic correct and synthesizable
5. Do NOT include comments, testbench, or extra text

Generate the Verilog module:"""

        if ground_truth:
            prompt += f"""

Reference (for interface hints only - may not match exactly):
{ground_truth[:500]}"""

        print("🤖 Generating with Gemma 3 4B...", end=" ", flush=True)
        response = self.call_llm(prompt)

        if not response:
            print("❌")
            self.failed_count += 1
            return {
                "folder": folder_path.name,
                "status": "FAILED",
                "reason": "Empty LLM response"
            }

        generated = self.extract_verilog(response)

        if not generated:
            print("❌ (extraction failed)")
            self.failed_count += 1
            return {
                "folder": folder_path.name,
                "status": "FAILED",
                "reason": "Failed to extract Verilog"
            }

        # Check if it looks like valid Verilog
        if "module " not in generated or "endmodule" not in generated:
            print("⚠️  (incomplete)")
            self.failed_count += 1
            status = "PARTIAL"
        else:
            print("✅")
            self.generated_count += 1
            status = "OK"

        # Save generated Verilog
        output_generated = output_folder / f"{folder_path.name}_generated.v"
        with open(output_generated, 'w') as f:
            f.write(generated)
        print(f"   💾 Saved generated code to folder")

        result = {
            "folder": folder_path.name,
            "status": status,
            "description": description,
            "generated": generated,
            "ground_truth": ground_truth,
            "output_folder": str(output_folder)
        }

        self.results.append(result)
        return result

    def generate_summary(self):
        """Generate summary report"""
        total = len(self.results)
        ok_count = sum(1 for r in self.results if r.get("status") == "OK")
        partial_count = sum(1 for r in self.results if r.get("status") == "PARTIAL")
        failed_count = sum(1 for r in self.results if r.get("status") == "FAILED")
        skipped_count = sum(1 for r in self.results if r.get("status") == "SKIP")

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                VERILOG GENERATION & ORGANIZATION REPORT                      ║
║                     Model: Gemma 3 4B (via LMStudio)                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 RESULTS
{'─' * 80}
Total Processed:        {total}
Generated Successfully: {ok_count} ({100*ok_count/total:.1f}%)
Partial/Incomplete:     {partial_count} ({100*partial_count/total:.1f}%)
Failed:                 {failed_count} ({100*failed_count/total:.1f}%)
Skipped:                {skipped_count} ({100*skipped_count/total:.1f}%)

📈 GENERATION RATE: {ok_count}/{total} ({100*ok_count/total:.1f}%)

📁 OUTPUT STRUCTURE
{'─' * 80}
{OUTPUT_DIR}/
├─ modulename1/
│  ├─ modulename1.txt                (description)
│  ├─ modulename1.v                  (ground truth)
│  └─ modulename1_generated.v        (generated code)
├─ modulename2/
├─ ...
└─ (47 total folders)

📋 DETAILED RESULTS
{'─' * 80}
"""

        for i, result in enumerate(self.results, 1):
            status = result.get("status", "UNKNOWN")
            if status == "SKIP":
                report += f"\n[{i}] {result['folder']}\n    Status: SKIP ({result.get('reason', 'unknown')})\n"
            elif status == "FAILED":
                report += f"\n[{i}] {result['folder']}\n    Status: FAILED ({result.get('reason', 'unknown')})\n"
            else:
                report += f"\n[{i}] {result['folder']}\n    Status: {status}\n    Folder: {result.get('output_folder', 'N/A')}\n"

        # Save report
        report_path = OUTPUT_DIR / f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(report)

        # Save JSON
        json_path = OUTPUT_DIR / f"generation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(report)
        print(f"\n✅ Report saved to: {report_path}")
        print(f"✅ JSON saved to: {json_path}")
        print(f"\n✅ Generated organized collection in: {OUTPUT_DIR}")
        print(f"\nStructure:")
        print(f"  {OUTPUT_DIR}/")
        print(f"  ├─ modulename1/")
        print(f"  │  ├─ modulename1.txt")
        print(f"  │  ├─ modulename1.v")
        print(f"  │  └─ modulename1_generated.v")
        print(f"  ├─ modulename2/")
        print(f"  └─ ... (47 total)")

    def run(self):
        """Run generation on all folders"""
        folders = sorted([f for f in COLLECTION_PATH.iterdir() if f.is_dir()])

        print(f"""
╔════════════════════════════════════════════════════════════════════════════════╗
║          VERILOG GENERATION - ORGANIZED COLLECTION OUTPUT                     ║
║                                                                                ║
║  Structure:                                                                    ║
║  generated_collection/                                                         ║
║  ├─ modulename/                                                                ║
║  │  ├─ modulename.txt (description)                                           ║
║  │  ├─ modulename.v (ground truth)                                            ║
║  │  └─ modulename_generated.v (LLM generated)                                 ║
║  └─ ... (47 total folders)                                                     ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝

📁 Input: {COLLECTION_PATH}
🤖 Model: {MODEL_NAME} (LMStudio)
📊 Folders: {len(folders)}
💾 Output: {OUTPUT_DIR}

Starting generation...
""")

        for i, folder in enumerate(folders, 1):
            try:
                print(f"[{i:2d}/{len(folders)}]", end=" ")
                self.process_folder(folder)
            except Exception as e:
                print(f"❌ Error: {e}")
                self.results.append({
                    "folder": folder.name,
                    "status": "ERROR",
                    "reason": str(e)
                })

        print("\n" + "="*80)
        self.generate_summary()


def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   Verilog Generation with Organized Collection Output        ║
    ║   Using Gemma 3 4B via LMStudio                              ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    # Check LMStudio connection
    try:
        print("🔌 Checking LMStudio connection...")
        response = requests.get(f"{LMSTUDIO_URL}/models", timeout=5)
        print(f"✅ Connected to LMStudio\n")
    except Exception as e:
        print(f"❌ Cannot connect to LMStudio at {LMSTUDIO_URL}")
        print(f"   Make sure LMStudio is running with {MODEL_NAME} loaded")
        print(f"   Error: {e}")
        return

    # Check collection directory
    if not COLLECTION_PATH.exists():
        print(f"❌ Collection directory not found: {COLLECTION_PATH}")
        return

    # Run generation
    generator = VerilogGeneratorOrganized()
    generator.run()


if __name__ == "__main__":
    main()
