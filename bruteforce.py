"""Scheme-independent search: candidate generation, address matching and progress reporting."""

import math
import time
from collections.abc import Callable, Iterator
from itertools import permutations

from eth_account import Account
from eth_account.hdaccount import key_from_seed
from eth_utils import is_checksum_address, is_hex_address, to_checksum_address

DERIVATION_PATH = "m/44'/60'/0'/0/{index}"
MAX_INDEX = 2**31 - 1
PROGRESS_INTERVAL_SECONDS = 5.0

Derive = Callable[[str], str]


def candidates(words: list[str]) -> Iterator[str]:
    """Yield the empty passphrase, then every ordered selection of 1..n words, concatenated."""
    yield ""
    for length in range(1, len(words) + 1):
        for selection in permutations(words, length):
            yield "".join(selection)


def search_space(word_count: int) -> int:
    return 1 + sum(math.perm(word_count, length) for length in range(1, word_count + 1))


def seed_to_address(seed: bytes, index: int) -> str:
    private_key = key_from_seed(seed, DERIVATION_PATH.format(index=index))
    return Account.from_key(private_key).address


def parse_target(address: str) -> str:
    """Return the checksummed address. Mixed-case input must carry a valid EIP-55 checksum."""
    address = address.strip()
    if not address.startswith("0x"):
        address = "0x" + address
    if not is_hex_address(address):
        raise ValueError(f"not a valid Ethereum address: {address}")
    hex_part = address[2:]
    mixed_case = hex_part != hex_part.lower() and hex_part != hex_part.upper()
    if mixed_case and not is_checksum_address(address):
        raise ValueError(f"address has an invalid EIP-55 checksum, check for a typo: {address}")
    return to_checksum_address(address)


def parse_index(raw: str | int) -> int:
    index = int(raw)
    if not 0 <= index <= MAX_INDEX:
        raise ValueError(f"account index must be between 0 and {MAX_INDEX}: {index}")
    return index


def unique_words(words: list[str]) -> list[str]:
    return list(dict.fromkeys(words))


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def search(
    derive: Derive,
    words: list[str],
    target: str,
    report: Callable[[str], None] = print,
) -> str | None:
    """Return the passphrase whose derived address equals target, or None if none matches."""
    total = search_space(len(words))
    report(f"Search space: {total:,} candidates from {len(words)} words")

    started = time.perf_counter()
    last_report = started
    for tried, passphrase in enumerate(candidates(words), start=1):
        if derive(passphrase) == target:
            return passphrase

        now = time.perf_counter()
        if tried == 1 or now - last_report >= PROGRESS_INTERVAL_SECONDS:
            rate = tried / (now - started)
            remaining = (total - tried) / rate
            report(
                f"{tried:,}/{total:,} ({tried / total:.1%}), "
                f"{rate:,.0f}/s, ETA {format_duration(remaining)}"
            )
            last_report = now
    return None
