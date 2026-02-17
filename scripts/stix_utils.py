#!/usr/bin/env python3
"""
Shared STIX utilities for TRIDENT data enrichment scripts.

Downloads and caches ATT&CK Enterprise STIX bundle from:
  https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json

Provides lookup functions for techniques, actors, and detection strategies.
"""

import json
import os
from pathlib import Path
from urllib.request import urlretrieve

CACHE_DIR = Path("/tmp/osa-stix-cache")
STIX_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"
STIX_CACHE_PATH = CACHE_DIR / "enterprise-attack.json"


def download_stix_bundle() -> dict:
    """Download or load cached ATT&CK Enterprise STIX bundle."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if STIX_CACHE_PATH.exists():
        size_mb = STIX_CACHE_PATH.stat().st_size / 1024 / 1024
        print(f"  Using cached STIX bundle ({size_mb:.1f} MB)")
    else:
        print(f"  Downloading ATT&CK STIX bundle...")
        urlretrieve(STIX_URL, STIX_CACHE_PATH)
        size_mb = STIX_CACHE_PATH.stat().st_size / 1024 / 1024
        print(f"  Downloaded {size_mb:.1f} MB")

    print("  Loading STIX bundle...")
    with open(STIX_CACHE_PATH, 'r', encoding='utf-8') as f:
        bundle = json.load(f)

    print(f"  Loaded {len(bundle.get('objects', []))} STIX objects")
    return bundle


def build_technique_lookup(bundle: dict) -> dict:
    """Build {technique_external_id: stix_object} lookup for attack-pattern objects.

    Returns dict keyed by ATT&CK ID (e.g., 'T1001', 'T1001.001') with STIX object as value.
    Only includes non-revoked, non-deprecated enterprise techniques.
    """
    lookup = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "attack-pattern":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        # Get external ID
        ext_refs = obj.get("external_references", [])
        attack_id = None
        for ref in ext_refs:
            if ref.get("source_name") == "mitre-attack":
                attack_id = ref.get("external_id")
                break
        if attack_id:
            lookup[attack_id] = obj

    return lookup


def build_actor_lookup(bundle: dict) -> dict:
    """Build {actor_external_id: stix_object} lookup for intrusion-set objects.

    Returns dict keyed by ATT&CK group ID (e.g., 'G0016') with STIX object as value.
    Only includes non-revoked, non-deprecated groups.
    """
    lookup = {}
    for obj in bundle.get("objects", []):
        if obj.get("type") != "intrusion-set":
            continue
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        ext_refs = obj.get("external_references", [])
        group_id = None
        for ref in ext_refs:
            if ref.get("source_name") == "mitre-attack":
                group_id = ref.get("external_id")
                break
        if group_id:
            lookup[group_id] = obj

    return lookup


def build_detection_lookup(bundle: dict) -> dict:
    """Build {detection_external_id: stix_object} lookup for x-mitre-data-component
    and detection strategy objects.

    ATT&CK v18 uses 'x-mitre-data-component' type for detection strategies.
    Returns dict keyed by DET ID (e.g., 'DET0001').
    """
    lookup = {}
    for obj in bundle.get("objects", []):
        # v18 detection strategies can be x-mitre-data-component or course-of-action with DET prefix
        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        ext_refs = obj.get("external_references", [])
        det_id = None
        for ref in ext_refs:
            if ref.get("source_name") == "mitre-attack":
                ext_id = ref.get("external_id", "")
                if ext_id.startswith("DET"):
                    det_id = ext_id
                    break
        if det_id:
            lookup[det_id] = obj

    return lookup


def clean_description(desc: str, max_length: int = 2000) -> str:
    """Clean and truncate a STIX description string."""
    if not desc:
        return ""

    # Remove citation markers like (Citation: Name Year)
    import re
    desc = re.sub(r'\(Citation:[^)]+\)', '', desc)

    # Clean up whitespace
    desc = re.sub(r'\s+', ' ', desc).strip()

    if len(desc) > max_length:
        desc = desc[:max_length - 3] + "..."

    return desc
