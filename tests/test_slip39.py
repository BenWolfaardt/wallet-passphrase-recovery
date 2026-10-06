import hashlib
import hmac

import pytest
import vectors as v
from shamir_mnemonic import combine_mnemonics

import main
from bruteforce import search
from schemes import slip39

BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
XPRV_MAINNET_VERSION = bytes.fromhex("0488ade4")


def base58check(payload: bytes) -> str:
    data = payload + hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    number = int.from_bytes(data)
    encoded = ""
    while number:
        number, digit = divmod(number, 58)
        encoded = BASE58[digit] + encoded
    leading_zeros = len(data) - len(data.lstrip(b"\0"))
    return "1" * leading_zeros + encoded


def bip32_root_xprv(seed: bytes) -> str:
    digest = hmac.digest(b"Bitcoin seed", seed, "sha512")
    key, chain_code = digest[:32], digest[32:]
    # depth 0, parent fingerprint 0, child number 0
    return base58check(XPRV_MAINNET_VERSION + bytes(9) + chain_code + b"\0" + key)


def test_official_vector_secret_is_the_bip32_seed():
    # SLIP-39 uses the decrypted master secret directly as the BIP-32 seed; the vector's
    # xprv proves it, so this is the step Trezor and Keystone perform.
    assert bip32_root_xprv(bytes.fromhex(v.SLIP39_SINGLE_SECRET)) == v.SLIP39_SINGLE_XPRV


@pytest.mark.parametrize(
    ("shares", "address"),
    [
        (v.SLIP39_SINGLE_SHARE, v.SLIP39_SINGLE_ADDRESS),
        (v.SLIP39_TWO_OF_THREE, v.SLIP39_TWO_OF_THREE_ADDRESS),
    ],
    ids=["single-share", "2-of-3"],
)
def test_finds_passphrase(shares, address):
    derive = slip39.load("\n".join(shares), index=0)
    assert derive(v.PASSPHRASE) == address
    assert search(derive, v.CANDIDATE_WORDS, address, report=lambda _: None) == v.PASSPHRASE


@pytest.mark.parametrize(
    ("shares", "secret"),
    [
        (v.SLIP39_SINGLE_SHARE, v.SLIP39_SINGLE_SECRET),
        (v.SLIP39_TWO_OF_THREE, v.SLIP39_TWO_OF_THREE_SECRET),
    ],
    ids=["single-share", "2-of-3"],
)
def test_decrypts_official_master_secret(shares, secret):
    assert combine_mnemonics(shares, v.PASSPHRASE.encode()).hex() == secret


def test_wrong_passphrase_still_decrypts_to_another_wallet():
    # Why a target address is required: SLIP-39 passphrases have no checksum.
    derive = slip39.load(v.SLIP39_SINGLE_SHARE[0], index=0)
    assert derive("wrong") != v.SLIP39_SINGLE_ADDRESS


@pytest.mark.parametrize(
    "mnemonic",
    [
        v.SLIP39_TWO_OF_THREE[0],  # one share of a 2-of-3
        v.SLIP39_SINGLE_SHARE[0].replace("keyboard", "academic"),  # bad checksum
        v.SLIP39_SINGLE_SHARE[0].replace("enlarge", "enlarg"),  # unknown word
    ],
    ids=["below-threshold", "bad-checksum", "unknown-word"],
)
def test_rejects_invalid_without_echoing_shares(mnemonic):
    with pytest.raises(ValueError, match="invalid SLIP-39 shares") as error:
        slip39.load(mnemonic, index=0)
    assert not set(str(error.value).split()) & set(mnemonic.split())
    assert "enlarg" not in str(error.value)


def test_env_example_finds_passphrase(capsys):
    assert main.main(["slip39", "--env-file", ".env.example"]) == main.EXIT_FOUND
    assert "Found passphrase: 'TREZOR'" in capsys.readouterr().out
