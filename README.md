# Hungry Spider - Complete Setup and Usage Guide

## Table of Contents
1. System Requirements
2. Installation
3. Configuration
4. Getting Started
5. CLI Commands Reference
6. Usage Examples
7. Features Explained
8. Advanced Configuration
9. Troubleshooting

---

## System Requirements

**Minimum Requirements:**
- Python 3.10 or higher
- 2GB RAM (4GB+ recommended for concurrent crawling)
- 1GB free disk space for database and exports
- Internet connection

**Optional Dependencies:**
- PostgreSQL (for production databases; SQLite works for single-user/testing)
- Proxy server list (for rotating proxies)
- API keys for OpenAI or Anthropic (if not using local Ollama)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Chiagoziem4/Hungry-Spider.git
cd Hungry-Spider
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# OR install with setup.py
pip install -e .
```

### Step 4: Install Playwright Browsers

Playwright needs to download browser binaries for dynamic crawling:

```bash
playwright install
```

This downloads Chromium, Firefox, and WebKit. You can also install just one:
```bash
playwright install chromium
```

### Step 5: Set Up Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Open .env in your text editor and configure the settings (see Configuration section below).

### Step 6: Initialize the Database

Before your first crawl, initialize the database schema:

```bash
spider db init
```

This creates the SQLite database at hungry_spider.db (or your configured PostgreSQL database).

**Verify the installation:**

```bash
spider --version
```

Should output: `Hungry Spider, version 1.0.0`

---

## Configuration

All configuration is controlled via the .env file in the project root.

### Example .env File

```bash
# ═══════════════════════════════════════════════════════════════
# AI CONFIGURATION - Choose which AI provider to use for extraction
# ═══════════════════════════════════════════════════════════════

# Options: ollama (local), openai, anthropic
AI_PROVIDER=ollama

# ─ Ollama Configuration (Local LLM - FREE)
# Ollama lets you run large language models locally on your computer
# Download from: https://ollama.ai
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
# Other available models: llama2, neural-chat, orca-mini, zephyr

# ─ OpenAI Configuration (Cloud-based)
# Requires API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
# Other options: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

# ─ Anthropic Configuration (Cloud-based)
# Requires API key from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307
# Other options: claude-3-sonnet, claude-3-opus

# ═══════════════════════════════════════════════════════════════
# DATABASE CONFIGURATION - Where to store crawled data
# ═══════════════════════════════════════════════════════════════

# Database type: sqlite (default, file-based) or postgresql (server)
DB_ENGINE=sqlite

# SQLite path - simple file-based database
SQLITE_PATH=data/hungry_spider.db

# PostgreSQL connection string (used if DB_ENGINE=postgresql)
POSTGRES_URL=postgresql://username:password@localhost:5432/hungry_spider

# ═══════════════════════════════════════════════════════════════
# CRAWLER CONFIGURATION - How the crawler behaves
# ═══════════════════════════════════════════════════════════════

# Number of concurrent requests (higher = faster but more CPU/memory)
# Recommended: 2-4 for development, 8-16 for production with proxies
CONCURRENT_REQUESTS=4

# Delay (seconds) between requests to the same domain
# Recommended: 2-5 seconds to avoid overloading servers
DOWNLOAD_DELAY=2

# Randomize delay between min and max (true/false)
# Makes crawling appear more human-like
RANDOMISE_DELAY=true

# Whether to use Playwright (dynamic JS rendering) by default
# true = use Playwright for all crawls, false = use Scrapy (faster)
USE_PLAYWRIGHT=false

# Maximum pages to crawl in a single job
MAX_PAGES_PER_CRAWL=50

# ═══════════════════════════════════════════════════════════════
# PROXY CONFIGURATION - Rotate IPs to avoid being blocked
# ═══════════════════════════════════════════════════════════════

# Enable proxy rotation (true/false)
USE_PROXIES=false

# Path to file containing proxy list (one proxy per line)
# Format examples:
#   http://proxy1.com:8080
#   http://user:pass@proxy2.com:8080
#   socks5://proxy3.com:1080
PROXY_LIST_PATH=config/proxies.txt

# Rotate to new proxy if current one gets blocked (true/false)
ROTATE_PROXY_ON_BAN=true

# ═══════════════════════════════════════════════════════════════
# LOGGING - Control verbosity of output
# ═══════════════════════════════════════════════════════════════

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

### AI Provider Setup Details

#### Option A: Ollama (FREE, Local)

Best for: Development, privacy-focused, no API costs

1. Install Ollama: https://ollama.ai
2. Start Ollama server:
   ```bash
   ollama serve
   ```
   (In another terminal)
3. Pull a model:
   ```bash
   ollama pull mistral
   # or: ollama pull llama2, ollama pull neural-chat
   ```
4. In .env:
   ```
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral
   ```

#### Option B: OpenAI (Cloud, $$$)

Best for: High quality results, GPT-4 access

1. Create account at https://platform.openai.com
2. Generate API key: https://platform.openai.com/api-keys
3. In `.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-XXXXX...
   OPENAI_MODEL=gpt-4o-mini
   ```
4. Cost: ~$0.15 per 1000 tokens (estimate $0.50-2 per crawl job)

#### Option C: Anthropic Claude (Cloud, $$$)

Best for: Very accurate extractions, long-context support

1. Create account at https://console.anthropic.com
2. Generate API key from dashboard
3. In .env:
   ```
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-XXXXX...
   ANTHROPIC_MODEL=claude-3-haiku-20240307
   ```
4. Cost: Similar to OpenAI

### Proxy Configuration

If you want to use proxies to avoid being blocked:

1. Create `config/proxies.txt`:
   ```
   http://proxy1.com:8080
   http://proxy2.com:3128
   socks5://proxy3.com:1080
   http://user:password@proxy4.com:8080
   ```

2. In .env:
   ```
   USE_PROXIES=true
   PROXY_LIST_PATH=config/proxies.txt
   ```

3. During crawl, proxies will be automatically rotated

---

## Getting Started

### Quick Test: Your First Crawl

```bash
# Make sure database is initialized
spider db init

# Crawl a simple website
spider crawl https://example.com --depth 1 --ai

# View results
spider db stats

# Export to JSON
spider export --format json --output data/exports/first_crawl
```

This will:
1. Crawl the example.com homepage
2. Extract data using AI
3. Store results in the database
4. Export extracted data as JSON

### Check What Happened

```bash
# See database statistics
spider db stats

# Shows: Total jobs, total pages crawled, total extracted records
```

---

## CLI Commands Reference

### Database Commands

#### Initialize Database
```bash
spider db init
```
Creates the database schema. Run this once before first crawl.

#### View Database Statistics
```bash
spider db stats
```
Shows:
- Total crawl jobs
- Total raw pages stored
- Total extracted records
- Database file size

### Crawling Commands

#### Crawl a Single URL
```bash
spider crawl <URL> [OPTIONS]
```

**Basic example:**
```bash
spider crawl https://news.ycombinator.com
```

**With all options:**
```bash
spider crawl https://example.com \
  --depth 3 \
  --dynamic \
  --ai \
  --proxies \
  --concurrency 4 \
  --delay 2.5 \
  --output json \
  --job-name my_job
```

**Options explained:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--depth` | INTEGER | 2 | How deep to crawl (depth 1 = homepage only) |
| `--dynamic` | BOOLEAN | false | Use Playwright (true) or Scrapy (false) for rendering |
| `--ai/--no-ai` | BOOLEAN | true | Enable/disable AI extraction |
| `--proxies/--no-proxies` | BOOLEAN | false | Enable proxy rotation |
| `--concurrency` | INTEGER | 4 | Number of concurrent requests (1-16) |
| `--delay` | FLOAT | 2.0 | Seconds between requests (avoid hammering servers) |
| `--output` | CHOICE | db | Where to save: db, json, csv, or jsonl |
| `--job-name` | STRING | auto | Human-readable name for the crawl |

#### Crawl Multiple Targets from File
```bash
spider crawl-file <YAML_FILE> [OPTIONS]
```

Create targets.yaml:
```yaml
targets:
  - url: https://news.ycombinator.com
    depth: 1
    dynamic: false
    job_name: hacker_news
    delay: 3.0
    concurrency: 2

  - url: https://example-spa.com
    depth: 2
    dynamic: true
    schema: generic
    job_name: spa_crawl
    delay: 5.0

  - url: https://shop.example.com
    depth: 2
    dynamic: false
    schema: ecommerce
    job_name: products
```

Run:
```bash
spider crawl-file config/targets.yaml
spider crawl-file config/targets.yaml --no-ai  # Skip AI extraction
```

Each target runs sequentially with its own configuration.

#### Reprocess Previously Crawled Pages
```bash
spider reprocess [OPTIONS]
```

Re-extract data from raw HTML (useful if you want to re-extract with different AI model):

```bash
spider reprocess --limit 50
```

**Options:**
- `--limit`: Number of pages to reprocess (default: 50)

This is useful when:
- You switch AI providers
- You have a better extraction prompt
- You failed to extract data first time

### Data Export Commands

#### Export All Data
```bash
spider export [OPTIONS]
```

**Export as JSON:**
```bash
spider export --format json --output data/exports/all_data
```
Output: `data/exports/all_data.json`

**Export as CSV (spreadsheet):**
```bash
spider export --format csv --output data/exports/all_data
```
Output: `data/exports/all_data.csv` (can open in Excel)

**Export as JSONL (newline-delimited JSON):**
```bash
spider export --format jsonl --output data/exports/all_data
```
Output: `data/exports/all_data.jsonl` (one JSON object per line)

**Export only recent records:**
```bash
spider export --format json --output data/exports/recent --limit 100
```

**Export from specific job:**
```bash
spider export --format json --output data/exports/job_5 --job-id 5
```

---

## Usage Examples

### Example 1: Simple News Site Scraping

Goal: Extract articles from a news website

```bash
# Step 1: Initialize (do once)
spider db init

# Step 2: Crawl the site
spider crawl https://news.ycombinator.com \
  --depth 2 \
  --ai \
  --concurrency 2 \
  --delay 3 \
  --job-name daily_hn

# Step 3: Check what was stored
spider db stats

# Step 4: Export as JSON
spider export --format json --output data/exports/hn_articles

# Step 5: View the results
cat data/exports/hn_articles.json
```

### Example 2: E-commerce Product Scraping

Goal: Extract product information from an online store

```bash
# Create config/ecommerce_targets.yaml
cat > config/ecommerce_targets.yaml << 'EOF'
targets:
  - url: https://shop.example.com/products
    depth: 2
    dynamic: false
    schema: ecommerce
    job_name: weekly_products
    concurrency: 4
    delay: 2.0
EOF

# Run crawl
spider crawl-file config/ecommerce_targets.yaml

# Export to spreadsheet format
spider export --format csv --output data/exports/products

# Open in Excel
open data/exports/products.csv  # macOS
# or: xdg-open on Linux, or just double-click on Windows
```

### Example 3: JavaScript-Heavy Website with Proxies

Goal: Scrape a modern SPA (Single Page Application) with anti-bot protection

```bash
# Make sure proxies are configured in .env
# USE_PROXIES=true
# PROXY_LIST_PATH=config/proxies.txt

spider crawl https://example-spa.com \
  --depth 1 \
  --dynamic \
  --ai \
  --proxies \
  --concurrency 1 \
  --delay 5 \
  --job-name spa_crawl_with_proxy

# Dynamic = uses Playwright (slower but handles JS)
# Proxies = rotates IP addresses
# Concurrency 1 = one request at a time (safer with proxies)
# Delay 5 = 5 seconds between requests (avoid detection)
```

### Example 4: Large-Scale Batch Processing

Goal: Crawl 5 different sites overnight

```bash
# Create batch configuration
cat > config/large_batch.yaml << 'EOF'
targets:
  - url: https://site1.com
    depth: 2
    job_name: site1_crawl
    concurrency: 4
    delay: 2
  - url: https://site2.com
    depth: 2
    job_name: site2_crawl
    concurrency: 4
  - url: https://site3.com
    depth: 1
    dynamic: true
    job_name: site3_crawl
    concurrency: 1
    delay: 5
  - url: https://site4.com
    depth: 3
    job_name: site4_crawl
  - url: https://site5.com
    depth: 2
    schema: ecommerce
    job_name: site5_products
EOF

# Start crawling (will run sequentially)
spider crawl-file config/large_batch.yaml

# Check progress
spider db stats

# After all done, export everything
spider export --format json --output data/exports/batch_results
```

### Example 5: Data Reprocessing with Different AI Model

Goal: Use a better AI model to re-extract previously crawled data

```bash
# Original crawl with cheap model
spider crawl https://example.com --depth 2

# Later, update .env to use better AI provider
# AI_PROVIDER=openai
# OPENAI_MODEL=gpt-4o

# Reprocess with new model
spider reprocess --limit 100

# Export fresh results
spider export --format json --output data/exports/reprocessed_data
```

---

## Features Explained

### 1. Dual Crawling Modes

**Static Crawler (Scrapy) - Faster**
- For websites with no JavaScript
- Fetches HTML directly
- Fast (10-100 pages/minute)
- Low CPU/memory usage
- Use: News sites, blogs, traditional websites

```bash
spider crawl https://example.com --no-dynamic
```

**Dynamic Crawler (Playwright) - Slower but Handles JS**
- For modern single-page applications (SPAs)
- Actually renders JavaScript in browser
- Slower (1-10 pages/minute)
- Higher CPU/memory usage
- Use: React/Vue/Angular sites, dynamic content

```bash
spider crawl https://example.com --dynamic
```

### 2. AI-Powered Data Extraction

The spider uses LLMs to intelligently extract structured data from messy HTML.

**How it works:**
1. Downloads HTML from URL
2. Cleans HTML (removes scripts, styles, ads)
3. Extracts plain text
4. Sends to LLM with schema definition
5. LLM returns structured JSON matching schema
6. Validates and stores result

**Example:**

Input HTML (messy):
```html
<div class="product" data-id="123">
  <h2>Amazing Widget</h2>
  <span class="price">$29.99 USD</span>
  <div class="rating">★★★★☆ (234 reviews)</div>
</div>
```

Output (structured):
```json
{
  "product_name": "Amazing Widget",
  "price": 29.99,
  "currency": "USD",
  "rating": 4.0,
  "review_count": 234
}
```

**Schema-based extraction:**

Define what fields to extract in extraction_schemas:

```yaml
# config/extraction_schemas/custom.yaml
name: custom_schema
description: My custom fields
fields:
  - product_name
  - price
  - currency
  - rating
  - review_count
  - availability
```

Use with:
```bash
spider crawl https://shop.com --schema custom_schema
```

### 3. Anti-Detection Features

**User-Agent Rotation:**
- Automatically rotates browser user agents
- Makes crawls appear like different browsers
- Prevents "bot" detection

**Proxy Rotation:**
- Cycles through list of proxy servers
- Changes IP address for each request
- Avoids IP-based rate limiting

**Human-Like Behavior:**
- Random delays between requests
- Mouse movement simulation
- Page scrolling simulation
- Makes crawling appear more human

**Usage:**
```bash
spider crawl https://example.com \
  --proxies \
  --delay 3 \
  --dynamic  # Includes mouse movement and scrolling
```

### 4. Flexible Data Storage

**SQLite (Default):**
- File-based, no setup needed
- Good for single-user/development
- Stored at hungry_spider.db
- Simple to backup (just copy file)

**PostgreSQL (Production):**
- Server-based, supports concurrent access
- Better for teams/production
- Requires PostgreSQL installation

Switch in .env:
```bash
DB_ENGINE=postgresql
POSTGRES_URL=postgresql://user:pass@localhost:5432/db
```

### 5. Multiple Export Formats

**JSON (Human-readable, complete):**
```bash
spider export --format json --output data/results.json
```

**CSV (Spreadsheet format):**
```bash
spider export --format csv --output data/results.csv
```

**JSONL (Line-delimited, for streaming/big data):**
```bash
spider export --format jsonl --output data/results.jsonl
```

### 6. Rate Limiting & Concurrency

**Concurrency:**
- `--concurrency 1`: One request at a time (safe, slowest)
- `--concurrency 4`: Four simultaneous requests (default)
- `--concurrency 16`: Sixteen simultaneous requests (fast, risky)

**Delay:**
- `--delay 1`: 1 second between requests
- `--delay 5`: 5 seconds between requests (respectful)
- `--delay 0.5`: 0.5 seconds (aggressive)

**Best practices:**
```bash
# Respectful crawling
spider crawl https://example.com \
  --concurrency 2 \
  --delay 5

# Aggressive crawling (with proxies)
spider crawl https://example.com \
  --concurrency 8 \
  --delay 1 \
  --proxies
```

### 7. Job Tracking

Each crawl is tracked with:
- Job ID (auto-generated)
- Job name (for reference)
- Start/end time
- Pages crawled
- Pages extracted
- Configuration used

View stats:
```bash
spider db stats
# Shows total jobs, pages, extractions
```

Export by job:
```bash
spider export --format json --job-id 5
# Exports only data from job #5
```

---

## Advanced Configuration

### Custom Extraction Schemas

Create new schema in `config/extraction_schemas/my_schema.yaml`:

```yaml
name: my_schema
description: Fields for my specific use case
fields:
  - field_1
  - field_2
  - field_3
  # ... as many as needed
```

Update schemas.py to register it:

```python
# In spider/ai/schemas.py, add to get_schema_model function:
if schema == "my_schema":
    return MySchemaModel

# Define the Pydantic model:
class MySchemaModel(BaseModel):
    field_1: str
    field_2: str
    field_3: str
```

Use it:
```bash
spider crawl https://example.com --schema my_schema
```

### Environment-Based Configuration

Use environment variables to control behavior:

```bash
# Set for current session
export CONCURRENT_REQUESTS=8
export DOWNLOAD_DELAY=1
export MAX_PAGES_PER_CRAWL=100

spider crawl https://example.com

# Or set inline
CONCURRENT_REQUESTS=8 spider crawl https://example.com
```

### Monitoring and Logging

Check logs in logs directory:

```bash
# View last 20 lines of log
tail -20 logs/spider.log

# Watch logs in real-time
tail -f logs/spider.log

# Search for errors
grep ERROR logs/spider.log
```

Set log level in .env:
```bash
LOG_LEVEL=DEBUG  # Most verbose
LOG_LEVEL=INFO   # Normal (recommended)
LOG_LEVEL=ERROR  # Only errors
```

---

## Troubleshooting

### "AI client not initialized"

**Problem:** Crawl fails with "AI client not initialized"

**Solutions:**
```bash
# 1. If using Ollama:
ollama serve  # Start Ollama server in another terminal

# 2. Check .env has correct AI_PROVIDER
grep AI_PROVIDER .env

# 3. If using OpenAI/Anthropic, verify API key
echo $OPENAI_API_KEY
# Should show your key, not empty
```

### "Playwright timeout after 30s"

**Problem:** JavaScript pages take too long to load

**Solutions:**
```bash
# 1. Increase timeout in code (edit spider/crawlers/playwright_crawler/dynamic_spider.py)
# Change timeout=30000 to timeout=60000

# 2. Use Scrapy instead (faster but doesn't render JS)
spider crawl https://example.com --no-dynamic

# 3. Check internet speed
ping example.com
```

### "Database locked"

**Problem:** SQLite database is locked when running multiple crawls

**Solutions:**
```bash
# 1. Use only one crawl at a time
# or

# 2. Switch to PostgreSQL for concurrent access
# Edit .env: DB_ENGINE=postgresql
```

### "No modules named spider"

**Problem:** Import error when running spider

**Solutions:**
```bash
# 1. Make sure venv is activated
source venv/bin/activate

# 2. Reinstall package
pip install -e .

# 3. Check you're in the right directory
cd /path/to/Hungry-Spider
```

### "Proxy connection refused"

**Problem:** Proxy errors when using --proxies

**Solutions:**
```bash
# 1. Verify proxy format in config/proxies.txt
cat config/proxies.txt
# Should be: http://host:port or socks5://host:port

# 2. Test proxy manually
curl -x http://proxy:port https://example.com

# 3. Test without proxies first
spider crawl https://example.com --no-proxies
```

### "Maximum pages already reached"

**Problem:** Crawl stops early with "maximum pages" error

**Solutions:**
```bash
# 1. Increase MAX_PAGES_PER_CRAWL in .env
MAX_PAGES_PER_CRAWL=200

# 2. Use --depth 1 instead of deeper crawls
spider crawl https://example.com --depth 1

# 3. Configure manually
spider crawl https://example.com --max-pages 500
```

---

## Performance Optimization Tips

### For Speed:
```bash
# Use Scrapy (not Playwright)
spider crawl https://example.com --no-dynamic

# Increase concurrency
spider crawl https://example.com --concurrency 8

# Reduce delay
spider crawl https://example.com --delay 0.5

# Use with proxies for large-scale
spider crawl https://example.com --concurrency 8 --proxies
```

### For Reliability:
```bash
# Use Playwright for JavaScript
spider crawl https://example.com --dynamic

# Reduce concurrency
spider crawl https://example.com --concurrency 2

# Increase delay
spider crawl https://example.com --delay 5

# Use proxies to avoid IP bans
spider crawl https://example.com --proxies
```

### For Quality AI Extraction:
```bash
# Use better LLM
# In .env: OPENAI_MODEL=gpt-4o (more expensive but better)
spider crawl https://example.com --ai

# Re-extract with better model
spider reprocess --limit 100
```

---

## Next Steps

1. **Set up environment:** Copy .env.example to .env and configure
2. **Choose AI provider:** Ollama (free), OpenAI, or Anthropic
3. **Initialize database:** `spider db init`
4. **Try first crawl:** `spider crawl https://example.com --depth 1`
5. **Export results:** `spider export --format json`
6. **Explore features:** Try batch crawls, different schemas, proxy rotation
7. **Monitor performance:** Check `spider db stats`

-
