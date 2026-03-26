# Analytics Platform

Home infrastructure observability system for analyzing usage patterns across multiple components.

## Quick Start

```bash
# Just run it! (last 14 days)
./analytics

# Last 7 days
./analytics --days 7

# Custom date range
./analytics --start 2026-03-01 --end 2026-03-14

# Filter by model
./analytics --model glm-5

# Show help
./analytics --help
```

**That's it!** No venv sourcing, no PYTHONPATH, just `./analytics`.

## Data Sources

- **LiteLLM** - LLM gateway logs (PostgreSQL) ✅
- **Home server monitoring** (coming soon)
- **Network monitoring** (coming soon)

## Installation (One-Time Setup)

```bash
cd ~/dev/analytics

# 1. Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure database connection
cp .env.example .env
# Edit .env with your database credentials (DB_HOST, DB_PORT, etc.)

# 3. Test connection
./analytics --test-db
```

## Usage Examples

```bash
# Basic usage (default: last 14 days)
./analytics

# Last 7 days
./analytics --days 7

# Custom date range
./analytics --start 2026-03-01 --end 2026-03-14

# Filter to specific model
./analytics --model glm-5 --days 7

# Output JSON only (no console tables)
./analytics --format json

# Save to specific directory
./analytics --output ./reports/

# Console only (no JSON export)
./analytics --format console

# Test database connection
./analytics --test-db

# Show all options
./analytics --help
```

## Configuration

Database connection is configured in `.env`:

```bash
DB_HOST=192.168.97.2    # Your database IP
DB_PORT=5432
DB_NAME=litellm
DB_USER=taasaa
```

## Output

The tool generates:

1. **Console Report** - Beautiful tables with:
   - Executive summary
   - Top models by usage
   - Hourly/daily patterns
   - Session analysis
   - API key breakdown
   - Error analysis

2. **JSON Export** - `analytics_YYYYMMDD_HHMMSS.json` with full data

## Development

```bash
# Run tests
source venv/bin/activate
PYTHONPATH=src pytest tests/ -v

# Run with coverage
PYTHONPATH=src pytest tests/ --cov=src/analytics
```

## Architecture

Clean, modular structure without over-engineering:

```
src/analytics/
├── db.py              # Database connection
├── statistics.py      # Statistical calculations
├── output.py          # Console + JSON export
├── cli.py             # Command-line interface
└── sources/
    ├── litellm.py     # LiteLLM source ✅
    ├── server_monitor.py  # Future
    └── network.py     # Future
```

## Adding New Sources

When you're ready to add server monitoring or network monitoring:

1. Create `src/analytics/sources/server_monitor.py` with `get_requests()` and `get_sessions()` functions
2. Register in `src/analytics/sources/__init__.py`
3. Run: `./analytics --source server_monitor`

**No framework refactoring needed.**