#!/usr/bin/env bash
# OSA Traffic Collection Script
# Run every few days to capture GitHub (14-day rolling window) and Cloudflare stats.
# Usage: ./metrics/collect.sh
#
# Requires:
#   - gh CLI authenticated
#   - OSA_CLOUDFLARE_API_TOKEN and OSA_CLOUDFLARE_ZONE_ID in environment (or ~/.zshrc)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
mkdir -p "$DATA_DIR"

TODAY=$(date +%Y-%m-%d)
GITHUB_CSV="$DATA_DIR/github-daily.csv"
CLOUDFLARE_CSV="$DATA_DIR/cloudflare-daily.csv"
REFERRERS_CSV="$DATA_DIR/referrers.csv"

# Source tokens from zshrc if not already set
if [[ -z "${OSA_CLOUDFLARE_API_TOKEN:-}" ]]; then
  source ~/.zshrc 2>/dev/null || true
fi

# --- GitHub Traffic ---
echo "Collecting GitHub traffic..."

# Initialise CSV headers if needed
if [[ ! -f "$GITHUB_CSV" ]]; then
  echo "date,repo,views,views_unique,clones,clones_unique" > "$GITHUB_CSV"
fi

for REPO in osa-data osa-website; do
  VIEWS=$(gh api "repos/opensecurityarchitecture/$REPO/traffic/views" 2>/dev/null)
  CLONES=$(gh api "repos/opensecurityarchitecture/$REPO/traffic/clones" 2>/dev/null)

  # Extract daily entries and merge views + clones by date
  echo "$VIEWS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for day in data.get('views', []):
    ts = day['timestamp'][:10]
    print(f\"{ts},{day['count']},{day['uniques']}\")
" | while IFS=, read -r date v vu; do
    # Find matching clone data for this date
    c=$(echo "$CLONES" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for day in data.get('clones', []):
    if day['timestamp'][:10] == '$date':
        print(f\"{day['count']},{day['uniques']}\")
        break
else:
    print('0,0')
")
    # Only append if this date+repo combo doesn't already exist
    if ! grep -q "^${date},${REPO}," "$GITHUB_CSV" 2>/dev/null; then
      echo "${date},${REPO},${v},${vu},${c}" >> "$GITHUB_CSV"
    fi
  done
done

# Sort in place (preserve header)
if [[ -f "$GITHUB_CSV" ]]; then
  header=$(head -1 "$GITHUB_CSV")
  tail -n +2 "$GITHUB_CSV" | sort -t, -k1,1 -k2,2 | uniq > "$DATA_DIR/.tmp_gh.csv"
  echo "$header" > "$GITHUB_CSV"
  cat "$DATA_DIR/.tmp_gh.csv" >> "$GITHUB_CSV"
  rm -f "$DATA_DIR/.tmp_gh.csv"
fi

echo "  GitHub daily data written to $GITHUB_CSV"

# --- GitHub Referrers ---
echo "Collecting GitHub referrers..."

if [[ ! -f "$REFERRERS_CSV" ]]; then
  echo "collected_date,repo,referrer,views,uniques" > "$REFERRERS_CSV"
fi

for REPO in osa-data osa-website; do
  gh api "repos/opensecurityarchitecture/$REPO/traffic/popular/referrers" 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for ref in data:
    print(f\"$TODAY,$REPO,{ref['referrer']},{ref['count']},{ref['uniques']}\")
" >> "$REFERRERS_CSV"
done

echo "  Referrers written to $REFERRERS_CSV"

# --- Cloudflare Analytics ---
echo "Collecting Cloudflare analytics..."

if [[ -z "${OSA_CLOUDFLARE_API_TOKEN:-}" || -z "${OSA_CLOUDFLARE_ZONE_ID:-}" ]]; then
  echo "  WARNING: OSA_CLOUDFLARE_API_TOKEN or OSA_CLOUDFLARE_ZONE_ID not set. Skipping."
else
  if [[ ! -f "$CLOUDFLARE_CSV" ]]; then
    echo "date,page_views,requests,unique_visitors" > "$CLOUDFLARE_CSV"
  fi

  # Fetch last 14 days
  START_DATE=$(date -v-14d +%Y-%m-%d 2>/dev/null || date -d '14 days ago' +%Y-%m-%d)

  RESPONSE=$(curl -s https://api.cloudflare.com/client/v4/graphql \
    -H "Authorization: Bearer $OSA_CLOUDFLARE_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data "{
      \"query\": \"{ viewer { zones(filter: {zoneTag: \\\"$OSA_CLOUDFLARE_ZONE_ID\\\"}) { httpRequests1dGroups(limit: 14, filter: {date_geq: \\\"$START_DATE\\\", date_leq: \\\"$TODAY\\\"}, orderBy: [date_ASC]) { dimensions { date } sum { requests pageViews } uniq { uniques } } } } }\"
    }")

  echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for day in data['data']['viewer']['zones'][0]['httpRequests1dGroups']:
    d = day['dimensions']['date']
    pv = day['sum']['pageViews']
    rq = day['sum']['requests']
    uv = day['uniq']['uniques']
    print(f'{d},{pv},{rq},{uv}')
" | while IFS=, read -r date pv rq uv; do
    if ! grep -q "^${date}," "$CLOUDFLARE_CSV" 2>/dev/null; then
      echo "${date},${pv},${rq},${uv}" >> "$CLOUDFLARE_CSV"
    fi
  done

  # Sort in place (preserve header)
  header=$(head -1 "$CLOUDFLARE_CSV")
  tail -n +2 "$CLOUDFLARE_CSV" | sort -t, -k1,1 | uniq > "$DATA_DIR/.tmp_cf.csv"
  echo "$header" > "$CLOUDFLARE_CSV"
  cat "$DATA_DIR/.tmp_cf.csv" >> "$CLOUDFLARE_CSV"
  rm -f "$DATA_DIR/.tmp_cf.csv"

  echo "  Cloudflare daily data written to $CLOUDFLARE_CSV"
fi

# --- Summary ---
echo ""
echo "=== Collection Summary ($TODAY) ==="
if [[ -f "$GITHUB_CSV" ]]; then
  GH_ROWS=$(tail -n +2 "$GITHUB_CSV" | wc -l | tr -d ' ')
  echo "  GitHub: $GH_ROWS daily records"
fi
if [[ -f "$CLOUDFLARE_CSV" ]]; then
  CF_ROWS=$(tail -n +2 "$CLOUDFLARE_CSV" | wc -l | tr -d ' ')
  echo "  Cloudflare: $CF_ROWS daily records"
fi
echo "  Data dir: $DATA_DIR"
echo "Done."
