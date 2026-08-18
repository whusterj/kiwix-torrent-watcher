import logging

from decouple import config
from transmission_rpc import Client

__all__ = ["BitTorrent_Client", "Transmission"]


class BitTorrent_Client(object):
    def __init__(self):
        """Connection to BitTorrent client"""

    def add(self, torrent_file):
        """Add torrent"""

    def remove(self, filename):
        """Removing torrent and deleting files"""


class Transmission(BitTorrent_Client):
    def __init__(self, directory):
        logging.debug("Connection to Transmission.")
        # Read the settings here, not at import time. Reading them at module
        # scope meant that importing this package needed Transmission
        # credentials, even to use Zim_File, which talks to nothing.
        self.client = Client(
            host=config("TR_HOST"),
            port=config("TR_PORT", cast=int),
            username=config("TR_USER"),
            password=config("TR_PASSWORD"),
        )
        self.directory = directory

    def add(self, torrent):
        logging.debug("Adding torrent: %s, directory: %s.", torrent, self.directory)
        self.client.add_torrent(torrent, download_dir=self.directory)

    def remove(self, torrent_name):
        logging.debug("Removing and deleting torrent: %s.", torrent_name)
        torrents = [t for t in self.client.get_torrents() if t.name == torrent_name]
        if torrents:
            self.client.remove_torrent(torrents[0].id, delete_data=True)
        else:
            logging.warning("Client could not find torrent: %s", torrent_name)
