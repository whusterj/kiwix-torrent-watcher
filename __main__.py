#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 20:53:46 2020

@author: Adrien André <adr.andre@laposte.net>
"""
import argparse
import glob
import logging
import os
import subprocess
import sys

from kiwixsync import Transmission, Zim_File, ZimFileException

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


def list_remote():
    """List remote zim files"""
    zims = set()

    # Try to read a cached list from file
    try:
        with open("remote_zims.txt", "rb") as f:
            return decode_zim_paths(f.read())
    except FileNotFoundError:
        pass

    # If it's not cached locally, then get a fresh list from the server
    process = subprocess.Popen("./list_remote.sh", stdout=subprocess.PIPE)
    out, err = process.communicate()

    if err:
        logging.warn("Error while listing remote files: %s", err)

    if out:
        decode_zim_paths(out)

    return zims


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
    files_remote = list_remote()
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
        torrent_file = remote[0].torrent("http://download.kiwix.org")

        if not local:
            # Add torrent to BT client
            downloader.add(torrent_file)
        else:  # zim present
            latest = remote[0]
            last_present = latest.filename in [zfile.filename for zfile in local]
            if not last_present:
                # Add torrent to BT client
                downloader.add(torrent_file)


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
