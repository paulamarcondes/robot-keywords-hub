#!/usr/bin/env python3
"""
Merge per-library libdoc JSON files into a single data/keywords.json
with robust argument detection.

This version uses Phase 1 (strict libdoc check) for all libraries.
It only runs the docstring fallback (Phase 2) specifically for 
RequestsLibrary keywords, which have historically poor libdoc data.

Usage:
  python build_keywords.py
"""

import os
import json
import re
from urllib.parse import quote

# --- Configuration and Helpers ---

DATA_FOLDER = "data"
OUTPUT_FILE = os.path.join(DATA_FOLDER, "keywords.json")

def slugify_anchor(name):
    """Percent-encodes the keyword name to create a safe URL anchor."""
    if not name:
        return ''
    # Use percent-encoding for safety (preserves casing, spaces -> %20, etc.)
    return quote(name, safe='')

# Map library "stem" names to base documentation pages.
LIB_DOC_BASE = {
    'Browser': 'https://marketsquare.github.io/robotframework-browser/Browser.html',
    'BuiltIn': 'https://robotframework.org/robotframework/latest/libraries/BuiltIn.html',
    'Collections': 'https://robotframework.org/robotframework/latest/libraries/Collections.html',
    'DatabaseLibrary': 'https://marketsquare.github.io/Robotframework-Database-Library/',
    'DateTime': 'https://robotframework.org/robotframework/latest/libraries/DateTime.html',
    'FakerLibrary': 'https://marketsquare.github.io/robotframework-faker/',
    'OperatingSystem': 'https://robotframework.org/robotframework/latest/libraries/OperatingSystem.html',
    'Process': 'https://robotframework.org/robotframework/latest/libraries/Process.html',
    'RequestsLibrary': 'https://marketsquare.github.io/robotframework-requests/doc/RequestsLibrary.html',
    'Screenshot': 'https://robotframework.org/robotframework/latest/libraries/Screenshot.html',
    'SeleniumLibrary': 'https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html',
    'String': 'https://robotframework.org/robotframework/latest/libraries/String.html',
    'XML': 'https://robotframework.org/robotframework/latest/libraries/XML.html'
}

# List of arguments common in the documentation but known to be optional (used for RequestsLibrary filtering)
OPTIONAL_DOC_ARGS = [
    "params", "data", "json", "headers", "cookies", "files", 
    "auth", "timeout", "allow_redirects", "proxies", 
    "verify", "cert", "expected_status", "msg", "any", "anything", 
    "session", "name", "value", "attributes", "kwargs",
    "ALL", "NONE", "TRUE", "FALSE" 
]

# --- Main Logic ---

libraries = [
    f for f in os.listdir(DATA_FOLDER)
    if f.endswith(".json") and f != "keywords.json"
]

all_keywords = []

for lib_file in libraries:
    lib_path = os.path.join(DATA_FOLDER, lib_file)
    with open(lib_path, "r", encoding="utf-8") as f:
        lib_data = json.load(f)

    lib_name = lib_data.get("name") or lib_file.replace(".json", "")

    for kw in lib_data.get("keywords", []):
        kw_name = kw.get("name", "")
        kw_doc = kw.get("doc", "").strip() or "No documentation available."
        args = kw.get("args", [])

        # 1. Argument Processing - Phase 1: Strict Libdoc Check (The default, correct method)
        arg_reprs = [arg.get("repr", "") for arg in args]

        # Detect required arguments (no '=' and not *args/**kwargs)
        required_args = [
            arg.get("name")
            for arg in args
            if "=" not in arg.get("repr", "") # Must not have an equals sign (i.e., no default value)
            and not arg.get("repr", "").startswith("*") # Must not be varargs (*args)
            and not arg.get("repr", "").startswith("**") # Must not be kwargs (**kwargs)
        ]

        # Phase 2: Fallback — ONLY for RequestsLibrary, where libdoc data is often sparse
        if not required_args and lib_name == "RequestsLibrary" and "code>" in kw_doc:
            
            code_args = re.findall(r"<code>([a-zA-Z_][a-zA-Z0-9_]*)</code>", kw_doc)
            
            # Filter the doc-extracted args to remove known optionals (case-insensitive check)
            optional_lower = [o.lower() for o in OPTIONAL_DOC_ARGS]
            
            filtered_code_args = [
                a for a in code_args
                if a.lower() not in optional_lower 
                and a.lower() not in ("get", "post", "put", "delete", "patch", "head")
            ]

            # Use the filtered list as the required arguments
            required_args = list(dict.fromkeys(filtered_code_args))
            
            
        # 2. URL Generation
        url = ""
        base = LIB_DOC_BASE.get(lib_name)
        if base:
            anchor = slugify_anchor(kw_name)
            # Ensure proper separator for anchor links
            separator = ''
            if not base.endswith('/') and not base.endswith('.html'):
                separator = '/' 
                
            url = f"{base}{separator}#{anchor}"

        # 3. Create Keyword Entry
        keyword_entry = {
            "name": kw_name,
            "library": lib_name,
            "doc": kw_doc,
            "args": arg_reprs,
            "requiredArgs": required_args,
            "url": url
        }

        all_keywords.append(keyword_entry)

# --- Output ---

all_keywords.sort(key=lambda x: (x["library"], x["name"].lower()))

# Ensure the data directory exists
os.makedirs(DATA_FOLDER, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_keywords, f, indent=2, ensure_ascii=False)

print(f"keywords.json updated successfully with {len(all_keywords)} keywords.")

# --- End ---