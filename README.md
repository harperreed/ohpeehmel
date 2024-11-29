# OhPeehMel - OPML Manager

A Python tool for managing OPML feed lists with genre categorization and health checking.

## Features

-   Deduplicates feed entries
-   Sorts feeds by genre
-   Auto-categorizes feeds based on content
-   Checks feed health and marks dead feeds
-   Caches feed status for faster subsequent runs
-   Rich terminal interface with live logging

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ohpeehmel.git
cd ohpeehmel

# Install using pip
pip install .
```

## Usage

```bash
# Run the manager
python -m ohpeehmel.main

# Or if installed via pip
ohpeehmel
```

## Requirements

-   Python 3.12 or higher
-   listparser
-   feedparser
-   rich
-   aiohttp

## Project Structure

```
ohpeehmel/
├── src/
│   └── ohpeehmel/
│       ├── ui/
│       │   ├── feeds_table.py
│       │   ├── layout.py
│       │   └── log_panel.py
│       ├── utils/
│       │   └── feed_health.py
│       ├── cache.py
│       ├── feed_manager.py
│       └── main.py
├── tests/
├── README.md
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
