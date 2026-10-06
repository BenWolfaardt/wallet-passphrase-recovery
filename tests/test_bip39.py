import pytest
import vectors as v
from eth_account.hdaccount import Mnemonic

from bruteforce import search, seed_to_address
from schemes import bip39


def test_official_vector_seed():
    assert Mnemonic.to_seed(v.BIP39_MNEMONIC, v.PASSPHRASE).hex() == v.BIP39_SEED


def test_derivation_matches_published_address():
    assert bip39.load(v.BIP39_MNEMONIC, index=0)("") == v.BIP39_EMPTY_PASSPHRASE_ADDRESS


def test_finds_passphrase():
    derive = bip39.load(v.BIP39_MNEMONIC, index=0)
    assert derive(v.PASSPHRASE) == seed_to_address(bytes.fromhex(v.BIP39_SEED), 0)
    assert search(derive, v.CANDIDATE_WORDS, v.BIP39_ADDRESS, report=lambda _: None) == v.PASSPHRASE


def test_index_changes_address():
    assert bip39.load(v.BIP39_MNEMONIC, index=1)("") != v.BIP39_EMPTY_PASSPHRASE_ADDRESS


@pytest.mark.parametrize(
    "mnemonic",
    [
        v.BIP39_MNEMONIC.replace("about", "abandon"),  # bad checksum
        v.BIP39_MNEMONIC.replace("about", "zzzzz"),  # unknown word
    ],
)
def test_rejects_invalid_without_echoing_mnemonic(mnemonic):
    with pytest.raises(ValueError, match="invalid BIP-39 mnemonic") as error:
        bip39.load(mnemonic, index=0)
    assert "abandon" not in str(error.value)
