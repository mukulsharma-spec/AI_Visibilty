#!/usr/bin/env python3
"""
build_run_csv.py - Build CSV files from raw captures

Processes runs/<run_id>/raw/ folders and generates:
  - answers.csv (35 columns)
  - brand_mentions.csv (20 columns)
  - citations.csv (12 columns)
  - answer_text.csv (4 columns)
  - build_info.json

Usage:
  python3 tools/build_run_csv.py --run-id 2026-11-05_delta_w02_uk70
"""

import csv
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup
import gzip
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).parent.parent

APOS_CHARS = "'\u2019\u2018\u02BC"
APOS_CLASS = f"[{APOS_CHARS}]?"
APOS_MATCH_CLASS = f"[{APOS_CHARS}]"

ANSWERS_COLUMNS = [
    'run_id', 'run_key', 'app', 'prompt_id', 'repeat', 'turn',
    'prompt', 'captured_at_utc', 'signed_in', 'session', 'egress_country', 'source',
    'text_source', 'has_raw_folder', 'answer_chars', 'web_search_marker',
    'angara_in_text', 'angara_mention_count', 'angara_first_char_pos',
    'n_brands_found', 'n_links', 'angara_link_present',
    'ai_answer_format', 'ai_n_recommended', 'ai_n_rank_slots',
    'ai_angara_role', 'ai_angara_published_rank', 'ai_angara_rank', 'ai_angara_rank_n',
    'ai_top1_brand', 'market', 'model_ui', 'capture_quality', 'chat_url', 'search_queries'
]

BRAND_MENTIONS_COLUMNS = [
    'run_id', 'run_key', 'app', 'prompt_id', 'repeat', 'turn',
    'brand', 'fact_row', 'mention_count', 'first_char_pos', 'order_of_first_appearance',
    'text_source', 'published_rank', 'tie', 'role', 'in_product_card',
    'price_shown_usd', 'claim', 'sentiment', 'confidence'
]

CITATIONS_COLUMNS = [
    'run_id', 'run_key', 'app', 'prompt_id', 'repeat', 'turn',
    'link_order', 'url', 'domain', 'is_angara', 'source_file', 'link_location'
]

ANSWER_TEXT_COLUMNS = ['run_id', 'run_key', 'answer_text', 'followup_answer_text']

DROP_DOMAINS = {
    'chatgpt.com', 'chat.openai.com', 'openai.com',
    'claude.ai', 'anthropic.com',
    'gemini.google.com', 'accounts.google.com', 'support.google.com', 'policies.google.com'
}


def normalize_accents(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


def get_registrable_domain(url):
    """Extract registrable domain from URL, stripping www."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        parts = domain.split('.')
        if len(parts) > 2:
            if parts[-2] in ('co', 'com', 'org', 'net', 'gov', 'edu'):
                return '.'.join(parts[-3:])
            return '.'.join(parts[-2:])
        return domain
    except:
        return ''


def is_drop_link(url):
    """Check if URL should be dropped (app links, mailto, etc.)."""
    if not url:
        return True
    url_lower = url.lower()
    if url_lower.startswith(('mailto:', 'javascript:', '#')):
        return True
    domain = get_registrable_domain(url)
    return domain in DROP_DOMAINS


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
    """Search for brand in text. Returns (count, first_pos) or (None, None)."""
    if not text:
        return None, None
    
    if brand in alias_patterns:
        matches = list(alias_patterns[brand].finditer(text))
        if matches:
            return len(matches), matches[0].start()
    return None, None


def search_angara(text):
    """Search for Angara in text, case-insensitive."""
    if not text:
        return 0, 0, ''
    matches = list(re.finditer(r'angara', text, re.I))
    if matches:
        return 1, len(matches), matches[0].start()
    return 0, 0, ''


def extract_links_from_html(html_content, source_file='html'):
    """Extract outbound links from HTML content."""
    links = []
    seen_urls = set()
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a', href=True):
            url = a['href']
            if url in seen_urls:
                continue
            if is_drop_link(url):
                continue
            if not url.startswith(('http://', 'https://')):
                continue
            seen_urls.add(url)
            domain = get_registrable_domain(url)
            links.append({
                'url': url,
                'domain': domain,
                'is_angara': 1 if domain == 'angara.com' else 0,
                'source_file': source_file,
                'link_location': 'inline'
            })
    except Exception as e:
        print(f"Warning: Error parsing HTML: {e}")
    
    return links


def read_folder_citations(folder_path):
    """Read per-folder citations.csv if it exists."""
    citations_path = folder_path / 'citations.csv'
    if not citations_path.exists():
        return []
    
    citations = []
    try:
        with open(citations_path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                url = row.get('url', '')
                domain = row.get('domain', '') or get_registrable_domain(url)
                source_file = row.get('source_file', 'html_card')
                citations.append({
                    'url': url,
                    'domain': domain,
                    'is_angara': 1 if domain == 'angara.com' else 0,
                    'source_file': source_file,
                    'link_location': 'inline' if source_file != 'sources_panel' else 'sources_panel'
                })
    except Exception as e:
        print(f"Warning: Error reading {citations_path}: {e}")
    
    return citations


def get_answer_text(folder_path):
    """Get answer text from answer.txt or answer.html."""
    answer_txt = folder_path / 'answer.txt'
    if answer_txt.exists():
        text = answer_txt.read_text(encoding='utf-8').strip()
        if text:
            return text, 'answer'
    
    answer_html = folder_path / 'answer.html'
    if answer_html.exists():
        try:
            html = answer_html.read_text(encoding='utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n').strip(), 'page_copy'
        except:
            pass
    
    answer_gz = folder_path / 'answer.html.gz'
    if answer_gz.exists():
        try:
            with gzip.open(answer_gz, 'rt', encoding='utf-8') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator='\n').strip(), 'page_copy'
        except:
            pass
    
    return '', 'answer'


def parse_run_key(folder_name):
    """Parse folder name like 'claude__BS01__r1__t1' into components."""
    parts = folder_name.split('__')
    if len(parts) != 4:
        return None
    app, prompt_id, repeat, turn_str = parts
    turn = int(turn_str[1]) if turn_str.startswith('t') else 1
    run_key = f"{app}|{prompt_id}|{repeat}|{turn_str}"
    return {
        'app': app,
        'prompt_id': prompt_id,
        'repeat': repeat,
        'turn': turn,
        'run_key': run_key
    }


def detect_answer_format(text):
    """Detect the format of the answer based on patterns."""
    if not text:
        return 'paragraphs'
    
    lines = text.strip().split('\n')
    
    numbered_pattern = re.compile(r'^\s*\d+[\.\)]\s')
    bullet_pattern = re.compile(r'^\s*[-•*]\s')
    heading_pattern = re.compile(r'^#+\s|^[A-Z][^.!?]*:$')
    
    numbered = sum(1 for l in lines if numbered_pattern.match(l))
    bullets = sum(1 for l in lines if bullet_pattern.match(l))
    headings = sum(1 for l in lines if heading_pattern.match(l.strip()))
    
    total_lines = len([l for l in lines if l.strip()])
    
    if numbered > 3:
        if headings > 1:
            return 'numbered_headings'
        return 'numbered_list'
    if bullets > 3:
        if headings > 1:
            return 'bullets_by_category'
        return 'bullets'
    if headings > 2:
        return 'headings'
    if '|' in text and text.count('|') > 5:
        return 'table'
    if numbered >= 1 or bullets >= 1:
        return 'paragraphs_bullets'
    return 'paragraphs'


def detect_web_search(meta, answer_text, app):
    """Detect if web search was used."""
    if meta.get('web_search'):
        return 1
    if meta.get('searched_web'):
        return 1
    if 'utm_source=chatgpt.com' in answer_text:
        return 1
    if app == 'claude' and 'Searched the web' in answer_text:
        return 1
    return 0


def load_prompts(repo_root, run_id):
    """Load prompts from run_lists for this run."""
    prompts = {}
    
    run_lists_dir = repo_root / 'inputs' / 'run_lists'
    for csv_file in run_lists_dir.glob('*.csv'):
        try:
            with open(csv_file, encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    pid = row.get('prompt_id', '')
                    if pid:
                        prompts[pid] = {
                            'prompt_text': row.get('prompt_text', ''),
                            'followup_text': row.get('followup_text', ''),
                            'category': row.get('category', '')
                        }
        except:
            pass
    
    main_prompts = repo_root / 'inputs' / 'prompts_v3_final.csv'
    if main_prompts.exists():
        with open(main_prompts, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                pid = row.get('prompt_id', '')
                if pid and pid not in prompts:
                    prompts[pid] = {
                        'prompt_text': row.get('prompt_text', ''),
                        'followup_text': row.get('followup_text', ''),
                        'category': row.get('category', '')
                    }
    
    return prompts


def build_run_csv(run_id, repo_root=REPO_ROOT):
    """Build all CSV files for a run."""
    run_dir = repo_root / 'runs' / run_id
    raw_dir = run_dir / 'raw'
    csv_dir = run_dir / 'csv'
    
    if not raw_dir.exists():
        print(f"Error: Raw directory not found: {raw_dir}")
        return False
    
    csv_dir.mkdir(exist_ok=True)
    
    alias_patterns = load_alias_patterns(repo_root / 'inputs' / 'brand_aliases_v3.csv')
    prompts = load_prompts(repo_root, run_id)
    
    answers_rows = []
    brand_mentions_rows = []
    citations_rows = []
    answer_text_rows = []
    
    warnings = []
    new_brand_names = set()
    folders_skipped = 0
    
    for app_dir in sorted(raw_dir.iterdir()):
        if not app_dir.is_dir():
            continue
        app = app_dir.name
        
        for folder in sorted(app_dir.iterdir()):
            if not folder.is_dir():
                continue
            if '__discarded' in folder.name:
                folders_skipped += 1
                continue
            
            parsed = parse_run_key(folder.name)
            if not parsed:
                warnings.append(f"Could not parse folder name: {folder.name}")
                continue
            
            meta_path = folder / 'meta.json'
            meta = {}
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding='utf-8'))
                except:
                    warnings.append(f"{folder.name}: Could not parse meta.json")
            
            answer_text, text_source = get_answer_text(folder)
            if not answer_text:
                warnings.append(f"{folder.name}: answer.txt empty, used page_copy")
            
            prompt_info = prompts.get(parsed['prompt_id'], {})
            prompt_text = meta.get('prompt_sent') or meta.get('prompt_text') or prompt_info.get('prompt_text', '')
            
            captured_at = meta.get('captured_at_utc', '')
            if not captured_at:
                captured_at = meta.get('captured_at', '')
            
            signed_in = meta.get('signed_in', False)
            signed_in_str = 'true' if signed_in else 'false'
            
            session = meta.get('session', '')
            egress_country = meta.get('egress_country', '')
            source = meta.get('source', 'grok_bot_ui')
            
            angara_in_text, angara_count, angara_pos = search_angara(answer_text)
            angara_first_pos = angara_pos if angara_in_text else ''
            
            web_search = detect_web_search(meta, answer_text, app)
            
            folder_citations = read_folder_citations(folder)
            if not folder_citations:
                html_path = folder / 'answer.html'
                if html_path.exists():
                    html_content = html_path.read_text(encoding='utf-8')
                    folder_citations = extract_links_from_html(html_content)
            
            sources_panel = folder / 'sources_panel.html'
            if sources_panel.exists():
                try:
                    panel_html = sources_panel.read_text(encoding='utf-8')
                    panel_links = extract_links_from_html(panel_html, 'html')
                    seen_urls = {c['url'] for c in folder_citations}
                    for link in panel_links:
                        if link['url'] not in seen_urls:
                            link['link_location'] = 'sources_panel'
                            folder_citations.append(link)
                except:
                    pass
            
            n_links = len(folder_citations)
            angara_link_present = 1 if any(c['is_angara'] for c in folder_citations) else 0
            
            for i, cite in enumerate(folder_citations, 1):
                citations_rows.append({
                    'run_id': run_id,
                    'run_key': parsed['run_key'],
                    'app': app,
                    'prompt_id': parsed['prompt_id'],
                    'repeat': parsed['repeat'],
                    'turn': parsed['turn'],
                    'link_order': i,
                    'url': cite['url'],
                    'domain': cite['domain'],
                    'is_angara': cite['is_angara'],
                    'source_file': cite['source_file'],
                    'link_location': cite['link_location']
                })
            
            brand_matches = []
            for brand, pattern in alias_patterns.items():
                count, pos = search_brand_in_text(brand, answer_text, alias_patterns)
                if count:
                    brand_matches.append({
                        'brand': brand,
                        'count': count,
                        'pos': pos
                    })
            
            brand_matches.sort(key=lambda x: x['pos'])
            for order, bm in enumerate(brand_matches, 1):
                brand_mentions_rows.append({
                    'run_id': run_id,
                    'run_key': parsed['run_key'],
                    'app': app,
                    'prompt_id': parsed['prompt_id'],
                    'repeat': parsed['repeat'],
                    'turn': parsed['turn'],
                    'brand': bm['brand'],
                    'fact_row': 1,
                    'mention_count': bm['count'],
                    'first_char_pos': bm['pos'],
                    'order_of_first_appearance': order,
                    'text_source': text_source,
                    'published_rank': '',
                    'tie': 0,
                    'role': 'mentioned',
                    'in_product_card': 0,
                    'price_shown_usd': '',
                    'claim': 'Named in answer',
                    'sentiment': 'neutral',
                    'confidence': 'high'
                })
            
            n_brands_found = len(brand_matches)
            
            ai_format = detect_answer_format(answer_text)
            
            angara_role = 'absent'
            angara_bm = next((bm for bm in brand_matches if bm['brand'] == 'Angara'), None)
            if angara_bm:
                angara_role = 'mentioned'
            
            market = meta.get('market', '')
            if not market:
                if 'the UK' in prompt_text or '£' in prompt_text:
                    market = 'UK'
                elif 'USA' in prompt_text or '$' in prompt_text:
                    market = 'US'
                else:
                    market = 'UK'
            
            model_ui = meta.get('model_ui', '')
            capture_quality = meta.get('capture_quality', '')
            chat_url = meta.get('chat_url', '')
            search_queries = meta.get('search_queries', '')
            if isinstance(search_queries, list):
                search_queries = ' ; '.join(search_queries)
            if meta.get('searched_web'):
                search_queries = meta.get('searched_web', '')
            
            answers_rows.append({
                'run_id': run_id,
                'run_key': parsed['run_key'],
                'app': app,
                'prompt_id': parsed['prompt_id'],
                'repeat': parsed['repeat'],
                'turn': parsed['turn'],
                'prompt': prompt_text,
                'captured_at_utc': captured_at,
                'signed_in': signed_in_str,
                'session': session,
                'egress_country': egress_country,
                'source': source,
                'text_source': text_source,
                'has_raw_folder': 1,
                'answer_chars': len(answer_text),
                'web_search_marker': web_search,
                'angara_in_text': angara_in_text,
                'angara_mention_count': angara_count,
                'angara_first_char_pos': angara_first_pos,
                'n_brands_found': n_brands_found,
                'n_links': n_links,
                'angara_link_present': angara_link_present,
                'ai_answer_format': ai_format,
                'ai_n_recommended': 0,
                'ai_n_rank_slots': '',
                'ai_angara_role': angara_role,
                'ai_angara_published_rank': '',
                'ai_angara_rank': '',
                'ai_angara_rank_n': '',
                'ai_top1_brand': '',
                'market': market,
                'model_ui': model_ui,
                'capture_quality': capture_quality,
                'chat_url': chat_url,
                'search_queries': search_queries
            })
            
            answer_text_rows.append({
                'run_id': run_id,
                'run_key': parsed['run_key'],
                'answer_text': answer_text,
                'followup_answer_text': ''
            })
    
    with open(csv_dir / 'answers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ANSWERS_COLUMNS)
        writer.writeheader()
        writer.writerows(answers_rows)
    
    with open(csv_dir / 'brand_mentions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=BRAND_MENTIONS_COLUMNS)
        writer.writeheader()
        writer.writerows(brand_mentions_rows)
    
    with open(csv_dir / 'citations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CITATIONS_COLUMNS)
        writer.writeheader()
        writer.writerows(citations_rows)
    
    with open(csv_dir / 'answer_text.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=ANSWER_TEXT_COLUMNS)
        writer.writeheader()
        writer.writerows(answer_text_rows)
    
    apps_processed = sorted(set(r['app'] for r in answers_rows))
    
    build_info = {
        'run_id': run_id,
        'builder': 'Grok Bot',
        'script_version': 'build_run_csv.py v1',
        'built_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'apps': apps_processed,
        'raw_folders_read': len(answers_rows),
        'folders_skipped_discarded': folders_skipped,
        'rows': {
            'answers': len(answers_rows),
            'brand_mentions': len(brand_mentions_rows),
            'citations': len(citations_rows),
            'answer_text': len(answer_text_rows)
        },
        'new_brand_names': sorted(new_brand_names),
        'warnings': warnings[:50]
    }
    
    with open(csv_dir / 'build_info.json', 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2)
    
    print(f"\nBuild complete for {run_id}")
    print(f"  Apps: {', '.join(apps_processed)}")
    print(f"  Rows: answers={len(answers_rows)}, brand_mentions={len(brand_mentions_rows)}, citations={len(citations_rows)}, answer_text={len(answer_text_rows)}")
    print(f"  Warnings: {len(warnings)}")
    
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Build CSV files from raw captures')
    parser.add_argument('--run-id', required=True, help='Run ID to process')
    args = parser.parse_args()
    
    success = build_run_csv(args.run_id)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
