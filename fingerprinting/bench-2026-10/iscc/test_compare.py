"""Tests for compare.py on the committed records of the paper and of this rerun.

    uv run --no-project --with pytest --with numpy==2.4.6 --with scipy==1.17.1 --with pillow==12.3.0 pytest iscc
"""

import compare as c


def test_differences_of_identical_records_are_empty():
    rec = c.image_records(c.PAPER)["PDQ"]
    assert c.differences(rec, rec) == []


def test_differences_tolerate_float32_rounding_only():
    assert c.differences({"a": 0.090875014}, {"a": 0.090875231}) == []
    assert c.differences({"a": 0.4266}, {"a": 0.4391}) == ["/a"]


def test_differences_ignore_host_details_at_top_level_only():
    assert c.differences({"host": "x", "timing": 1}, {"host": "y", "timing": 2}) == []
    assert c.differences({"r": {"host": "x"}}, {"r": {"host": "y"}}) == ["/r/host"]


def test_max_bits_from_thresholds():
    assert c.max_bits(0.937501, 64) == "3"
    assert c.max_bits(0.9296885, 256) == "17"
    assert c.max_bits(0.8671885, 256) == "33"
    assert c.max_bits(1.000001, 64) == "none"


def test_values_parse_committed_numbers():
    vals = c.values((c.BENCH / "paper" / "generated" / "numbers.tex").read_text(encoding="utf-8"))
    assert vals["wm/image/ISCC-Image-64/drift/pct"] == "62.0"
    assert vals["image/ISCC-Image-64/TPR@pair@1e-07/pct"] == "42.7"


def test_citations_include_the_abstract_drift():
    assert "abstract" in c.citations()["wm/image/ISCC-Image-64/drift/pct"]


def test_unattacked_hits_cover_every_marked_photo():
    assert len(c.unattacked_hits(c.wm_records(c.PAPER)["ISCC-Image-64"])) == 300


def test_rerun_with_paper_versions_matches_paper_records():
    paper, old = c.image_records(c.PAPER), c.image_records(c.OLD)
    assert all(c.differences(paper[m], old[m]) == [] for m in c.ISCC)


def test_rebuild_reproduces_committed_numbers():
    committed = (c.BENCH / "paper" / "generated" / "numbers.tex").read_text(encoding="utf-8")
    assert c.rebuild(c.PAPER)["numbers.tex"] == committed


def test_merged_results_carry_the_update(tmp_path):
    merged = c.merged_results(tmp_path / "results")
    assert c.image_records(merged)["ISCC-Image-256"] == c.image_records(c.NEW)["ISCC-Image-256"]
    assert c.wm_records(merged)["PDQ"] == c.wm_records(c.PAPER)["PDQ"]
    assert c.wm_records(merged)["ISCC-Image-64"] == c.wm_records(c.NEW)["ISCC-Image-64"]
