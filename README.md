# SLIP-39 / BIP-39 passphrase recovery

Forgot the passphrase on your hardware wallet but remember roughly which words went into it? Give this tool your mnemonic, the words you think the passphrase was built from, and an Ethereum address you know the wallet holds. It tries every ordered combination of those words until the derived address matches, entirely offline. I built it to recover the passphrase on my own SLIP-39 (Shamir) backup: the match was found by the SLIP-39 derivation here, checked on a Keystone, and the same passphrase then opened the wallet on a Trezor.

## Safety

- **Your mnemonic is your whole wallet.** Anyone who sees it, plus the passphrase this tool finds, owns your funds.
- **Run it offline**, ideally on an air-gapped machine booted from a live USB. The tool makes no network calls; install the dependencies first, then disconnect.
- **Don't put a real mnemonic in `.env`.** Leave `MNEMONIC` out and you are prompted for it with hidden input. There is deliberately no `--mnemonic` flag, so it never lands in your shell history.
- On a match the tool prints the passphrase and nothing else: never the mnemonic or seed.
- Once you have your funds back, move them to a fresh wallet with a new mnemonic.

## Install

Requires [uv](https://docs.astral.sh/uv/). uv fetches Python 3.14 if you don't have it.

```bash
git clone https://github.com/BenWolfaardt/slip-39-passphrase-brute-force.git
cd slip-39-passphrase-brute-force
uv sync
```

## Usage

```text
uv run main.py [slip39|bip39] [--words W [W ...]] [--target ADDRESS] [--index N] [--env-file PATH]
```

Each input comes from its flag, then `.env`, then an interactive prompt. Leave out the scheme and you'll be asked for it.

| Input | Flag | `.env` | Notes |
| --- | --- | --- | --- |
| Scheme | `slip39` / `bip39` | | prompted if omitted |
| Candidate words | `--words` | `WORDS` | space separated |
| Target address | `--target` | `TARGET_ADDRESS` | any address you know is in the wallet; mixed case must pass the EIP-55 checksum |
| Account index | `--index` | `ACCOUNT_INDEX` | `i` in `m/44'/60'/0'/0/i`, default 0 |
| Mnemonic | none | `MNEMONIC` | hidden prompt; SLIP-39 shares one per line |

Exit codes: `0` found, `1` not found, `2` invalid input, `130` interrupted.

### SLIP-39 example

`.env.example` holds the official SLIP-39 "2-of-3" test vector, so it runs as-is:

```console
$ cp .env.example .env && uv run main.py slip39
Target: 0x25b3C9CEE49c59d8864d97c4E58Db2906466c3Cf at m/44'/60'/0'/0/0
Search space: 16 candidates from 3 words
1/16 (6.2%), 71/s, ETA 0s
Found passphrase: 'TREZOR'
```

### BIP-39 example

The official BIP-39 test mnemonic `abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about`, entered at the prompt:

```console
$ uv run main.py bip39 --words ZOR wallet TRE --target 0x9c32F71D4DB8Fb9e1A58B0a80dF79935e7256FA6
Enter the mnemonic, one share per line, then an empty line. Input is hidden.
Line 1:
Line 2:
Target: 0x9c32F71D4DB8Fb9e1A58B0a80dF79935e7256FA6 at m/44'/60'/0'/0/0
Search space: 16 candidates from 3 words
1/16 (6.2%), 95/s, ETA 0s
Found passphrase: 'TREZOR'
```

## What it tries

The empty passphrase first, then every ordered selection of 1 to n of your words, **concatenated with no separator**. For `a b c` that is `""`, `a`, `b`, `c`, `ab`, `ac`, `ba`, ..., `cba`: 16 candidates. Words are case-sensitive and used as given; there are no case, digit or symbol mutations, so list every spelling you might have used as its own word.

| Words | Candidates | Time at ~90/s |
| --- | --- | --- |
| 5 | 326 | 4 s |
| 6 | 1,957 | 22 s |
| 7 | 13,700 | 2.5 min |
| 8 | 109,601 | 20 min |
| 9 | 986,410 | 3 h |
| 10 | 9,864,101 | 30 h |

8 to 9 words is the practical limit. The search space and a running ETA are printed as it goes.

## Supported

| Scheme | Passphrase | Derivation | Status |
| --- | --- | --- | --- |
| SLIP-39, single share or threshold shares | SLIP-39 native passphrase | master secret is the BIP-32 seed, `m/44'/60'/0'/0/i` | used for a real recovery (Keystone, Trezor) and tested against the official vectors |
| BIP-39, 12 to 24 words | BIP-39 passphrase | `m/44'/60'/0'/0/i` | tested against the official vectors |

Not supported: chains other than Ethereum (and EVM chains sharing its path), other derivation paths such as Ledger Live's `m/44'/60'/i'/0/0`, SLIP-39 shares used as a BIP-39 backup, GPU or multi-core search.

## Speed

One core of an Apple M4 Max manages 93 candidates/s for SLIP-39 (iteration exponent 0), 71/s for SLIP-39 with iteration exponent 2, and 97/s for BIP-39. Most of the time goes on the pure-Python secp256k1 key derivation in `eth-account`, not on the PBKDF2 stretching.

## Adding a scheme

Add `schemes/<name>.py` with a `DESCRIPTION` string and a `load(mnemonic, index)` function that returns `derive(passphrase) -> checksummed address`, then add it to `SCHEMES` in `main.py`. The shared search in `bruteforce.py` does the rest.

## Development

```bash
uv run pytest
uv tool run pre-commit run --all-files
```

The tests use only the official [SLIP-39](https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json) and [BIP-39](https://github.com/trezor/python-mnemonic/blob/master/vectors.json) vectors, plus the widely published first address of the `abandon ... about` mnemonic to pin the derivation path.

## License

[MIT](LICENSE)
