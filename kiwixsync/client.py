import logging

from decouple import config
from transmission_rpc import Client

__all__ = ["BitTorrent_Client", "Transmission"]


HOST = config("TR_HOST")
PORT = config("TR_PORT", cast=int)
USERNAME = config("TR_USER")
PASSWORD = config("TR_PASSWORD")


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
        self.client = Client(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
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
            logging.warn("Client could not find torrent: %s", torrent_name)
