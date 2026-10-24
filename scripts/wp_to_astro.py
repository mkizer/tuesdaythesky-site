#!/usr/bin/env python3
"""
wp_to_astro.py
Convert WordPress WXR export XML to Astro / AstroWind MDX posts.

Features:
- Parses WordPress WXR XML export (posts, attachments, postmeta, categories, tags).
- Converts HTML content to clean Markdown/MDX using markdownify and BeautifulSoup.
- Automatically detects YouTube embeds (iframes and standalone URLs) and converts to <YouTubeEmbed id="..." />.
- Matches featured images (_thumbnail_id) to attachment URLs and downloads missing images locally.
- Formats frontmatter matching AstroWind's content collection schema.
- Reusable across any Astro / AstroWind site.
"""

import argparse
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter, markdownify as md


XML_NAMESPACES = {
    'wp': 'http://wordpress.org/export/1.2/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
}


def clean_text(text: str) -> str:
    """Unescape HTML entities, normalize quotes and whitespace."""
    if not text:
        return ""
    text = html.unescape(text.strip())
    # Normalize common Unicode smart punctuation if desired or keep clean UTF-8
    return text


def extract_youtube_id(url_or_src: str) -> str | None:
    """Extract YouTube 11-char ID from embed URL or watch link."""
    patterns = [
        r'(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})',
        r'^[A-Za-z0-9_-]{11}$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_src)
        if match:
            return match.group(1)
    return None


def sanitize_yaml_string(val: str) -> str:
    """Safely format string for YAML frontmatter."""
    val = val.strip().replace('\r\n', ' ').replace('\n', ' ')
    # If string contains single quotes or colons, use double quotes and escape internal quotes
    val_escaped = val.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{val_escaped}"'


def wpautop(html_content: str) -> str:
    """
    Port of WordPress wpautop().
    Replaces double line breaks with paragraph tags and single line breaks with <br />
    so that markdownify properly maintains blank lines between paragraphs.
    """
    if not html_content or not html_content.strip():
        return ""

    # Normalize line endings
    text = html_content.replace('\r\n', '\n').replace('\r', '\n')

    # Split by two or more newlines to identify paragraphs
    chunks = re.split(r'\n\s*\n', text)
    processed_chunks = []

    block_tags = (
        '<p', '<div', '<h1', '<h2', '<h3', '<h4', '<h5', '<h6',
        '<ul', '<ol', '<li', '<blockquote', '<table', '<iframe', '<section', '<article'
    )

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        stripped_lower = chunk.lower()
        if not stripped_lower.startswith(block_tags):
            # Convert single newlines inside paragraph to <br />\n to preserve soft line breaks
            chunk = re.sub(r'(?<!<br>)(?<!<br />)\n', '<br />\n', chunk)
            chunk = f'<p>{chunk}</p>'

        processed_chunks.append(chunk)

    return '\n\n'.join(processed_chunks)


class AstroMdxConverter(MarkdownConverter):
    """
    Custom Markdownify converter for Astro MDX.
    Ensures external links are converted to <a href="..." target="_blank" rel="noopener noreferrer">
    while keeping internal links as clean Markdown [text](url).
    """
    def __init__(self, base_domain: str = "tuesdaythesky.com", **kwargs):
        super().__init__(**kwargs)
        self.base_domain = base_domain.lower()

    def convert_a(self, el, text, convert_as_inline=False, **kwargs):
        href = el.get('href', '').strip()
        if not href:
            return text
        target = el.get('target')
        parsed = urlparse(href)
        is_external = False
        if parsed.scheme in ('http', 'https'):
            netloc = parsed.netloc.lower()
            if netloc and not (netloc == self.base_domain or netloc.endswith('.' + self.base_domain)):
                is_external = True

        if target == '_blank' or is_external:
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'
        return f'[{text}]({href})'


def process_content_to_mdx(html_content: str, base_domain: str = "tuesdaythesky.com") -> tuple[str, bool]:
    """
    Parse HTML content, convert YouTube embeds to <YouTubeEmbed />,
    clean up WordPress artifacts and shortcodes, ensure external links open in a new tab,
    and convert to Markdown while preserving clean paragraph breaks.
    Returns (mdx_body, has_youtube_embed).
    """
    if not html_content or not html_content.strip():
        return "", False

    # 1. Clean WordPress shortcodes like [caption]...[/caption]
    html_content = re.sub(r'\[caption[^\]]*\](.*?)\[/caption\]', r'\1', html_content, flags=re.DOTALL)
    html_content = re.sub(r'\[/?caption[^\]]*\]', '', html_content)

    # 2. Normalize non-breaking spaces that can corrupt numbered lists
    html_content = html_content.replace('\xa0', ' ').replace('&nbsp;', ' ')

    # 3. Apply wpautop to ensure double newlines become real paragraph tags
    html_with_paragraphs = wpautop(html_content)

    soup = BeautifulSoup(html_with_paragraphs, 'html.parser')
    has_youtube = False

    # 4. Convert YouTube iframes to custom token placeholder
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '')
        yt_id = extract_youtube_id(src)
        if yt_id:
            has_youtube = True
            placeholder = soup.new_tag('p')
            placeholder.string = f'[[YOUTUBE:{yt_id}]]'
            iframe.replace_with(placeholder)

    # 5. Convert standalone YouTube links if they are the primary content of a paragraph
    for a in soup.find_all('a'):
        href = a.get('href', '')
        yt_id = extract_youtube_id(href)
        parent = a.parent
        if yt_id and parent and parent.name in ['p', 'div'] and len(parent.get_text(strip=True)) <= len(href) + 10:
            has_youtube = True
            placeholder = soup.new_tag('p')
            placeholder.string = f'[[YOUTUBE:{yt_id}]]'
            parent.replace_with(placeholder)

    # 6. Clean empty bookmarks and unwrap styling spans (WordPress wraps every word/phrase in font-weight 400 spans)
    for span in soup.find_all('span'):
        if span.get('data-mce-type') == 'bookmark' or 'mce_SELRES_start' in span.get('class', []):
            span.decompose()
        else:
            span.unwrap()

    # 7. Convert cleaned HTML to Markdown using custom AstroMdxConverter
    markdown_text = AstroMdxConverter(
        base_domain=base_domain,
        heading_style="ATX",
        bullets="-",
        strip=['script', 'style'],
        strong_em_symbol='*'
    ).convert_soup(soup)

    # 8. Replace YouTube placeholders with Astro MDX component
    def replace_yt(match):
        yt_id = match.group(1).replace('\\', '')
        return f'\n\n<YouTubeEmbed id="{yt_id}" />\n\n'

    # Match [[YOUTUBE:id]] and variants even if markdownify escaped underscores
    markdown_text = re.sub(r'\[\[YOUTUBE:([A-Za-z0-9_\\-]+)\]\]', replace_yt, markdown_text)
    markdown_text = re.sub(r'\[\[YOUTUBE\\?_?EMBED:([A-Za-z0-9_\\-]+)\]\]', replace_yt, markdown_text)
    markdown_text = re.sub(r'(?:\\_){3}YOUTUBE(?:\\_)?EMBED(?:\\_)?([A-Za-z0-9_\\-]+)(?:\\_){3}', replace_yt, markdown_text)

    # 9. Convert Markdown autolinks <https://...> to standard Markdown links or target="_blank" HTML links
    clean_base = base_domain.lower()
    def autolink_replacer(match):
        url = match.group(1)
        parsed = urlparse(url)
        if parsed.scheme in ('http', 'https'):
            netloc = parsed.netloc.lower()
            if netloc and not (netloc == clean_base or netloc.endswith('.' + clean_base)):
                return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        return f'[{url}]({url})'

    markdown_text = re.sub(r'<(https?://[^>]+)>', autolink_replacer, markdown_text)

    # 10. Separate adjacent inline links that were run together
    markdown_text = re.sub(r'</a>\s*<a', '</a>\n\n<a', markdown_text)
    markdown_text = re.sub(r'\)\s*\[', ')\n\n[', markdown_text)
    markdown_text = re.sub(r'</a>\s*\[', '</a>\n\n[', markdown_text)
    markdown_text = re.sub(r'\)\s*<a', ')\n\n<a', markdown_text)

    # 11. Normalize paragraph breaks: ensure blank line between paragraphs
    markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()

    return markdown_text, has_youtube


def download_image_if_needed(url: str, dest_dir: Path) -> str | None:
    """Download image to dest_dir if it doesn't exist. Returns local filename."""
    if not url:
        return None

    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename:
        return None

    dest_path = dest_dir / filename

    # Check if already exists (including case-insensitive check or extension variants)
    for existing in dest_dir.iterdir():
        if existing.is_file() and existing.name.lower() == filename.lower():
            return existing.name
        # Also check .png vs .jpg if base names match
        if existing.is_file() and existing.stem.lower() == Path(filename).stem.lower():
            return existing.name

    print(f"  Downloading missing image: {url} -> {dest_path.name}")
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            return filename
        else:
            print(f"  Warning: HTTP {resp.status_code} fetching image {url}")
            return None
    except Exception as e:
        print(f"  Warning: Failed to download {url}: {e}")
        return None


def parse_wp_xml(xml_path: Path):
    """Parse WXR XML and return attachments dict and posts list."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find('channel')
    if channel is None:
        raise ValueError(f"Invalid WordPress XML file: no <channel> found in {xml_path}")

    items = channel.findall('item')

    authors = {}
    for author_el in channel.findall('wp:author', XML_NAMESPACES):
        login_el = author_el.find('wp:author_login', XML_NAMESPACES)
        display_el = author_el.find('wp:author_display_name', XML_NAMESPACES)
        if login_el is not None and login_el.text:
            authors[login_el.text] = display_el.text if display_el is not None and display_el.text else login_el.text

    attachments = {}
    posts = []

    for item in items:
        post_type_el = item.find('wp:post_type', XML_NAMESPACES)
        post_type = post_type_el.text if post_type_el is not None else ''

        if post_type == 'attachment':
            post_id = item.find('wp:post_id', XML_NAMESPACES).text
            url_el = item.find('wp:attachment_url', XML_NAMESPACES)
            url = url_el.text if url_el is not None else ''
            title_el = item.find('title')
            title = title_el.text if title_el is not None else ''
            attachments[post_id] = {
                'url': url,
                'title': title
            }
        elif post_type == 'post':
            status_el = item.find('wp:status', XML_NAMESPACES)
            status = status_el.text if status_el is not None else ''
            if status != 'publish':
                continue

            post_id = item.find('wp:post_id', XML_NAMESPACES).text
            title = clean_text(item.find('title').text or '')
            slug_el = item.find('wp:post_name', XML_NAMESPACES)
            slug = slug_el.text if slug_el is not None and slug_el.text else ''
            
            # Post date
            date_gmt = item.find('wp:post_date_gmt', XML_NAMESPACES)
            date_local = item.find('wp:post_date', XML_NAMESPACES)
            raw_date = (date_gmt.text if date_gmt is not None and date_gmt.text != '0000-00-00 00:00:00'
                        else (date_local.text if date_local is not None else ''))
            
            # Content & Excerpt
            content_el = item.find('content:encoded', XML_NAMESPACES)
            content = content_el.text if content_el is not None else ''
            
            excerpt_el = item.find('excerpt:encoded', XML_NAMESPACES)
            excerpt = clean_text(excerpt_el.text or '') if excerpt_el is not None else ''

            # Creator / Author
            creator_el = item.find('dc:creator', XML_NAMESPACES)
            author = creator_el.text if creator_el is not None else ''

            # Categories and tags
            categories = []
            tags = []
            for cat in item.findall('category'):
                domain = cat.attrib.get('domain')
                cat_name = clean_text(cat.text or '')
                if not cat_name:
                    continue
                if domain == 'category':
                    categories.append(cat_name)
                elif domain == 'post_tag':
                    tags.append(cat_name)

            # Postmeta
            meta = {}
            for pm in item.findall('wp:postmeta', XML_NAMESPACES):
                k = pm.find('wp:meta_key', XML_NAMESPACES)
                v = pm.find('wp:meta_value', XML_NAMESPACES)
                if k is not None and v is not None and k.text:
                    meta[k.text] = v.text

            posts.append({
                'id': post_id,
                'title': title,
                'slug': slug,
                'date_str': raw_date,
                'content': content,
                'excerpt': excerpt,
                'author': author,
                'categories': categories,
                'tags': tags,
                'meta': meta
            })

    return attachments, posts, authors


def format_iso_date(date_str: str) -> str:
    """Convert 'YYYY-MM-DD HH:MM:SS' to 'YYYY-MM-DDTHH:MM:SSZ'."""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        return f"{date_str}T00:00:00Z"


def main():
    parser = argparse.ArgumentParser(description="Convert WordPress export XML to AstroWind MDX posts")
    parser.add_argument('--xml', default='scripts/WordPress_export_20261023.xml', help="Path to WordPress export XML")
    parser.add_argument('--output-dir', default='src/data/post', help="Output directory for MDX posts")
    parser.add_argument('--images-dir', default='src/assets/images', help="Assets images directory")
    parser.add_argument('--author', default=None, help="Override author name for all posts")
    parser.add_argument('--default-author', default='webmaster', help="Fallback author name if not found in XML")
    parser.add_argument('--canonical-base', default='https://tuesdaythesky.com', help="Canonical site URL")
    parser.add_argument('--site-image-alias', default='~/assets/images', help="Astro import alias for images")
    parser.add_argument('--download-images', action='store_true', default=True, help="Download featured images if missing")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existing posts in output-dir")
    parser.add_argument('--dry-run', action='store_true', help="Perform dry run without writing files")

    args = parser.parse_args()

    xml_path = Path(args.xml)
    out_dir = Path(args.output_dir)
    images_dir = Path(args.images_dir)

    if not xml_path.exists():
        print(f"Error: XML file not found at {xml_path}")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing WordPress export: {xml_path}...")
    attachments, posts, authors = parse_wp_xml(xml_path)
    print(f"Found {len(attachments)} attachments, {len(authors)} authors, and {len(posts)} published posts.\n")

    for p in posts:
        title = p['title']
        slug = p['slug'] or re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        iso_date = format_iso_date(p['date_str'])
        date_prefix = iso_date[:10]
        filename = f"{date_prefix}-{slug}.mdx"
        out_file = out_dir / filename

        print(f"Processing: [{p['id']}] {title}")
        print(f"  Target: {out_file.name}")

        if out_file.exists() and not args.overwrite:
            print(f"  Skipping (file exists, use --overwrite to replace)")
            continue

        # Determine featured image
        thumb_id = p['meta'].get('_thumbnail_id')
        image_path = None
        if thumb_id and thumb_id in attachments:
            att = attachments[thumb_id]
            att_url = att['url']
            if att_url:
                local_file = download_image_if_needed(att_url, images_dir) if args.download_images else Path(urlparse(att_url).path).name
                if local_file:
                    image_path = f"{args.site_image_alias}/{local_file}"

        # Determine excerpt
        excerpt = p['excerpt']
        if not excerpt and p['content']:
            # Strip tags and take first 160 characters
            raw_text = BeautifulSoup(p['content'], 'html.parser').get_text(separator=' ', strip=True)
            excerpt = raw_text[:160].rstrip()
            if len(raw_text) > 160:
                excerpt += '...'

        # Author: allow CLI override, otherwise resolve from XML author display name
        if args.author:
            author = args.author
        else:
            author = authors.get(p['author'], p['author']) or args.default_author

        # Category and tags
        category = p['categories'][0] if p['categories'] else 'News'
        tags = p['tags'] if p['tags'] else ['news']

        # Process MDX body & embeds (ensuring external links open in new tab)
        base_domain = urlparse(args.canonical_base).netloc.lower() or 'tuesdaythesky.com'
        body_mdx, has_youtube = process_content_to_mdx(p['content'], base_domain=base_domain)

        # Build frontmatter
        canonical_url = f"{args.canonical_base.rstrip('/')}/{slug}"
        
        frontmatter_lines = [
            "---",
            f"publishDate: {iso_date}",
            f"author: {sanitize_yaml_string(author)}",
            f"title: {sanitize_yaml_string(title)}",
            f"excerpt: {sanitize_yaml_string(excerpt)}",
        ]
        if image_path:
            frontmatter_lines.append(f"image: '{image_path}'")
        frontmatter_lines.append(f"category: {sanitize_yaml_string(category)}")
        frontmatter_lines.append("tags:")
        for t in tags:
            frontmatter_lines.append(f"  - {sanitize_yaml_string(t)}")
        frontmatter_lines.append("metadata:")
        frontmatter_lines.append(f"  canonical: {canonical_url}")
        frontmatter_lines.append("---\n")

        # Imports if needed
        import_lines = []
        if has_youtube:
            import_lines.append("import YouTubeEmbed from '~/components/common/YouTubeEmbed.astro';\n")

        full_content = "\n".join(frontmatter_lines)
        if import_lines:
            full_content += "\n" + "\n".join(import_lines) + "\n"
        full_content += body_mdx + "\n"

        if args.dry_run:
            print(f"  [DRY RUN] Would write {len(full_content)} chars to {out_file.name}")
        else:
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"  Successfully wrote {out_file.name}")

    print("\nConversion complete!")


if __name__ == '__main__':
    main()
