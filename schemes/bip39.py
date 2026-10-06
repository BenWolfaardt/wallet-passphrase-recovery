"""BIP-39 mnemonic with a BIP-39 passphrase (the "25th word"), as used by most wallets."""

from eth_account.hdaccount import Mnemonic, ValidationError, seed_from_mnemonic

from bruteforce import Derive, seed_to_address

DESCRIPTION = "BIP-39 mnemonic with a BIP-39 passphrase: Ledger, Trezor, MetaMask and most others"


def load(mnemonic: str, index: int) -> Derive:
    """Validate the mnemonic once, then return a passphrase -> address function."""
    words = " ".join(mnemonic.split())
    try:
        seed_from_mnemonic(words, "")
        words = Mnemonic(Mnemonic.detect_language(words)).expand(words)
    except ValidationError:
        # The library's message repeats the mnemonic, so it must not reach the terminal.
        raise ValueError("invalid BIP-39 mnemonic: unknown word or bad checksum") from None

    def derive(passphrase: str) -> str:
        return seed_to_address(Mnemonic.to_seed(words, passphrase), index)

    return derive
