"""Offline template-based digital product generator; never publishes listings."""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

def generate(topic, audience, days=7):
    topic, audience = topic.strip(), audience.strip()
    if not 1 <= len(topic) <= 120 or not 1 <= len(audience) <= 120 or not 1 <= days <= 90:
        raise ValueError('Topic/audience must have 1-120 characters; days must be 1-90')
    if any(ord(c) < 32 for c in topic+audience):
        raise ValueError('Control characters are not allowed')
    slug = re.sub('[^a-z0-9]+', '-', topic.lower()).strip('-') or 'product'
    title = f'{topic} action planner'
    guide = [f'# {title}', '', f'For: {audience}', '',
        'An editable planning template. Choose realistic actions and adapt every prompt to your situation.', '']
    table = io.StringIO(newline='')
    writer = csv.writer(table)
    writer.writerow(['day', 'focus', 'action', 'minutes', 'completed', 'reflection'])
    for day in range(1, days+1):
        focus = ['Define one small goal', 'Remove one obstacle', 'Practice a small step', 'Review and adjust'][(day-1)%4]
        guide += [f'## Day {day}: {focus}', f'What is one useful step for {topic}? __________________',
                  'Time available: ____ minutes', 'What worked? __________________', 'Next adjustment: __________________', '']
        writer.writerow([day, focus, '', '', '', ''])
    listing = {'status': 'DRAFT - HUMAN REVIEW REQUIRED', 'title': title,
        'audience': audience, 'description': f'An editable {days}-day {topic} planner for {audience}. Includes Markdown workbook and CSV tracker. No guaranteed outcomes.',
        'included_files': ['workbook.md', 'tracker.csv', 'buyer-readme.txt'],
        'price': None, 'currency': None,
        'review_checklist': ['Edit and proofread all content', 'Validate audience demand',
            'Check intellectual property and marketplace rules', 'Set price, currency and refund terms',
            'Preview CSV in spreadsheet software', 'Publish manually only after review']}
    return slug, {'workbook.md': '\n'.join(guide), 'tracker.csv': table.getvalue(),
        'listing-draft.json': json.dumps(listing, ensure_ascii=False, indent=2),
        'listing-draft.md': f"# DRAFT: {title}\n\n{listing['description']}\n\nPrice: decide after review. Not published.\n", 
        'buyer-readme.txt': 'Open workbook.md in a text editor and tracker.csv in a spreadsheet. Make a working copy before editing. This is a general planning template. No promised results.\n'}

def save(topic, audience, days, output):
    slug, files = generate(topic, audience, days)
    destination = Path(output)/slug
    destination.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        (destination/name).write_text(content, encoding='utf-8')
    # Customer pack excludes internal draft listings.
    with zipfile.ZipFile(destination/'customer-product.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ['workbook.md', 'tracker.csv', 'buyer-readme.txt']:
            z.write(destination/name, name)
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir() if p.is_file()}
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return destination

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic', default='Weekly focus')
    parser.add_argument('--audience', default='Busy beginners')
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--output', type=Path, default=Path('output'))
    args = parser.parse_args()
    try:
        print('Draft product saved to', save(args.topic, args.audience, args.days, args.output).resolve())
    except (ValueError, OSError) as exc:
        parser.exit(2, f'Generation error: {exc}\n')

if __name__ == '__main__':
    main()
