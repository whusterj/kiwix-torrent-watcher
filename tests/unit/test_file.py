from kiwixsync import Zim_File

# A path as list_remote.sh reports it: relative to the server's /zim/ directory.
PATH = "zimit/wikibooks_pt_all_nopic_2020-06.zim"


def test_from_path_splits_directory_and_filename():
    zfile = Zim_File.from_path(PATH)

    assert zfile.directory == "zimit"
    assert zfile.filename == "wikibooks_pt_all_nopic_2020-06"


def test_basename_drops_the_publication_date():
    assert Zim_File.from_path(PATH).basename == "wikibooks_pt_all_nopic"


def test_publication_is_the_last_field():
    assert Zim_File.from_path(PATH).publication == "2020-06"


def test_fullpath_rejoins_directory_and_filename():
    assert Zim_File.from_path(PATH).fullpath == "zimit/wikibooks_pt_all_nopic_2020-06"


def test_torrent_builds_the_download_url():
    zfile = Zim_File.from_path(PATH)

    # torrent() prepends /zim/ because list_remote.sh reports paths relative to it.
    assert zfile.torrent("http://download.kiwix.org") == "http://download.kiwix.org/zim/zimit/wikibooks_pt_all_nopic_2020-06.zim.torrent"


def test_to_update_is_true_when_the_other_is_newer():
    older = Zim_File.from_path("zimit/wikibooks_pt_all_nopic_2020-06.zim")
    newer = Zim_File.from_path("zimit/wikibooks_pt_all_nopic_2020-07.zim")

    assert older.to_update(newer)
    assert not newer.to_update(older)


def test_sorting_is_by_filename():
    first = Zim_File.from_path("zimit/wikibooks_pt_all_nopic_2020-06.zim")
    second = Zim_File.from_path("zimit/wikibooks_pt_all_nopic_2020-07.zim")

    assert sorted([second, first]) == [first, second]
