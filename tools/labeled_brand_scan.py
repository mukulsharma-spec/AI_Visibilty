#!/usr/bin/env python3
"""
labeled_brand_scan.py - Text scan for labeled brands

Searches answer text for brand names that were labeled in brand_mentions.csv,
using normalized pattern matching. This fills mention_count, first_char_pos,
and order_of_first_appearance for brands that were added as fact_row=0 (judged
brands not in the alias list).

Design:
1. For each answer, look at all labeled brands (existing brand_mentions rows)
2. Search answer text with normalization:
   - Case-insensitive
   - & vs "and"
   - Dots/periods optional with optional space (H.Samuel = H Samuel)
   - Optional leading "The"
   - Optional trailing "'s"
   - Apostrophe variants (straight, curly)
   - Accent normalization (À = A)
3. Fill mention_count, first_char_pos; recompute order_of_first_appearance
4. Alias patterns (brand_aliases_v3.csv) override when present

Usage:
  python3 tools/labeled_brand_scan.py --backfill   # Backfill live_csv
  python3 tools/labeled_brand_scan.py --dry-run    # Show what would change
  python3 tools/labeled_brand_scan.py --run-id X   # Process single run
"""

import csv
import re
import os
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Apostrophe variants: straight, right single quote, left single quote, modifier letter
APOS_CHARS = "'\u2019\u2018\u02BC"
APOS_CLASS = f"[{APOS_CHARS}]?"
APOS_MATCH_CLASS = f"[{APOS_CHARS}]"

def normalize_accents(text):
    """Normalize accented characters to ASCII equivalents."""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def build_brand_pattern(brand_name):
    """
    Build regex pattern for a brand name with normalizations.
    
    Handles:
    - Case insensitive (applied at search time)
    - & vs "and"
    - Dots optional with optional space (H.Samuel)
    - Optional leading "The"
    - Optional trailing "'s"
    - Apostrophe variants
    """
    b = brand_name
    words = b.split()
    patterns = []
    
    for word in words:
        w = word
        if w == '&':
            patterns.append(r'(?:&|and)')
            continue
        
        # Replace apostrophes with character class
        w_out = []
        for c in w:
            if c in APOS_CHARS:
                w_out.append(APOS_CLASS)
            else:
                w_out.append(c)
        w = ''.join(w_out)
        
        # Handle dots
        if '.' in w:
            parts = w.split('.')
            escaped_parts = []
            for p in parts:
                if APOS_CLASS in p:
                    segs = p.split(APOS_CLASS)
                    escaped_parts.append(APOS_CLASS.join(re.escape(s) for s in segs))
                else:
                    escaped_parts.append(re.escape(p))
            w = r'\.?\s*'.join(escaped_parts)
        else:
            if APOS_CLASS in w:
                segs = w.split(APOS_CLASS)
                w = APOS_CLASS.join(re.escape(s) for s in segs)
            else:
                w = re.escape(w)
        
        patterns.append(w)
    
    # Join with flexible space/dot
    pattern = r'[. ]+'.join(patterns)
    
    # Optional leading "The "
    if not brand_name.lower().startswith('the'):
        pattern = r'(?:the\s+)?' + pattern
    
    # Optional trailing "'s"
    pattern = pattern + f"(?:{APOS_MATCH_CLASS}?s)?"
    
    return pattern

def load_alias_patterns(aliases_path):
    """Load brand alias patterns from CSV."""
    patterns = {}
    if aliases_path.exists():
        with open(aliases_path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                brand = row['brand']
                pattern = row['pattern']
                try:
                    patterns[brand] = re.compile(pattern, re.I)
                except re.error as e:
                    print(f"Warning: Invalid alias pattern for {brand}: {e}")
    return patterns

def search_brand_in_text(brand, text, alias_patterns):
    """
    Search for brand in text. Returns (mention_count, first_char_pos) or (None, None).
    
    Uses alias pattern if available, otherwise builds normalized pattern from brand name.
    Also searches with accent-normalized text as fallback.
    """
    if not text:
        return None, None
    
    # Try alias pattern first
    if brand in alias_patterns:
        matches = list(alias_patterns[brand].finditer(text))
        if matches:
            return len(matches), matches[0].start()
    
    # Build normalized pattern from brand name
    pattern_str = build_brand_pattern(brand)
    try:
        pattern = re.compile(pattern_str, re.I)
    except re.error:
        return None, None
    
    # Search original text
    matches = list(pattern.finditer(text))
    if matches:
        return len(matches), matches[0].start()
    
    # Try with accent-normalized text (always, not just when brand has accents)
    # This handles cases like "A Vie" matching "À Vie" in text
    norm_text = normalize_accents(text)
    if norm_text != text:
        matches = list(pattern.finditer(norm_text))
        if matches:
            return len(matches), matches[0].start()
    
    return None, None

def run_backfill(repo_root, dry_run=False, run_id_filter=None):
    """
    Backfill text scan columns for labeled brands in live_csv.
    
    Returns dict with stats and miss report.
    """
    live_csv = repo_root / 'live_csv'
    inputs = repo_root / 'inputs'
    
    # Load alias patterns
    alias_patterns = load_alias_patterns(inputs / 'brand_aliases_v3.csv')
    
    # Load answer texts
    answer_texts = {}
    with open(live_csv / 'answer_text.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['run_id'], row['run_key'])
            text = row.get('answer_text', '')
            followup = row.get('followup_answer_text', '')
            answer_texts[key] = {'t1': text, 't2': followup}
    
    # Load brand mentions
    with open(live_csv / 'brand_mentions.csv', encoding='utf-8') as f:
        bm_rows = list(csv.DictReader(f))
    
    # Get field names (preserve order)
    with open(live_csv / 'brand_mentions.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
    
    # Group by answer key
    by_answer = defaultdict(list)
    for i, row in enumerate(bm_rows):
        key = (row['run_id'], row['run_key'])
        by_answer[key].append((i, row))
    
    # Stats
    stats = {
        'total_rows': len(bm_rows),
        'blank_before': 0,
        'filled': 0,
        'still_blank': 0,
        'recomputed_order': 0,
        'missing_answer_text': 0
    }
    miss_report = []
    
    # Process each answer
    for key, rows in by_answer.items():
        run_id, run_key = key
        
        # Filter by run_id if specified
        if run_id_filter and run_id != run_id_filter:
            continue
        
        # Get answer text for appropriate turn
        turn = run_key.split('|')[-1]  # e.g., 't1' or 't2'
        texts = answer_texts.get(key, {})
        text = texts.get(turn, '') or texts.get('t1', '')
        
        if not text:
            stats['missing_answer_text'] += 1
            continue
        
        # Collect brands with positions
        brand_positions = []
        
        for idx, row in rows:
            mc = row.get('mention_count', '')
            
            # Check if needs filling
            if mc == '' or mc is None:
                stats['blank_before'] += 1
                
                # Search for brand
                count, pos = search_brand_in_text(row['brand'], text, alias_patterns)
                
                if count is not None:
                    bm_rows[idx]['mention_count'] = str(count)
                    bm_rows[idx]['first_char_pos'] = str(pos)
                    bm_rows[idx]['text_source'] = 'answer'
                    stats['filled'] += 1
                    brand_positions.append((pos, row['brand'], idx))
                else:
                    stats['still_blank'] += 1
                    miss_report.append({
                        'run_id': run_id,
                        'run_key': run_key,
                        'brand': row['brand'],
                        'role': row.get('role', '')
                    })
            else:
                # Already has count, record position for order calculation
                pos = row.get('first_char_pos', '')
                if pos and pos != '':
                    try:
                        brand_positions.append((float(pos), row['brand'], idx))
                    except ValueError:
                        pass
        
        # Recompute order_of_first_appearance for all brands with positions
        if brand_positions:
            brand_positions.sort(key=lambda x: x[0])
            for order, (pos, brand, idx) in enumerate(brand_positions, 1):
                old_order = bm_rows[idx].get('order_of_first_appearance', '')
                new_order = str(order)
                if old_order != new_order:
                    bm_rows[idx]['order_of_first_appearance'] = new_order
                    stats['recomputed_order'] += 1
    
    # Write output (or report in dry run)
    if dry_run:
        print("DRY RUN - no changes written")
        print(f"Would update {stats['filled']} rows, {stats['still_blank']} still blank")
    else:
        # Backup existing file
        backup_dir = repo_root / 'archive' / f'live_csv_backup_{datetime.now().strftime("%Y-%m-%d")}_textscan_backfill'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        import shutil
        for csv_file in ['answers.csv', 'brand_mentions.csv', 'citations.csv', 'answer_text.csv']:
            src = live_csv / csv_file
            if src.exists():
                shutil.copy(src, backup_dir / csv_file)
        
        # Write updated brand_mentions.csv
        with open(live_csv / 'brand_mentions.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(bm_rows)
        
        # Write miss report
        miss_path = backup_dir / 'labeled_not_found_in_text.csv'
        if miss_report:
            with open(miss_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['run_id', 'run_key', 'brand', 'role'])
                writer.writeheader()
                writer.writerows(miss_report)
    
    return stats, miss_report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Text scan for labeled brands')
    parser.add_argument('--backfill', action='store_true', help='Backfill live_csv')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change')
    parser.add_argument('--run-id', help='Process only this run_id')
    args = parser.parse_args()
    
    if not args.backfill and not args.dry_run:
        parser.print_help()
        sys.exit(1)
    
    stats, miss_report = run_backfill(
        REPO_ROOT, 
        dry_run=args.dry_run,
        run_id_filter=args.run_id
    )
    
    print(f"\nBackfill results:")
    print(f"  Total rows: {stats['total_rows']}")
    print(f"  Blank before: {stats['blank_before']}")
    print(f"  Filled: {stats['filled']}")
    print(f"  Still blank: {stats['still_blank']}")
    print(f"  Recomputed order: {stats['recomputed_order']}")
    print(f"  Missing answer text: {stats['missing_answer_text']}")
    
    if miss_report:
        print(f"\nTop brands still not found:")
        from collections import Counter
        for brand, cnt in Counter(m['brand'] for m in miss_report).most_common(15):
            print(f"  {brand}: {cnt}")
    
    return 0 if not miss_report else 1

if __name__ == '__main__':
    sys.exit(main())
