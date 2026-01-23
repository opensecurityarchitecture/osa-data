#!/usr/bin/env python3
"""
OSA Pattern Extractor
Extracts security architecture patterns from opensecurityarchitecture.org
and converts them to structured JSON format.

Usage:
    python extract_patterns.py                    # Extract all patterns
    python extract_patterns.py --pattern SP-011   # Extract single pattern
    python extract_patterns.py --list             # List available patterns
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString

BASE_URL = "https://www.opensecurityarchitecture.org"
PATTERN_LANDSCAPE_URL = f"{BASE_URL}/library/patternlandscape?limit=100"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "patterns")
DELAY_BETWEEN_REQUESTS = 1  # Be nice to the server


@dataclass
class Control:
    id: str
    name: str
    family: str


@dataclass
class Reference:
    title: str
    url: Optional[str] = None


@dataclass
class PatternMetadata:
    release: str = ""
    classification: str = ""
    status: str = "published"
    type: str = "pattern"
    datePublished: Optional[str] = None
    dateModified: Optional[str] = None
    authors: list = field(default_factory=list)
    reviewers: list = field(default_factory=list)


@dataclass
class PatternContent:
    description: str = ""
    keyControlAreas: list = field(default_factory=list)
    assumptions: str = ""
    typicalChallenges: str = ""
    indications: str = ""
    contraIndications: str = ""
    threatResistance: str = ""


@dataclass
class Pattern:
    id: str
    slug: str
    joomla_id: int
    title: str
    description: str
    url: str
    metadata: PatternMetadata
    diagram: dict = field(default_factory=dict)
    legend: str = ""
    content: PatternContent = field(default_factory=PatternContent)
    examples: dict = field(default_factory=dict)
    references: list = field(default_factory=list)
    relatedPatterns: list = field(default_factory=list)
    relatedPatternNames: list = field(default_factory=list)
    controls: list = field(default_factory=list)
    controlFamilySummary: dict = field(default_factory=dict)


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a page and return parsed BeautifulSoup object."""
    print(f"  Fetching: {url}")
    headers = {
        "User-Agent": "OSA-Pattern-Extractor/1.0 (modernisation project)"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_pattern_list() -> list[dict]:
    """Get list of all patterns from the pattern landscape page."""
    soup = fetch_page(PATTERN_LANDSCAPE_URL)
    patterns = []

    # Find all pattern links in the content area
    for link in soup.select('a[href*="/library/patternlandscape/"]'):
        href = link.get("href", "")
        if "/library/patternlandscape/" in href and href != "/library/patternlandscape":
            # Extract joomla_id and slug from URL like /library/patternlandscape/251-pattern-cloud-computing
            match = re.search(r"/library/patternlandscape/(\d+)-(.+)$", href)
            if match:
                joomla_id = int(match.group(1))
                slug = match.group(2)
                title = link.get_text(strip=True)

                # Avoid duplicates
                if not any(p["joomla_id"] == joomla_id for p in patterns):
                    patterns.append({
                        "joomla_id": joomla_id,
                        "slug": slug,
                        "title": title,
                        "url": urljoin(BASE_URL, href)
                    })

    return patterns


def extract_pattern_id(title: str, slug: str) -> str:
    """Extract pattern ID from title or generate from slug."""
    # Try to extract SP-XXX from title
    match = re.search(r"(SP-\d{3}(?:\.\d+)?)", title)
    if match:
        return match.group(1)

    # Try to extract from slug like 0802pattern-001
    match = re.search(r"0802pattern-?(\d+)", slug)
    if match:
        num = int(match.group(1))
        return f"SP-{num:03d}"

    # Try module patterns
    if "module" in slug.lower():
        match = re.search(r"sp-(\d+)", slug)
        if match:
            return f"SP-{int(match.group(1)):03d}"

    # Fallback: generate from slug
    slug_clean = slug.replace("pattern-", "").replace("0802", "")
    return f"SP-{slug_clean[:10]}"


def extract_text_between_headers(soup: BeautifulSoup, start_text: str, end_texts: list[str] = None) -> str:
    """Extract text content between two h3 headers."""
    content_parts = []
    capturing = False

    article = soup.select_one("article") or soup

    for element in article.descendants:
        if hasattr(element, "name"):
            if element.name == "h3":
                header_text = element.get_text(strip=True).lower()
                if start_text.lower() in header_text:
                    capturing = True
                    continue
                elif capturing and end_texts:
                    for end_text in end_texts:
                        if end_text.lower() in header_text:
                            capturing = False
                            break
                elif capturing:
                    capturing = False

            if capturing and element.name in ["p", "li", "div"]:
                text = element.get_text(strip=True)
                if text and text not in content_parts:
                    content_parts.append(text)

    return "\n\n".join(content_parts)


def extract_controls(soup: BeautifulSoup) -> list[Control]:
    """Extract NIST controls from pattern page."""
    controls = []
    seen = set()

    # Find control links
    for link in soup.select('a[href*="control-catalogue"]'):
        href = link.get("href", "")
        text = link.get_text(strip=True)

        # Parse control ID and name from text like "AC-01 Access Control Policies and Procedures"
        match = re.match(r"([A-Z]{2}-\d{2})\s+(.+)", text)
        if match:
            control_id = match.group(1)
            control_name = match.group(2)
            family = control_id.split("-")[0]

            if control_id not in seen:
                seen.add(control_id)
                controls.append(Control(
                    id=control_id,
                    name=control_name,
                    family=family
                ))

    # Sort by family then number
    controls.sort(key=lambda c: (c.family, int(c.id.split("-")[1])))
    return controls


def extract_diagram_paths(soup: BeautifulSoup) -> dict:
    """Extract SVG and PNG diagram paths."""
    diagram = {}

    # Look for SVG object
    svg_obj = soup.select_one('object[type="image/svg+xml"]')
    if svg_obj and svg_obj.get("data"):
        diagram["svg"] = svg_obj["data"]

    # Look for PNG fallback
    png_img = soup.select_one('object img[src*=".png"]')
    if png_img:
        diagram["png"] = png_img["src"]
    else:
        # Try standalone img
        for img in soup.select('img[src*="Pattern"]'):
            src = img.get("src", "")
            if ".png" in src:
                diagram["png"] = src
                break

    return diagram


def extract_metadata_from_schema(soup: BeautifulSoup) -> dict:
    """Extract metadata from schema.org JSON-LD."""
    metadata = {}

    script = soup.select_one('script[type="application/ld+json"]')
    if script:
        try:
            data = json.loads(script.string)
            graph = data.get("@graph", [])
            for item in graph:
                if item.get("@type") == "Article":
                    if "datePublished" in item:
                        metadata["datePublished"] = item["datePublished"][:10]
                    if "dateModified" in item:
                        metadata["dateModified"] = item["dateModified"][:10]
        except (json.JSONDecodeError, TypeError):
            pass

    # Also check meta tags
    for meta in soup.select('meta[property="datePublished"], meta[property="dateModified"]'):
        prop = meta.get("property")
        content = meta.get("content", "")[:10]
        if prop and content:
            metadata[prop] = content

    # Check article meta
    article = soup.select_one("article")
    if article:
        date_mod = article.select_one('meta[property="dateModified"]')
        if date_mod:
            metadata["dateModified"] = date_mod.get("content", "")[:10]
        date_pub = article.select_one('meta[property="datePublished"]')
        if date_pub:
            metadata["datePublished"] = date_pub.get("content", "")[:10]
        author = article.select_one('meta[property="author"]')
        if author:
            metadata["author"] = author.get("content", "")

    return metadata


def extract_field_from_text(text: str, field_name: str) -> str:
    """Extract a field value from text like 'Assumptions: blah blah'."""
    patterns = [
        rf"\*\*{field_name}\*\*:\s*(.+?)(?=\*\*[A-Z]|\Z)",
        rf"<strong>{field_name}</strong>:\s*(.+?)(?=<strong>|\Z)",
        rf"{field_name}:\s*(.+?)(?=\n[A-Z][a-z]+:|\Z)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

    return ""


def extract_references(soup: BeautifulSoup) -> list[Reference]:
    """Extract external references."""
    references = []
    seen_urls = set()

    # Find the references section
    content = soup.select_one("article .uk-margin-medium-top, article div[property='text']")
    if not content:
        content = soup

    text = str(content)

    # Look for reference section
    ref_match = re.search(r"References\*?\*?:(.+?)(?=Related patterns|Classification|Release|\Z)",
                          text, re.IGNORECASE | re.DOTALL)

    if ref_match:
        ref_section = ref_match.group(1)
        # Find all links in the reference section
        ref_soup = BeautifulSoup(ref_section, "html.parser")

        for link in ref_soup.find_all("a"):
            url = link.get("href", "")
            title = link.get_text(strip=True)

            if url and url.startswith("http") and url not in seen_urls:
                seen_urls.add(url)
                # Try to get surrounding text as title if link text is just URL
                if title == url or not title:
                    title = url.split("/")[-1][:50]

                references.append(Reference(title=title, url=url))

    return references


def parse_authors_reviewers(text: str) -> tuple[list, list]:
    """Parse authors and reviewers from text."""
    authors = []
    reviewers = []

    # Authors
    match = re.search(r"Authors?\*?\*?:\s*([^\n<]+)", text, re.IGNORECASE)
    if match:
        authors = [a.strip() for a in re.split(r"[,;]", match.group(1)) if a.strip()]

    # Reviewers
    match = re.search(r"Reviewers?\(s\)\*?\*?:\s*([^\n<]+)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"Reviewers?\*?\*?:\s*([^\n<]+)", text, re.IGNORECASE)
    if match:
        reviewers = [r.strip() for r in re.split(r"[,;]", match.group(1)) if r.strip()]

    return authors, reviewers


def extract_pattern(pattern_info: dict) -> Pattern:
    """Extract full pattern data from a pattern page."""
    soup = fetch_page(pattern_info["url"])

    # Get article content
    article = soup.select_one("article")
    if not article:
        article = soup

    article_text = article.get_text()
    article_html = str(article)

    # Extract basic info
    title = pattern_info["title"]
    h1 = soup.select_one("h1")
    if h1:
        title = h1.get_text(strip=True)

    pattern_id = extract_pattern_id(title, pattern_info["slug"])

    # Get meta description
    meta_desc = soup.select_one('meta[name="description"]')
    description = meta_desc["content"] if meta_desc else ""

    # Extract schema metadata
    schema_meta = extract_metadata_from_schema(soup)

    # Parse authors/reviewers
    authors, reviewers = parse_authors_reviewers(article_html)

    # Extract release and classification
    release_match = re.search(r"Release\*?\*?:\s*(\S+)", article_html)
    release = release_match.group(1) if release_match else "08.02"

    class_match = re.search(r"Classification\*?\*?:\s*([^<\n]+)", article_html)
    classification = class_match.group(1).strip() if class_match else ""

    # Determine status
    status = "published"
    if "draft" in title.lower() or "draft" in pattern_info["slug"]:
        status = "draft"
    elif "reserved" in title.lower() or "reserved" in pattern_info["slug"]:
        status = "reserved"

    # Determine type
    pattern_type = "module" if "module" in title.lower() or "module" in pattern_info["slug"] else "pattern"

    # Build metadata
    metadata = PatternMetadata(
        release=release,
        classification=classification,
        status=status,
        type=pattern_type,
        datePublished=schema_meta.get("datePublished"),
        dateModified=schema_meta.get("dateModified"),
        authors=authors or [schema_meta.get("author", "Unknown")],
        reviewers=reviewers
    )

    # Extract diagram
    diagram = extract_diagram_paths(soup)

    # Extract legend
    legend = ""
    legend_h3 = article.find("h3", string=re.compile(r"Legend", re.IGNORECASE))
    if legend_h3:
        next_elem = legend_h3.find_next_sibling()
        if next_elem and next_elem.name == "p":
            legend = next_elem.get_text(strip=True)

    # Extract main description
    desc_text = ""
    desc_h3 = article.find("h3", string=re.compile(r"Description", re.IGNORECASE))
    if desc_h3:
        parts = []
        for sibling in desc_h3.find_next_siblings():
            if sibling.name == "h3":
                break
            if sibling.name in ["p", "ul", "div"]:
                text = sibling.get_text(strip=True)
                if text:
                    parts.append(text)
        desc_text = "\n\n".join(parts)

    # Extract key control areas
    key_areas = []
    key_h3 = article.find("h3", string=re.compile(r"Key control", re.IGNORECASE))
    if key_h3:
        for sibling in key_h3.find_next_siblings():
            if sibling.name == "h3":
                break
            if sibling.name == "ul":
                for li in sibling.find_all("li"):
                    text = li.get_text(strip=True)
                    if text:
                        key_areas.append(text)

    # Extract other content fields from the HTML
    assumptions = extract_field_from_text(article_html, "Assumptions")
    challenges = extract_field_from_text(article_html, "Typical challenges")
    indications = extract_field_from_text(article_html, "Indications")
    contra = extract_field_from_text(article_html, "Contra-indications")
    threat_resist = extract_field_from_text(article_html, "Resistance against threats")

    content = PatternContent(
        description=desc_text,
        keyControlAreas=key_areas,
        assumptions=assumptions,
        typicalChallenges=challenges,
        indications=indications,
        contraIndications=contra,
        threatResistance=threat_resist
    )

    # Extract references
    references = extract_references(soup)

    # Extract related patterns
    related_patterns = []
    related_names = []
    related_match = re.search(r"Related patterns\*?\*?:\s*([^<\n.]+)", article_html, re.IGNORECASE)
    if related_match:
        related_text = related_match.group(1)
        # Try to find pattern references
        for name in re.split(r"[,;]", related_text):
            name = name.strip()
            if name:
                related_names.append(name)

    # Extract controls
    controls = extract_controls(soup)

    # Build control family summary
    family_summary = {}
    for ctrl in controls:
        family_summary[ctrl.family] = family_summary.get(ctrl.family, 0) + 1

    return Pattern(
        id=pattern_id,
        slug=pattern_info["slug"],
        joomla_id=pattern_info["joomla_id"],
        title=title.replace(f"{pattern_id}: ", "").replace(f"{pattern_id} ", ""),
        description=description,
        url=pattern_info["url"],
        metadata=metadata,
        diagram=diagram,
        legend=legend,
        content=content,
        references=[asdict(r) for r in references],
        relatedPatterns=related_patterns,
        relatedPatternNames=related_names,
        controls=[asdict(c) for c in controls],
        controlFamilySummary=family_summary
    )


def pattern_to_dict(pattern: Pattern) -> dict:
    """Convert Pattern dataclass to dict for JSON serialization."""
    d = asdict(pattern)
    d["$schema"] = "../schema/pattern.schema.json"

    # Convert metadata
    d["metadata"] = asdict(pattern.metadata)

    # Convert content
    d["content"] = asdict(pattern.content)

    # Clean up empty values
    if not d["diagram"]:
        del d["diagram"]
    if not d["legend"]:
        del d["legend"]
    if not d["examples"]:
        del d["examples"]
    if not d["relatedPatterns"]:
        del d["relatedPatterns"]
    if not d["relatedPatternNames"]:
        del d["relatedPatternNames"]

    return d


def save_pattern(pattern: Pattern):
    """Save pattern to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    filename = f"{pattern.id}-{pattern.slug}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    data = pattern_to_dict(pattern)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filepath}")
    return filepath


def main():
    global OUTPUT_DIR

    parser = argparse.ArgumentParser(description="Extract OSA security patterns to JSON")
    parser.add_argument("--pattern", "-p", help="Extract single pattern by ID (e.g., SP-011)")
    parser.add_argument("--list", "-l", action="store_true", help="List available patterns")
    parser.add_argument("--output", "-o", help="Output directory", default=OUTPUT_DIR)
    args = parser.parse_args()

    OUTPUT_DIR = args.output

    print("OSA Pattern Extractor")
    print("=" * 50)

    # Get pattern list
    print("\nFetching pattern list...")
    patterns = get_pattern_list()
    print(f"Found {len(patterns)} patterns")

    if args.list:
        print("\nAvailable patterns:")
        for p in patterns:
            print(f"  {p['joomla_id']:3d}: {p['title']}")
        return

    if args.pattern:
        # Find matching pattern
        target_id = args.pattern.upper()
        matching = None
        for p in patterns:
            pid = extract_pattern_id(p["title"], p["slug"])
            if pid == target_id:
                matching = p
                break

        if not matching:
            print(f"Pattern {target_id} not found")
            sys.exit(1)

        patterns = [matching]

    # Extract patterns
    print(f"\nExtracting {len(patterns)} pattern(s)...")

    extracted = []
    errors = []

    for i, pattern_info in enumerate(patterns, 1):
        print(f"\n[{i}/{len(patterns)}] {pattern_info['title']}")
        try:
            pattern = extract_pattern(pattern_info)
            filepath = save_pattern(pattern)
            extracted.append({
                "id": pattern.id,
                "title": pattern.title,
                "controls": len(pattern.controls),
                "file": filepath
            })

            if i < len(patterns):
                time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            print(f"  ERROR: {e}")
            errors.append({
                "pattern": pattern_info,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 50)
    print("EXTRACTION COMPLETE")
    print("=" * 50)
    print(f"Extracted: {len(extracted)}")
    print(f"Errors: {len(errors)}")

    if extracted:
        total_controls = sum(p["controls"] for p in extracted)
        print(f"Total controls mapped: {total_controls}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  - {err['pattern']['title']}: {err['error']}")

    # Write manifest
    manifest_path = os.path.join(OUTPUT_DIR, "_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source": BASE_URL,
            "patterns": extracted,
            "errors": errors
        }, f, indent=2)
    print(f"\nManifest: {manifest_path}")


if __name__ == "__main__":
    main()
