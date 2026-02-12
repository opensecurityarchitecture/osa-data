#!/usr/bin/env node
/**
 * convert-coverage-data.mjs
 *
 * Reads Python data files from osa-strategy/docs/sp800/ and converts them
 * into 14 JSON framework-coverage files at data/framework-coverage/.
 *
 * Run once; JSON becomes the canonical source going forward.
 */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STRATEGY_DIR = resolve(__dirname, '../../osa-strategy/docs/sp800');
const OUTPUT_DIR   = resolve(__dirname, '../data/framework-coverage');

mkdirSync(OUTPUT_DIR, { recursive: true });

const FRAMEWORKS = [
  { id: 'iso_27001_2022',  name: 'ISO 27001:2022',       output: 'iso-27001-2022.json',       variable: 'iso27001_data',            source: 'generate_mappings.py' },
  { id: 'iso_27002_2022',  name: 'ISO 27002:2022',       output: 'iso-27002-2022.json',       variable: 'iso27002_data',            source: 'data_iso27002.py' },
  { id: 'nist_csf_2',      name: 'NIST CSF 2.0',         output: 'nist-csf-2.json',           variable: 'nist_csf_data',            source: 'data_nist_csf.py' },
  { id: 'pci_dss_v4',      name: 'PCI DSS v4.0.1',       output: 'pci-dss-v4.json',           variable: 'pci_dss_data',             source: 'data_pci_dss.py' },
  { id: 'cis_controls_v8', name: 'CIS Controls v8',       output: 'cis-controls-v8.json',      variable: 'cis_data',                 source: 'data_cis.py' },
  { id: 'cobit_2019',      name: 'COBIT 2019',            output: 'cobit-2019.json',           variable: 'cobit_data',               source: 'data_cobit.py' },
  { id: 'finos_ccc',       name: 'FINOS CCC',             output: 'finos-ccc.json',            variable: 'finos_ccc_data',           source: 'data_remaining_part1.py' },
  { id: 'iec_62443',       name: 'IEC 62443',             output: 'iec-62443.json',            variable: 'iec62443_data',            source: 'data_remaining_part1.py' },
  { id: 'nis2',            name: 'NIS2 Directive',         output: 'nis2.json',                 variable: 'nis2_data',                source: 'data_remaining_part1.py' },
  { id: 'uk_pra_fca',      name: 'UK PRA/FCA',             output: 'uk-pra-fca.json',           variable: 'uk_pra_fca_data',          source: 'data_remaining_part2.py' },
  { id: 'mas_trm',         name: 'MAS TRM',                output: 'mas-trm.json',              variable: 'mas_trm_data',             source: 'data_remaining_part2.py' },
  { id: 'apra_cps_234',    name: 'APRA CPS 234',           output: 'apra-cps-234.json',         variable: 'apra_cps234_data',         source: 'data_remaining_part2.py' },
  { id: 'asd_e8',          name: 'ASD Essential Eight',     output: 'asd-essential-eight.json',  variable: 'asd_essential_eight_data', source: 'data_remaining_part3.py' },
  { id: 'bsi_grundschutz', name: 'BSI IT-Grundschutz',     output: 'bsi-grundschutz.json',      variable: 'bsi_grundschutz_data',     source: 'data_remaining_part3.py' },
];

// --- Python parser ---

function extractPythonArray(source, variableName) {
  const pattern = new RegExp(`^${variableName}\\s*=\\s*\\[`, 'm');
  const match = pattern.exec(source);
  if (!match) throw new Error(`Variable "${variableName}" not found`);

  let pos = match.index + match[0].length - 1;
  const arrayStr = extractBracketed(source, pos);

  const items = [];
  let i = 1;
  while (i < arrayStr.length - 1) {
    i = skipWS(arrayStr, i);
    if (i >= arrayStr.length - 1) break;
    if (arrayStr[i] === '[') {
      const inner = extractBracketed(arrayStr, i);
      items.push(parseRow(inner));
      i += inner.length;
    } else {
      i++;
    }
  }
  return items;
}

function extractBracketed(src, start) {
  let depth = 0, i = start;
  while (i < src.length) {
    const ch = src[i];
    if (ch === '"' || ch === "'") { i = skipStr(src, i); continue; }
    if (ch === '#') { while (i < src.length && src[i] !== '\n') i++; continue; }
    if (ch === '[') depth++;
    else if (ch === ']') { depth--; if (depth === 0) return src.slice(start, i + 1); }
    i++;
  }
  throw new Error('Unbalanced brackets');
}

function skipStr(src, start) {
  const q = src[start];
  if (start + 2 < src.length && src[start+1] === q && src[start+2] === q) {
    let i = start + 3;
    while (i < src.length) {
      if (src[i] === '\\') { i += 2; continue; }
      if (src.slice(i, i+3) === q+q+q) return i + 3;
      i++;
    }
  }
  let i = start + 1;
  while (i < src.length) {
    if (src[i] === '\\') { i += 2; continue; }
    if (src[i] === q) return i + 1;
    i++;
  }
  return i;
}

function skipWS(src, pos) {
  while (pos < src.length) {
    const ch = src[pos];
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r' || ch === ',') pos++;
    else if (ch === '#') { while (pos < src.length && src[pos] !== '\n') pos++; }
    else break;
  }
  return pos;
}

function parseRow(listStr) {
  const elems = [];
  let i = 1;
  while (i < listStr.length - 1) {
    i = skipWS(listStr, i);
    if (i >= listStr.length - 1) break;
    const ch = listStr[i];
    if (ch === '"' || ch === "'") {
      const { value, end } = parseStr(listStr, i);
      elems.push(value);
      i = end;
    } else if (ch === '-' || (ch >= '0' && ch <= '9')) {
      let n = '';
      while (i < listStr.length && (listStr[i] === '-' || listStr[i] === '.' || (listStr[i] >= '0' && listStr[i] <= '9'))) {
        n += listStr[i]; i++;
      }
      elems.push(Number(n));
    } else {
      i++;
    }
  }
  return elems;
}

function parseStr(src, start) {
  const q = src[start];
  if (start+2 < src.length && src[start+1] === q && src[start+2] === q) {
    let i = start + 3, val = '';
    while (i < src.length) {
      if (src[i] === '\\') { val += esc(src, i); i += 2; continue; }
      if (src.slice(i, i+3) === q+q+q) return { value: val, end: i + 3 };
      val += src[i]; i++;
    }
  }
  let i = start + 1, val = '';
  while (i < src.length) {
    if (src[i] === '\\') { val += esc(src, i); i += 2; continue; }
    if (src[i] === q) return { value: val, end: i + 1 };
    val += src[i]; i++;
  }
  return { value: val, end: i };
}

function esc(src, pos) {
  const n = src[pos+1];
  if (n === 'n') return '\n';
  if (n === 't') return '\t';
  if (n === 'r') return '\r';
  if (n === '\\') return '\\';
  if (n === "'") return "'";
  if (n === '"') return '"';
  return '\\' + n;
}

// --- Conversion ---

function parseControls(s) {
  if (!s || s.trim() === '' || s.trim() === 'None directly') return [];
  return s.split(', ').map(c => c.trim()).filter(c => c.length > 0);
}

function band(pct) {
  if (pct >= 85) return 'full';
  if (pct >= 65) return 'substantial';
  if (pct >= 40) return 'partial';
  if (pct >= 1) return 'weak';
  return 'none';
}

function buildJSON(fw, rawData) {
  const clauses = rawData.map(row => ({
    id: String(row[0]),
    title: String(row[1]),
    controls: parseControls(String(row[2])),
    coverage_pct: Number(row[3]),
    rationale: String(row[4]),
    gaps: String(row[5]),
  }));

  const total = clauses.length;
  const avg = total > 0 ? Math.round((clauses.reduce((s, c) => s + c.coverage_pct, 0) / total) * 10) / 10 : 0;
  const counts = { full: 0, substantial: 0, partial: 0, weak: 0, none: 0 };
  for (const c of clauses) counts[band(c.coverage_pct)]++;

  return {
    $schema: '../schema/framework-coverage.schema.json',
    framework_id: fw.id,
    framework_name: fw.name,
    metadata: {
      source: 'SP800-53v5_Control_Mappings',
      version: '1.0',
      disclaimer: 'Based on publicly available crosswalks and expert analysis. Validate with qualified assessors for compliance/audit use.',
    },
    weight_scale: {
      full:        { min: 85, max: 100, label: 'Fully addressed' },
      substantial: { min: 65, max: 84,  label: 'Well addressed, notable gaps' },
      partial:     { min: 40, max: 64,  label: 'Partially addressed' },
      weak:        { min: 1,  max: 39,  label: 'Weakly addressed' },
      none:        { min: 0,  max: 0,   label: 'No mapping' },
    },
    clauses,
    summary: {
      total_clauses: total,
      average_coverage: avg,
      full_count: counts.full,
      substantial_count: counts.substantial,
      partial_count: counts.partial,
      weak_count: counts.weak,
      none_count: counts.none,
    },
  };
}

// --- Main ---
const cache = new Map();
function getSrc(file) {
  if (!cache.has(file)) cache.set(file, readFileSync(join(STRATEGY_DIR, file), 'utf-8'));
  return cache.get(file);
}

let ok = 0;
for (const fw of FRAMEWORKS) {
  try {
    const raw = extractPythonArray(getSrc(fw.source), fw.variable);
    const json = buildJSON(fw, raw);
    writeFileSync(join(OUTPUT_DIR, fw.output), JSON.stringify(json, null, 2) + '\n');
    console.log(`OK  ${fw.output} -- ${json.summary.total_clauses} clauses, avg ${json.summary.average_coverage}%`);
    ok++;
  } catch (err) {
    console.error(`ERR ${fw.output}: ${err.message}`);
  }
}
console.log(`\nDone: ${ok}/${FRAMEWORKS.length} files written to ${OUTPUT_DIR}`);
