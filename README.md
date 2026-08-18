Kiwix torrent watcher
=====================

This program aims to subscribe to Kiwix ZIM files shared via bittorrent.

It keeps a complete version locally and downloads new versions if available.

This way the local file version stays up do date
and participation in sharing files is maximized, and thus content availability.

For now, integration with [Transmission BitTorrent](https://transmissionbt.com/) only.


See also [Kiwix content listing](https://wiki.kiwix.org/wiki/Content (http://download.kiwix.org/zim/wikipedia))

### Setup

Needs Python 3.12. Create a virtual environment and install the dependencies:

    python -m venv .venv
    .venv/bin/pip install -r requirements.txt

Copy `.env.example` to `.env` and fill in the Transmission settings. The program
reads `TR_HOST`, `TR_PORT`, `TR_USER`, and `TR_PASSWORD` when it connects.

### Usage

    .venv/bin/python __main__.py zim.lib /data/documents/kiwix/

### Development

    .venv/bin/pip install -r requirements-dev.txt
    .venv/bin/pytest
    .venv/bin/ruff format . && .venv/bin/ruff check .

### License

Code under GPLv3 license

Forked from https://gitlab.com/adrienandrem/kiwix-torrent-watcher by Adrien Andre