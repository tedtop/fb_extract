import os
import csv
import json
import re
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urlunparse
from datetime import datetime

def clean_url(url):
    """Remove query parameters from URL"""
    if not url:
        return ''
    parsed = urlparse(url)
    clean = parsed._replace(query=None, fragment=None)
    return urlunparse(clean)

def extract_post_info(soup):
    """Extract all post info from the HTML elements"""
    author_name = ''
    author_link = ''
    group_name = ''
    group_link = ''
    date = ''
    date_iso = ''

    # Extract author name and link
    # Look for links to facebook.com/[username] (not groups, videos, etc.)
    author_links = soup.find_all('a', href=re.compile(r'facebook\.com/[^/]+\?'))
    for link in author_links:
        href = link.get('href', '')
        # Skip if it's a group, video, page, etc.
        if any(x in href for x in ['/groups/', '/videos/', '/watch/', '/pages/', '/events/']):
            continue

        # Get the text content
        text = link.get_text(strip=True)
        if text and len(text) > 1:
            author_name = text
            author_link = clean_url(href)
            break

    # Extract group name and link
    # Look for links to facebook.com/groups/
    group_links = soup.find_all('a', href=re.compile(r'facebook\.com/groups/'))
    for link in group_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if text and len(text) > 5:  # Group names are usually longer
            group_name = text
            group_link = clean_url(href)
            break

    # Extract date
    # Look for links with aria-label containing a date
    date_links = soup.find_all('a', {'aria-label': re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)')})
    for link in date_links:
        aria_label = link.get('aria-label', '')
        if aria_label:
            date = aria_label
            break

    # Also try to find date in text content
    if not date:
        all_text = soup.get_text()
        date_pattern = r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})'
        match = re.search(date_pattern, all_text, re.IGNORECASE)
        if match:
            date = match.group(1)

    # Convert date to ISO format
    if date:
        try:
            date_iso = datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
        except ValueError:
            try:
                date_iso = datetime.strptime(date, '%B %d %Y').strftime('%Y-%m-%d')
            except ValueError:
                pass

    return author_name, author_link, group_name, group_link, date, date_iso

def extract_video_link(soup):
    """Extract video link from comments or DOM"""
    video_link = ''

    # Strategy 1: Check SingleFile comments for original URL
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if 'url:' in comment:
            try:
                url_part = comment.split('url:')[1].strip().split()[0]
                if 'facebook.com' in url_part and ('/videos/' in url_part or '/watch/' in url_part):
                    video_link = clean_url(url_part)
                    break
            except:
                continue

    # Strategy 2: Look for video links in the DOM
    if not video_link:
        video_links = soup.find_all('a', href=re.compile(r'facebook\.com.*(videos|watch)'))
        if video_links:
            video_link = clean_url(video_links[0].get('href', ''))

    return video_link

def extract_post_data(file_path):
    """Extract all data from a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        author_name, author_link, group_name, group_link, date, date_iso = extract_post_info(soup)
        video_link = extract_video_link(soup)

        return {
            'author_name': author_name,
            'author_link': author_link,
            'group_name': group_name,
            'group_link': group_link,
            'date': date,
            'date_iso': date_iso,
            'video_link': video_link
        }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    directory = 'fb_posts'
    csv_file = 'fb_posts_data.csv'
    json_file = 'fb_posts_data.json'
    extracted_data = []

    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found!")
        return

    # Process all HTML files
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]

    if not html_files:
        print(f"No HTML files found in '{directory}'")
        return

    print(f"Processing {len(html_files)} HTML files...")

    for filename in html_files:
        file_path = os.path.join(directory, filename)
        data = extract_post_data(file_path)

        if data:
            extracted_data.append(data)
            print(f"✓ {filename} - Author: {data['author_name'] or 'Unknown'}")
        else:
            print(f"✗ Failed to process {filename}")

    if not extracted_data:
        print("No data extracted!")
        return

    # Save to CSV
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=extracted_data[0].keys(), quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(extracted_data)
        print(f"✅ CSV saved to {csv_file}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

    # Save to JSON
    try:
        with open(json_file, 'w', encoding='utf-8') as f_json:
            json.dump(extracted_data, f_json, ensure_ascii=False, indent=2)
        print(f"✅ JSON saved to {json_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

    print(f"\n🎉 Extraction complete! Processed {len(extracted_data)} files.")

if __name__ == "__main__":
    main()
