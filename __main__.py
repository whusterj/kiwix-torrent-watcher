#!/usr/bin/env python
import argparse
import glob
import logging
import os
import re
import sys
import urllib.request

from kiwixsync import Transmission, Zim_File, ZimFileException, notify

ZIM_HREF_RE = re.compile(r'href="([^"]+\.zim)"')

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def read_library(filename):
    """Read file list from configuration file"""
    library = set()

    with open(filename, "r") as lib_file:
        library = set([line[:-1] for line in lib_file])

    return library


def list_local(directory):
    """List local zim files"""
    zims = set()
    for path in glob.glob("%s/**/*.zim" % directory, recursive=True):
        try:
            zim = Zim_File.from_path(path)
            zims.add(zim)
        except Exception:
            logging.warning("Error loading file: %s", path)

    return zims


def decode_zim_paths(paths):
    zims = set()
    for path in paths.decode("UTF-8").splitlines():
        if path.endswith(".zim"):
            try:
                zim = Zim_File.from_path(path)
            except ZimFileException:
                continue
            zims.add(zim)
    return zims


def list_remote(library):
    """List remote zim files for the categories referenced in library.

    Fetches each category's plain HTTPS directory listing (e.g.
    https://download.kiwix.org/zim/wikipedia/) and parses the .zim
    filenames out of the HTML index. Always fetches fresh — never cached,
    since a stale cache would silently prevent the watcher from ever
    detecting new ZIM versions.

    Kiwix category directories match the first underscore-delimited token
    of the tracked radical (e.g. "wikipedia_en_all_maxi" -> "wikipedia").
    This replaced an rsync-based listing (download.kiwix.org's rsync daemon
    has been decommissioned as of their migration to hub.kiwix.org).
    """
    categories = sorted({radical.split("_")[0] for radical in library})
    lines = []

    for category in categories:
        url = f"https://download.kiwix.org/zim/{category}/"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            logging.warning("Error listing remote category %s: %s", category, exc)
            continue

        for filename in ZIM_HREF_RE.findall(html):
            lines.append(f"{category}/{filename}")

    if not lines:
        return set()

    return decode_zim_paths("\n".join(lines).encode("utf-8"))


def find_missing(local_files, remote_files):
    """Remote files not present localy"""
    local = {zim.basename: zim for zim in local_files}

    return {zim for zim in remote_files if zim.basename not in local}


def to_update(local_files, remote_files):
    remote = {zim.basename: zim for zim in remote_files}
    present = {zim for zim in local_files if zim.basename in remote}

    return {zim.filename: remote[zim.basename].filename for zim in present if zim.to_update(remote[zim.basename])}


def clean(library, local_files, torrent_client, keep=0):
    """Remove former file versions"""
    zims_local = sorted(local_files)

    for zim in library:
        local = [zfile for zfile in zims_local if zfile.basename == zim]

        if local:
            # logging.debug("Zim, Local: %s, %s", zim, [zfile.filename for zfile in local])
            former = local[:-1]
            if former:
                # logging.debug("Zim, Former: %s, %s", zim, [zfile.filename for zfile in former])
                for zfile in former[keep:]:
                    torrent_client.remove(zfile.filename + ".zim")


def main(library, directory, url):
    logging.debug("Library: %s", library)

    # Clean

    # List local files
    files_local = list_local(directory)
    zims_local = [zfile for zfile in files_local if zfile.basename in library]
    # logging.debug("Local files: %s" % [zfile.filename for zfile in sorted(zims_local)])

    downloader = Transmission(directory)

    logging.info("Removing former versions…")
    clean(library, zims_local, downloader)

    # Process

    logging.info("Processing…")

    # List local files
    files_local = list_local(directory)
    zims_local = [zfile for zfile in files_local if zfile.basename in library]
    logging.debug("Local files: %s" % [zfile.filename for zfile in sorted(zims_local)])

    # List remote files
    files_remote = list_remote(library)
    zims_remote = [zfile for zfile in files_remote if zfile.basename in library]
    logging.debug("Remote files: %s" % [zfile.filename for zfile in zims_remote])

    for zim in library:
        # logging.debug("Zim: %s", zim)
        local, remote = (
            sorted([zfile for zfile in zims_local if zfile.basename == zim], reverse=True),
            sorted([zfile for zfile in zims_remote if zfile.basename == zim], reverse=True),
        )
        logging.debug("Local: %s", [zfile.filename for zfile in local])
        logging.debug("Remote: %s", [zfile.filename for zfile in remote])

        if not remote:
            logging.warning("No remote match for tracked zim %s (renamed or discontinued upstream?)", zim)
            notify(f"WARNING: no remote match for tracked zim {zim} (renamed or discontinued upstream?)")
            continue

        torrent_file = remote[0].torrent("http://download.kiwix.org")

        if not local:
            # Add torrent to BT client
            downloader.add(torrent_file)
            notify(f"New ZIM download queued: {remote[0].filename}")
        else:  # zim present
            latest = remote[0]
            last_present = latest.filename in [zfile.filename for zfile in local]
            if not last_present:
                # Add torrent to BT client
                downloader.add(torrent_file)
                notify(f"ZIM update queued: {latest.filename}")


if __name__ == "__main__":
    # execute only if run as a script

    url = "https://download.kiwix.org/zim"  # "ftp://mirror.download.kiwix.org"

    PARSER = argparse.ArgumentParser(prog="ktw")
    PARSER.add_argument("lib_file", help="Library file")
    PARSER.add_argument("repo", help="ZIM files directory")
    ARGS = PARSER.parse_args()

    LIB = ARGS.lib_file
    REPO = ARGS.repo

    # Check input data
    if not os.path.isfile(LIB):
        logging.error("Error reading file: %s", LIB)
        sys.exit(1)
    if not os.path.isdir(REPO):
        logging.error("Error accessing directory: %s", REPO)
        sys.exit(2)

    # Read configuration (file list)
    library = read_library(LIB)

    main(library, REPO, url)
