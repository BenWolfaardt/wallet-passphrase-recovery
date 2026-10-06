"""Official test vectors, copied verbatim. None of these mnemonics belongs to a real wallet.

SLIP-39: https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json
BIP-39:  https://github.com/trezor/python-mnemonic/blob/master/vectors.json
All use the passphrase "TREZOR".
"""

PASSPHRASE = "TREZOR"

# SLIP-39 vector 1: "Valid mnemonic without sharing (128 bits)"
SLIP39_SINGLE_SHARE = [
    "duckling enlarge academic academic agency result length solution fridge kidney coal piece "
    "deal husband erode duke ajar critical decision keyboard",
]
SLIP39_SINGLE_SECRET = "bb54aac4b89dc868ba37d9cc21b2cece"  # gitleaks:allow
SLIP39_SINGLE_XPRV = (
    "xprv9s21ZrQH143K4QViKpwKCpS2zVbz8GrZgpEchMDg6KME9HZtjfL7iThE9w5muQA4YPHKN1u5VM1w8D4pvnjxa2B"
    "mpGMfXr7hnRrRHZ93awZ"
)

# SLIP-39 vector 4: "Basic sharing 2-of-3 (128 bits)"
SLIP39_TWO_OF_THREE = [
    "shadow pistol academic always adequate wildlife fancy gross oasis cylinder mustang wrist "
    "rescue view short owner flip making coding armed",
    "shadow pistol academic acid actress prayer class unknown daughter sweater depict flip twice "
    "unkind craft early superior advocate guest smoking",
]
SLIP39_TWO_OF_THREE_SECRET = "b43ceb7e57a0ea8766221624d01b0864"  # gitleaks:allow

# BIP-39 english vector 1
BIP39_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)
BIP39_SEED = (
    "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2c"
    "f141630c7a3c4ab7c81b2f001698e7463b04"
)

# The same BIP-39 mnemonic with an empty passphrase, at m/44'/60'/0'/0/0. Published widely as
# the first MetaMask / Ledger address for this mnemonic, so it pins the BIP-32/BIP-44 derivation
# independently of this code.
BIP39_EMPTY_PASSPHRASE_ADDRESS = "0x9858EfFD232B4033E47d90003D41EC34EcaEda94"

# m/44'/60'/0'/0/0 addresses of the seeds above. Each follows from an official seed plus the
# derivation pinned by BIP39_EMPTY_PASSPHRASE_ADDRESS; the tests re-check both halves.
SLIP39_SINGLE_ADDRESS = "0x621b6bbB9f844F114F14369D1bB4ACc907b01cC3"
SLIP39_TWO_OF_THREE_ADDRESS = "0x25b3C9CEE49c59d8864d97c4E58Db2906466c3Cf"
BIP39_ADDRESS = "0x9c32F71D4DB8Fb9e1A58B0a80dF79935e7256FA6"

# Splits "TREZOR" so the search has to find the right order, with a decoy word.
CANDIDATE_WORDS = ["ZOR", "wallet", "TRE"]
