#!/usr/bin/env python3
"""Markdown to standalone HTML converter for vocational reports."""

import argparse
import re
import sys
from pathlib import Path

try:
    import markdown
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Install dependencies: pip install markdown beautifulsoup4")
    sys.exit(1)


def detect_headings(md_text):
    """Detect Chinese-numbered headings and assign levels."""
    lines = md_text.split('\n')
    headings = []
    
    for line in lines:
        line = line.strip()
        # 一、二、三... 十、 → level 1
        if re.match(r'^\*\*([一二三四五六七八九十])、', line):
            headings.append(('h1', line))
        # （一）（二）... → level 2
        elif re.match(r'^\*\*（[一二三四五六七八九十]）', line):
            headings.append(('h2', line))
        # 1. 2. 3. → level 3
        elif re.match(r'^\d+\.', line):
            headings.append(('h3', line))
    
    return headings


def build_html(md_text, title):
    """Convert markdown to self-contained HTML."""
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    # Generate TOC
    headings = detect_headings(md_text)
    toc_items = []
    for level, heading in headings:
        clean = heading.replace('*', '').strip()
        anchor = re.sub(r'[^\w\u4e00-\u9fff]', '', clean)
        indent = '  ' if level == 'h2' else ''
        toc_items.append(f'{indent}<li><a href="#{anchor}">{clean}</a></li>')
    
    toc_html = '<nav class="toc"><h2>目录</h2><ul>' + '\n'.join(toc_items) + '</ul></nav>' if toc_items else ''
    
    # Add back-to-toc links after each h1
    soup = BeautifulSoup(html_body, 'html.parser')
    for tag in soup.find_all(['h1']):
        back_link = soup.new_tag('a', href='#', **{'class': 'back-to-toc'})
        back_link.string = '↑ 返回目录'
        tag.insert_after(back_link)
    
    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif;
        font-size: 16px; line-height: 1.8; color: #333;
        max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem;
        background: #fff;
    }
    h1 { font-size: 1.8rem; margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #1a5276; color: #1a5276; }
    h2 { font-size: 1.4rem; margin: 1.5rem 0 0.8rem; color: #2471a3; }
    h3 { font-size: 1.2rem; margin: 1.2rem 0 0.6rem; color: #2e86c1; }
    p { margin: 0.8rem 0; text-indent: 2em; }
    table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9rem; }
    th { background: #1a5276; color: #fff; padding: 0.6rem 0.8rem; text-align: left; }
    td { border: 1px solid #ddd; padding: 0.5rem 0.8rem; }
    tr:nth-child(even) { background: #f8f9fa; }
    code { background: #f4f4f4; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
    pre { background: #f4f4f4; padding: 1rem; border-radius: 5px; overflow-x: auto; margin: 1rem 0; }
    pre code { background: none; padding: 0; }
    blockquote { border-left: 4px solid #1a5276; padding: 0.5rem 1rem; margin: 1rem 0; background: #f0f7ff; }
    .toc { background: #f8f9fa; padding: 1.2rem 1.5rem; margin: 1.5rem 0; border-radius: 5px; border: 1px solid #dee2e6; }
    .toc h2 { margin-top: 0; font-size: 1.2rem; }
    .toc ul { list-style: none; padding-left: 0; }
    .toc li { margin: 0.3rem 0; }
    .toc a { color: #2471a3; text-decoration: none; }
    .toc a:hover { text-decoration: underline; }
    .back-to-toc { display: inline-block; margin-left: 1rem; font-size: 0.85rem; color: #888; text-decoration: none; }
    .back-to-toc:hover { color: #1a5276; }
    hr { border: none; border-top: 1px solid #dee2e6; margin: 2rem 0; }
    """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<h1>{title}</h1>
{toc_html}
{soup.prettify()}
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description='Convert MD report to standalone HTML')
    parser.add_argument('--input', required=True, help='Input .md file path')
    parser.add_argument('--output', required=True, help='Output .html file path')
    parser.add_argument('--title', required=True, help='Report title')
    args = parser.parse_args()
    
    md_text = Path(args.input).read_text(encoding='utf-8')
    html = build_html(md_text, args.title)
    Path(args.output).write_text(html, encoding='utf-8')
    print(f'Converted: {args.input} -> {args.output}')


if __name__ == '__main__':
    main()
