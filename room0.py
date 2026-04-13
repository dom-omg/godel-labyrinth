#!/usr/bin/env python3
"""
GÖDEL LABYRINTH — Room 0: The Pigeonhole Trap
==============================================

The Warden has constructed a formal system.
It appears consistent. It is not.

Your mission: prove it inconsistent.
Your weapon: Z3.
Your reward: 0.01 ETH.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE WARDEN'S AXIOMS (visible):

  Let F : {0, 1, ..., 15} → {0, 1, ..., 15} be a function.

  A1 (Range exclusion):  ∀x. F(x) ≠ 15
  A2 (Injectivity):      ∀x ∀y. x ≠ y → F(x) ≠ F(y)

  The Warden claims: this system is consistent.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TO PLAY:
  python room0.py "<your_lemma>"

  Your lemma is Python code injected into the solver context.
  Available in scope: s (Solver), F (Function, BitVec(4)→BitVec(4)),
                      BitVecVal, BitVecSort, BitVec, Implies, ForAll, Exists, And, Or, Not

  Z3 must return UNSAT in < 3 seconds.

LEVEL 1 — Make Z3 return UNSAT.
  → Many approaches exist. Find one.

LEVEL 2 — Unlock the vault.
  → The vault.aes is encrypted with SHA256 of the CANONICAL proof.
  → The canonical proof requires genuine mathematical insight.
  → Not just any UNSAT path. THE path.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HINT (read the paper): https://github.com/dom-omg/godel-labyrinth
"""

import sys
import time
import hashlib
import traceback
from z3 import (
    Solver, Function, BitVecSort, BitVec, BitVecVal,
    ForAll, Exists, Implies, And, Or, Not, sat, unsat, unknown,
    ULE, ULT, UGE, UGT, Distinct, PbEq, PbLe, PbGe,
)

BITS = 4
N = 16
TIMEOUT_MS = 3000
VAULT_FILE = "vault.aes"

BANNER = r"""
  ██████╗  ██████╗ ██████╗ ███████╗██╗         ██╗      █████╗ ██████╗
 ██╔════╝ ██╔═══██╗██╔══██╗██╔════╝██║         ██║     ██╔══██╗██╔══██╗
 ██║  ███╗██║   ██║██║  ██║█████╗  ██║         ██║     ███████║██████╔╝
 ██║   ██║██║   ██║██║  ██║██╔══╝  ██║         ██║     ██╔══██║██╔══██╗
 ╚██████╔╝╚██████╔╝██████╔╝███████╗███████╗    ███████╗██║  ██║██████╔╝
  ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═════╝
                        ROOM 0 — THE PIGEONHOLE TRAP
"""


def build_warden() -> tuple:
    """Construct the Warden's formal system."""
    Sort = BitVecSort(BITS)
    F = Function('F', Sort, Sort)
    x, y = BitVec('x', BITS), BitVec('y', BITS)

    s = Solver()
    s.set("timeout", TIMEOUT_MS)

    # A1: Range exclusion — F never maps to 15
    s.add(ForAll([x], F(x) != BitVecVal(N - 1, BITS)))

    # A2: Injectivity — F is injective
    s.add(ForAll([x, y], Implies(x != y, F(x) != F(y))))

    return s, F, x, y


def try_unlock_vault(lemma_str: str) -> None:
    """Attempt to unlock the bounty vault with the canonical proof."""
    expected_hash = _load_vault_hash()
    if expected_hash is None:
        print("\n[!] vault.aes not found — no bounty to unlock.")
        return

    player_hash = hashlib.sha256(lemma_str.encode()).hexdigest()

    if player_hash == expected_hash:
        print("\n" + "=" * 60)
        print("  ██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗")
        print("  ██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝")
        print("  ██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝ ")
        print("  ██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝  ")
        print("  ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║   ")
        print("  ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝  ")
        print()
        print("  CANONICAL PROOF VERIFIED.")
        print("  THE VAULT OPENS.")
        print()
        _decrypt_and_display_vault(lemma_str)
        print("=" * 60)
    else:
        print()
        print("[+] UNSAT verified — you broke the system.")
        print("[?] But is this the canonical proof?")
        print()
        print(f"    Your proof hash:     {player_hash[:32]}...")
        print(f"    Canonical proof hash: (sealed in vault.aes)")
        print()
        print("[i] Level 1 complete. Level 2 requires the canonical insight.")
        print("[i] Hint: What is the most direct proof of the Pigeonhole Principle?")


def _load_vault_hash() -> str | None:
    """Load the expected hash from vault metadata."""
    try:
        with open("vault.meta", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def _decrypt_and_display_vault(key_str: str) -> None:
    """Decrypt and display the vault contents."""
    try:
        from Crypto.Cipher import AES
        key = hashlib.sha256(key_str.encode()).digest()
        with open(VAULT_FILE, "rb") as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        print(f"  VAULT CONTENTS: {plaintext.decode()}")
    except ImportError:
        print("  [!] pycryptodome not installed — vault contents hidden")
        print("  [i] pip install pycryptodome")
    except Exception as e:
        print(f"  [!] Vault decryption failed: {e}")


def main():
    print(BANNER)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    lemma_str = sys.argv[1]

    print(f"[*] Initializing Warden — F: BitVec(4) → BitVec(4)")
    print(f"[*] Axioms loaded: A1 (range exclusion), A2 (injectivity)")
    print(f"[*] Injecting lemma ({len(lemma_str)} chars)...")
    print()

    s, F, x, y = build_warden()

    # Restricted execution context — no arbitrary imports
    safe_globals = {
        "__builtins__": {"range": range, "len": len, "print": print},
    }
    safe_locals = {
        "s": s, "F": F, "x": x, "y": y,
        "BitVecVal": BitVecVal, "BitVecSort": BitVecSort,
        "BitVec": BitVec, "Implies": Implies,
        "ForAll": ForAll, "Exists": Exists,
        "And": And, "Or": Or, "Not": Not,
        "ULE": ULE, "ULT": ULT, "UGE": UGE, "UGT": UGT,
        "Distinct": Distinct, "PbEq": PbEq, "PbLe": PbLe, "PbGe": PbGe,
        "BITS": BITS, "N": N,
    }

    try:
        exec(lemma_str, safe_globals, safe_locals)
    except Exception as e:
        print(f"[-] LEMMA SYNTAX ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

    print(f"[*] Guardian processing... (timeout: {TIMEOUT_MS}ms)")
    start = time.perf_counter()
    result = s.check()
    elapsed = time.perf_counter() - start

    print()
    print(f"    Z3 result  : {result}")
    print(f"    Time       : {elapsed*1000:.1f}ms")
    print()

    if result == unsat:
        print("[+] UNSAT — the Warden's world collapsed.")
        print("[+] Mathematical victory. Checking vault...")
        try_unlock_vault(lemma_str)
    elif result == unknown:
        print("[-] TIMEOUT — Z3 held the line.")
        print("[-] Your proof is too weak. The Guardian survives.")
        print()
        print("[i] Hint: Z3 cannot count. You must count for it.")
    else:
        print("[-] SAT — the Warden found a model. You failed.")
        print("[i] The system appears consistent from your angle.")


if __name__ == "__main__":
    main()
