from kiwixsync import Zim_File


def test_init_0():
    path = "wikibooks_pt_all_nopic_2020-06.zim"
    website, lang, selection, content, publication = "wikibooks", "pt", "all", "nopic", "2020-06"

    zfile = Zim_File.from_path(path)

    assert zfile.website == website
    assert zfile.lang == lang
    assert zfile.selection == selection
    assert zfile.content == content
    assert zfile.publication == publication
