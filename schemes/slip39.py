"""SLIP-39 with the native SLIP-39 passphrase, as used by Trezor and Keystone Shamir backups.

The passphrase decrypts the encrypted master secret, and the master secret is the BIP-32 seed.
Any passphrase decrypts to *some* wallet, so a match is only provable against a known address.
"""

from shamir_mnemonic import MnemonicError, decode_mnemonics, recover_ems

from bruteforce import Derive, seed_to_address

DESCRIPTION = "SLIP-39 (Shamir) shares with a SLIP-39 passphrase: Trezor, Keystone"


def load(mnemonic: str, index: int) -> Derive:
    """Combine the shares once, then return a passphrase -> address function."""
    shares = [line.strip() for line in mnemonic.splitlines() if line.strip()]
    try:
        encrypted_secret = recover_ems(decode_mnemonics(shares))
    except MnemonicError:
        # The library's messages quote share words, so they must not reach the terminal.
        raise ValueError(
            "invalid SLIP-39 shares: unknown word, bad checksum, mismatched shares "
            "or fewer shares than the threshold"
        ) from None

    def derive(passphrase: str) -> str:
        return seed_to_address(encrypted_secret.decrypt(passphrase.encode()), index)

    return derive
