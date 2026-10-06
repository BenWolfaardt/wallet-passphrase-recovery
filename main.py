"""Recover a forgotten wallet passphrase from words you think it contains. Runs fully offline.

Each input is taken from, in order: its command-line flag, the .env file, an interactive prompt.
The mnemonic has no flag, so it never lands in shell history; without .env it is read with getpass.
"""

import argparse
import getpass
import sys
from pathlib import Path

from dotenv import dotenv_values

from bruteforce import parse_index, parse_target, search, unique_words
from schemes import bip39, slip39

SCHEMES = {
    "slip39": slip39,
    "bip39": bip39,
}

EXIT_FOUND = 0
EXIT_NOT_FOUND = 1
EXIT_BAD_INPUT = 2
EXIT_INTERRUPTED = 130


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    scheme_help = "\n".join(f"  {name:8} {module.DESCRIPTION}" for name, module in SCHEMES.items())
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            f"schemes:\n{scheme_help}\n\n"
            "Candidates tried: the empty passphrase, then every ordered selection of 1..n of the\n"
            "given words, concatenated with no separator. For n words that is\n"
            "1 + sum(n!/(n-k)!) candidates: 3 words = 16, 8 words = 109,601."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("scheme", nargs="?", choices=SCHEMES, help="prompted for if omitted")
    parser.add_argument("--words", nargs="+", help="candidate passphrase words (.env: WORDS)")
    parser.add_argument(
        "--target", help="address the passphrase should unlock (.env: TARGET_ADDRESS)"
    )
    parser.add_argument(
        "--index",
        type=int,
        help="account index i in m/44'/60'/0'/0/i (.env: ACCOUNT_INDEX, default 0)",
    )
    parser.add_argument(
        "--env-file", type=Path, default=Path(".env"), help="default: .env, ignored if absent"
    )
    return parser.parse_args(argv)


def prompt_scheme() -> str:
    names = "/".join(SCHEMES)
    while (choice := input(f"Scheme [{names}]: ").strip().lower()) not in SCHEMES:
        print(f"Choose one of: {names}")
    return choice


def prompt_mnemonic() -> str:
    print("Enter the mnemonic, one share per line, then an empty line. Input is hidden.")
    lines = []
    while line := getpass.getpass(f"Line {len(lines) + 1}: ").strip():
        lines.append(line)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    env = dotenv_values(args.env_file) if args.env_file.is_file() else {}

    try:
        scheme = SCHEMES[args.scheme or prompt_scheme()]
        words = (
            args.words or (env.get("WORDS") or input("Candidate words, space separated: ")).split()
        )
        target = parse_target(args.target or env.get("TARGET_ADDRESS") or input("Target address: "))
        index = parse_index(args.index if args.index is not None else env.get("ACCOUNT_INDEX") or 0)
        derive = scheme.load(env.get("MNEMONIC") or prompt_mnemonic(), index)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_BAD_INPUT
    except EOFError, KeyboardInterrupt:
        print("\nNo input, exiting.")
        return EXIT_INTERRUPTED

    if len(unique := unique_words(words)) != len(words):
        print(f"Ignoring {len(words) - len(unique)} duplicate word(s)")
    print(f"Target: {target} at m/44'/60'/0'/0/{index}")
    try:
        passphrase = search(derive, unique, target)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return EXIT_INTERRUPTED

    if passphrase is None:
        print("No candidate matched. Check the word list, the target address and the index.")
        return EXIT_NOT_FOUND
    print(f"Found passphrase: {passphrase!r}" if passphrase else "Found: the passphrase is empty")
    return EXIT_FOUND


if __name__ == "__main__":
    sys.exit(main())
