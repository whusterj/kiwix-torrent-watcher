import os

__all__ = ["Zim_File"]


class ZimFileException(Exception):
    pass


class Zim_File(object):
    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename

    def __repr__(self):
        return str(
            {
                "directory": self.directory,
                "filename": self.filename,
                "publication": self.publication,
            }
        )

    @property
    def basename(self):
        return "_".join(self.filename.split("_")[:-1])

    @property
    def publication(self):
        return self.filename.split("_")[-1]

    @property
    def fullpath(self):
        return os.path.join(self.directory, self.filename)

    def __lt__(self, other):
        return self.filename < other.filename

    def to_update(self, other):
        return other.publication > self.publication

    def torrent(self, server):
        return f"{server}/zim/{self.fullpath}.zim.torrent"

    @staticmethod
    def from_path(path):
        """Builds Zim_File instance from path.

        ex.: zim/wikipedia_en_all_nopic_2020-03.zim
        """
        return Zim_File(
            os.path.split(path)[0],
            os.path.splitext(os.path.split(path)[1])[0],
        )
