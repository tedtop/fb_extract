# Facebook Posts Data Extractor

This project extracts data from saved Facebook post HTML files, including author information, group details, dates, and video links.

## Prerequisites

1. **Terminal Application**
   - Install [iTerm2](https://iterm2.com/) or [Warp](https://www.warp.dev/)

2. **Package Manager**
   - Install [Homebrew](https://brew.sh/):
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

3. **Python**
   - Install Python using Homebrew:
     ```bash
     brew install python
     ```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/tedtop/fb_extract
   cd fb_extract
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Create a directory named `fb_posts` (if it doesn't exist):
   ```bash
   mkdir -p fb_posts
   ```

2. Place all your Facebook post HTML files in the `fb_posts` directory

3. Run the extraction script:
   ```bash
   python extract_fb_posts.py
   ```

4. The script will generate two output files:
   - `fb_posts_data.csv`: Data in CSV format
   - `fb_posts_data.json`: Data in JSON format

## Output Format

The script extracts the following information for each post:
- Author name
- Author profile link
- Group name (if posted in a group)
- Group link
- Post date
- ISO formatted date
- Video link (if present)

## Error Handling

- The script will skip any files it cannot process
- Failed files will be logged in the console output
- Successfully processed files will be marked with a checkmark (✓)
