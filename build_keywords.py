#!/usr/bin/env python3
"""
Usage:
  1) pip install robotframework
  2) Ensure external libraries are installed (e.g. SeleniumLibrary).
  3) Generate per-library libdoc JSON files manually:
       python -m robot.libdoc SeleniumLibrary data/SeleniumLibrary.json
     or let your pipeline produce data/*.json files.
  4) Run:
       python build_keywords.py
This will merge data/*.json -> data/keywords.json
"""

import json
import subprocess
import sys
import os
import re
import argparse
from pathlib import Path
from urllib.parse import quote

def run_libdoc(lib, out):
    # produce JSON libdoc (if desired). Keep this available but not auto-invoked here.
    cmd = [sys.executable, '-m', 'robot.libdoc', lib, out]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def slugify_anchor(name):
    # Use percent-encoding for safety (preserves casing, spaces -> %20, etc.)
    # This is a best-effort approach; some libraries may use different anchor schemes.
    if not name:
        return ''
    return quote(name, safe='')

# Map library "stem" names to base documentation pages.
LIB_DOC_BASE = {
    'Browser': 'https://marketsquare.github.io/robotframework-browser/Browser.html',
    'BuiltIn': 'https://robotframework.org/robotframework/latest/libraries/BuiltIn.html',
    'Collections': 'https://robotframework.org/robotframework/latest/libraries/Collections.html',
    'Database': 'https://marketsquare.github.io/Robotframework-Database-Library/',
    'DateTime': 'https://robotframework.org/robotframework/latest/libraries/DateTime.html',
    'FakerLibrary': 'https://marketsquare.github.io/robotframework-faker/FakerLibrary.html',
    'OperatingSystem': 'https://robotframework.org/robotframework/latest/libraries/OperatingSystem.html',
    'Process': 'https://robotframework.org/robotframework/latest/libraries/Process.html',
    'RequestsLibrary': 'https://marketsquare.github.io/robotframework-requests/doc/RequestsLibrary.html',
    'Screenshot': 'https://robotframework.org/robotframework/latest/libraries/Screenshot.html',
    'SeleniumLibrary': 'https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html',
    'String': 'https://robotframework.org/robotframework/latest/libraries/String.html',
    'XML': 'https://robotframework.org/robotframework/latest/libraries/XML.html'
    # Add mappings for other libraries as needed; keys should match the JSON file stem names in /data.
}

def merge_libdocs(lib, libdoc_json_path):
    with open(libdoc_json_path, 'r', encoding='utf-8') as f:
        doc = json.load(f)
    results = []
    for kw in doc.get('keywords', []):
        name = kw.get('name')
        args = kw.get('args') or []
        docstr = kw.get('doc') or ''
        url = ''
        base = LIB_DOC_BASE.get(lib)
        if base:
            anchor = slugify_anchor(name)
            # If base already contains an anchor scheme different from '#', still append '#'
            url = f"{base}#{anchor}"
        results.append({
            'name': name,
            'library': lib,
            'args': args,
            'doc': docstr.strip(),
            'url': url
        })
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='data/keywords.json', help='Output merged JSON')
    parser.add_argument('--data-dir', default='data', help='Directory containing per-library json libdocs')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Data directory {data_dir} not found. Create it and place per-library libdoc JSON files there.")
        sys.exit(1)

    merged = []

    # Detect all libraries from data/*.json (excluding keywords.json)
    lib_json_files = sorted([f for f in data_dir.glob('*.json') if f.name != Path(args.out).name])
    libs = [f.stem for f in lib_json_files]

    print("Detected library json files:", [str(x.name) for x in lib_json_files])
    if not libs:
        print("No per-library JSON files found in data/. To create them run e.g.:\n  python -m robot.libdoc SeleniumLibrary data/SeleniumLibrary.json")
        sys.exit(1)

    for lib in libs:
        out_file = data_dir / f"{lib}.json"
        if not out_file.exists():
            print(f"Skipping {lib} because {out_file} not found.")
            continue
        print(f"Merging {out_file} ...")
        try:
            merged += merge_libdocs(lib, out_file)
        except Exception as e:
            print(f"Error processing {out_file}: {e}")

    # sort by library then name
    merged = sorted(merged, key=lambda k: (k['library'] or '', (k['name'] or '').lower()))
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print("Wrote", out_path)
    print("Tip: review the generated URLs in the file; some anchors may need manual correction depending on the library's documentation anchor scheme.")

if __name__ == '__main__':
    main()
