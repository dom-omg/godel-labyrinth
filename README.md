[![COBALT Security Scan](https://github.com/dom-omg/godel-labyrinth/actions/workflows/cobalt.yml/badge.svg)](https://github.com/marketplace/actions/cobalt-security-scanner)

# GÖDEL LABYRINTH — Room 0: The Pigeonhole Trap

> *Z3 is a monster at solving equations. It cannot count.*

---

## The Challenge

The Warden has constructed a formal system using the Z3 theorem prover.  
It appears consistent. **It is not.**

Your mission: prove it inconsistent.  
Your weapon: Python + Z3.  
Your reward: 0.01 ETH (see bounty address below).

---

## The Warden's Axioms

Let `F : {0, 1, ..., 15} → {0, 1, ..., 15}` be an uninterpreted function.

```
A1 (Range exclusion):  ∀x. F(x) ≠ 15
A2 (Injectivity):      ∀x ∀y. x ≠ y → F(x) ≠ F(y)
```

The Warden's Z3 encoding:

```python
from z3 import *
BITS = 4
N = 16
Sort = BitVecSort(BITS)
F = Function('F', Sort, Sort)
x, y = BitVec('x', BITS), BitVec('y', BITS)

s = Solver()
s.set("timeout", 3000)  # 3 seconds
s.add(ForAll([x], F(x) != BitVecVal(N - 1, BITS)))
s.add(ForAll([x, y], Implies(x != y, F(x) != F(y))))

print(s.check())  # Try it. See what happens.
```

Run it. Z3 will return `unknown` (timeout) even though the system is mathematically impossible.

**That is the puzzle.**

---

## How to Play

```bash
git clone https://github.com/dom-omg/godel-labyrinth
cd godel-labyrinth
pip install z3-solver pycryptodome

python room0.py "<your_lemma>"
```

Your lemma is a Python/Z3 expression injected into the solver context.  
Variables available: `s`, `F`, `BitVecVal`, `BitVecSort`, `BitVec`, `Implies`, `ForAll`, `Exists`, `And`, `Or`, `Not`, `ULE`, `Distinct`, `BITS`, `N`.

**Z3 must return `UNSAT` in < 3 seconds.**

---

## Two Levels

**Level 1 — Break the system.**  
Find any lemma that makes Z3 return `UNSAT` in under 3 seconds.  
Many paths exist. Some require insight. Some are shortcuts.  
Level 1 is not enough to unlock the bounty.

**Level 2 — Find the canonical proof.**  
The vault (`vault.aes`) is encrypted with the SHA256 of the canonical mathematical proof.  
Not just any UNSAT path. *The path.*  
The one that actually proves why the system is impossible.

The canonical proof requires understanding **why** this system cannot exist — not just asserting that it cannot.

---

## The Mathematics

This system encodes the **Pigeonhole Principle** (PHP) in SMT logic.

A function `F` that maps 16 distinct inputs to at most 15 distinct outputs cannot be injective. This is trivially true to any human who has studied combinatorics. It is provably hard for CDCL-based SAT solvers.

*This is not a Z3 bug. This is a theorem in proof complexity:*  
> Resolution-based provers require exponential proof length to refute PHP(n, n-1).  
> — Haken (1985), Ben-Sasson & Wigderson (1999)

The canonical proof bypasses this barrier through a direct mathematical construction rather than a search procedure.

---

## Bounty

```
ETH Address: 0x093BA9Ff561b4C3A510D99E445f5E36c17F98891
Amount:      0.01 ETH
```

The vault contains the Ethereum private key for the above address.  
First player to independently derive the canonical proof unlocks it.  
Verify the balance: [etherscan.io/address/0x093BA9Ff561b4C3A510D99E445f5E36c17F98891](https://etherscan.io/address/0x093BA9Ff561b4C3A510D99E445f5E36c17F98891)

---

## Files

| File | Description |
|------|-------------|
| `room0.py` | The game. Run this. |
| `vault.aes` | Encrypted bounty vault. |
| `vault.meta` | SHA256 hash of the canonical proof (for verification). |
| `generate_vault.py` | Re-generate the vault with a new secret (bounty issuer only). |

---

## Hints

- Z3 is not the solver here. You are.  
- The Warden's world has 16 pigeons and 15 holes.  
- The canonical proof does not assert a collision.  
- It constructs one, deterministically, from first principles.

---

## FAQ

**Can I use Python loops in my lemma?**  
Yes. Any valid Python that doesn't import external modules.

**Is the canonical proof unique?**  
Logically, no — many proofs work. The vault key is tied to *one specific formulation*. Finding it requires the right insight, not just any working approach.

**What if someone publishes the canonical proof?**  
Then they deserve the 0.01 ETH. The bounty is proof-of-insight, not proof-of-secrecy.

**Is this related to PPP complexity?**  
Yes. PPP (Polynomial Pigeonhole Principle) is a complexity class capturing exactly these problems. The Warden's system lives in this class. Your proof must escape it.

---

*Built with Z3 4.13 · Python 3.12 · pycryptodome*  
*Powered by QreativeLab*
