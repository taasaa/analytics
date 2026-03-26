# Analytics Quick Reference

## 🚀 Quick Start

```bash
./analytics              # Last 14 days
./analytics --days 7     # Last 7 days
./analytics --help       # Show all options
```

## 📊 Common Commands

| Command | Description |
|---------|-------------|
| `./analytics` | Analyze last 14 days (default) |
| `./analytics --days 7` | Last 7 days |
| `./analytics --days 30` | Last 30 days |
| `./analytics --start 2026-03-01 --end 2026-03-14` | Custom date range |
| `./analytics --model glm-5` | Filter to specific model |
| `./analytics --format console` | Console only, no JSON export |
| `./analytics --format json` | JSON only, no console output |
| `./analytics --test-db` | Test database connection |
| `./analytics --help` | Show all options |

## 📁 Output

- **Console**: Beautiful tables with charts and statistics
- **JSON**: `analytics_YYYYMMDD_HHMMSS.json` file with full data

## 🔧 One-Time Setup

```bash
./setup.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Create `.env` config file
4. Test database connection

## ⚙️ Configuration

Edit `.env` to change database connection:

```bash
DB_HOST=192.168.97.2
DB_PORT=5432
DB_NAME=litellm
DB_USER=taasaa
```

## 📈 What You Get

**Executive Summary:**
- Total requests, success rate, unique models
- Total tokens processed

**Model Usage:**
- Top models by request count
- Mean, median, P95 tokens
- Success rates

**Temporal Patterns:**
- Hourly distribution (when you use it most)
- Daily distribution (which days)
- Peak usage times

**Sessions:**
- Top sessions by request count
- Multi-model sessions
- Session duration

**API Keys:**
- Request sources breakdown
- Most used model per key

**Errors:**
- Error count by model
- Error rate analysis

## 🐛 Troubleshooting

**Database connection failed:**
```bash
# Check your .env configuration
cat .env

# Test connection
./analytics --test-db
```

**Command not found:**
```bash
# Make sure you're in the analytics directory
cd ~/dev/analytics

# Run with explicit path
./analytics
```

**Missing dependencies:**
```bash
# Re-run setup
./setup.sh
```

## 📚 Full Documentation

See `README.md` for complete documentation.