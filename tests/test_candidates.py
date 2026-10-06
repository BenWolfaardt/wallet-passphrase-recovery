import pytest

from bruteforce import (
    candidates,
    parse_index,
    parse_target,
    search,
    search_space,
    unique_words,
)


def test_candidates_are_empty_then_ordered_selections_concatenated():
    assert list(candidates(["a", "b", "c"])) == [
        "",
        "a", "b", "c",
        "ab", "ac", "ba", "bc", "ca", "cb",
        "abc", "acb", "bac", "bca", "cab", "cba",
    ]  # fmt: skip


@pytest.mark.parametrize("word_count", range(7))
def test_search_space_matches_generator(word_count):
    words = [f"w{i}" for i in range(word_count)]
    assert search_space(word_count) == sum(1 for _ in candidates(words))


def test_search_space_for_eight_words():
    assert search_space(8) == 109_601


def test_unique_words_keeps_first_occurrence_order():
    assert unique_words(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_search_returns_first_match_and_none_when_absent():
    def derive(passphrase):
        return "hit" if passphrase == "ba" else "miss"

    assert search(derive, ["a", "b"], "hit", report=lambda _: None) == "ba"
    assert search(derive, ["a", "c"], "hit", report=lambda _: None) is None


def test_search_finds_empty_passphrase():
    assert search(lambda p: "hit" if p == "" else "miss", ["a"], "hit", report=lambda _: None) == ""


@pytest.mark.parametrize(
    "raw",
    [
        "0x9858EfFD232B4033E47d90003D41EC34EcaEda94",
        "0x9858effd232b4033e47d90003d41ec34ecaeda94",
        "9858effd232b4033e47d90003d41ec34ecaeda94",
    ],
)
def test_parse_target_accepts_and_checksums(raw):
    assert parse_target(raw) == "0x9858EfFD232B4033E47d90003D41EC34EcaEda94"


@pytest.mark.parametrize(
    "raw",
    [
        "0x9858efFD232B4033E47d90003D41EC34EcaEda94",  # mixed case, wrong EIP-55 checksum
        "0x9858effd232b4033e47d90003d41ec34ecaeda9",  # 39 hex chars
        "not an address",
    ],
)
def test_parse_target_rejects(raw):
    with pytest.raises(ValueError):
        parse_target(raw)


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), (7, 7), ("2147483647", 2**31 - 1)])
def test_parse_index_accepts(raw, expected):
    assert parse_index(raw) == expected


@pytest.mark.parametrize("raw", ["-1", 2**31, "x"])
def test_parse_index_rejects(raw):
    with pytest.raises(ValueError):
        parse_index(raw)
