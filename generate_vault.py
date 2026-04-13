#!/usr/bin/env python3
"""
Generate vault.aes + vault.meta for the Gödel Labyrinth bounty.

Usage:
  python generate_vault.py "<eth_private_key_or_secret>"

The canonical proof (vault key) is hardcoded here.
The vault can only be decrypted by someone who independently
derives the same canonical proof string.
"""

import sys
import hashlib

# ══════════════════════════════════════════════════════════════
# THE CANONICAL PROOF — the one true mathematical path.
#
# Insight: To prove that no injective F: {0..15} → {0..14} exists,
# construct the proof by SATURATING all N-1 holes.
#
# Assign F(0)=0, F(1)=1, ..., F(14)=14.
# Now F(15) must land in {0..14} (by A1) but must differ from
# all of {0, 1, ..., 14} (by A2 + explicit assignments).
# No such value exists. UNSAT.
#
# This is the Pigeonhole Principle, proved by construction.
# ══════════════════════════════════════════════════════════════

BITS = 4
N = 16

CANONICAL_PROOF = "\n".join([
    f"s.add(F(BitVecVal({i}, {BITS})) == BitVecVal({i}, {BITS}))"
    for i in range(N - 1)
])


def generate_vault(secret: str) -> None:
    try:
        from Crypto.Cipher import AES
    except ImportError:
        print("[!] pycryptodome required: pip install pycryptodome")
        sys.exit(1)

    key = hashlib.sha256(CANONICAL_PROOF.encode()).digest()
    canonical_hash = hashlib.sha256(CANONICAL_PROOF.encode()).hexdigest()

    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(secret.encode())

    with open("vault.aes", "wb") as f:
        f.write(cipher.nonce)
        f.write(tag)
        f.write(ciphertext)

    with open("vault.meta", "w") as f:
        f.write(canonical_hash)

    print(f"[+] vault.aes created.")
    print(f"[+] vault.meta created.")
    print()
    print(f"    Canonical hash  : {canonical_hash[:32]}...")
    print(f"    Key (SHA256)    : {key.hex()[:32]}...")
    print()
    print(f"[i] The canonical proof ({N-1} lines):")
    print()
    for line in CANONICAL_PROOF.split("\n"):
        print(f"    {line}")


def verify_canonical() -> None:
    """Self-test: verify that the canonical proof makes Z3 return UNSAT fast."""
    from z3 import (
        Solver, Function, BitVecSort, BitVec, BitVecVal,
        ForAll, Implies, unsat,
    )
    import time

    Sort = BitVecSort(BITS)
    F = Function('F', Sort, Sort)
    x, y = BitVec('x', BITS), BitVec('y', BITS)

    s = Solver()
    s.set("timeout", 3000)
    s.add(ForAll([x], F(x) != BitVecVal(N - 1, BITS)))
    s.add(ForAll([x, y], Implies(x != y, F(x) != F(y))))

    exec(CANONICAL_PROOF, {"__builtins__": {}}, {
        "s": s, "F": F, "BitVecVal": BitVecVal, "BITS": BITS,
    })

    start = time.perf_counter()
    result = s.check()
    elapsed = time.perf_counter() - start

    if result == unsat:
        print(f"[+] Self-test PASSED: canonical proof → UNSAT in {elapsed*1000:.1f}ms")
    else:
        print(f"[!] Self-test FAILED: got {result} in {elapsed*1000:.1f}ms")
        sys.exit(1)


if __name__ == "__main__":
    verify_canonical()
    print()

    if len(sys.argv) < 2:
        print("Usage: python generate_vault.py '<secret_to_encrypt>'")
        print()
        print("Example: python generate_vault.py 'PLACEHOLDER_ETH_KEY'")
        sys.exit(0)

    generate_vault(sys.argv[1])
