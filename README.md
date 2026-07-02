Kiwix torrent watcher
======================

This program aims to subscribe to Kiwix ZIM files shared via bittorrent.

It keeps a complete version locally and downloads new versions if available.

This way the local file version stays up do date
and participation in sharing files is maximized, and thus content availability.

For now, integration with [Transmission BitTorrent](https://transmissionbt.com/) only.

See also [Kiwix content listing](https://wiki.kiwix.org/wiki/Content) / <http://download.kiwix.org/zim/>

### Setup

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Copy `.env.example` to `.env` and fill in your Transmission RPC credentials
(and, optionally, Matrix notification settings — see below):

    cp .env.example .env

`zim.lib` lists the archive prefixes (no dates) you want to track, one per line,
e.g. `wikipedia_en_all_maxi`.

### Usage

    python __main__.py zim.lib /path/to/zim/directory/

Typically run on a schedule via cron:

    0 3 * * * cd /path/to/kiwix-torrent-watcher && .venv/bin/python __main__.py zim.lib /path/to/zim/directory/ >> /path/to/log/kiwix-torrent-watcher.log 2>&1

### Matrix notifications

When a new ZIM (or a newer version of a tracked ZIM) is detected and queued for
download, the watcher can post a notification to a Matrix room via a bot
account. This is optional — set these in `.env` to enable it:

    MATRIX_HOMESERVER=http://your.homeserver:8008
    MATRIX_USER=bot
    MATRIX_PASSWORD=your-bot-password
    MATRIX_ROOM_ID=!yourRoomId:your.matrix.server

If any of these are unset, notifications are silently skipped — the rest of
the watcher's behavior is unaffected. Notification failures (login errors,
network issues, etc.) are logged but never crash the watcher — a Matrix
hiccup should never block a ZIM download.

The bot account must first be invited to the target room (from any Matrix
client); the watcher's Matrix client auto-joins on each run if not already a
member.

### License

Code under GPLv3 license

Forked from https://gitlab.com/adrienandrem/kiwix-torrent-watcher by Adrien Andre
