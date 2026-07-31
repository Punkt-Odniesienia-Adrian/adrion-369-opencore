<div align="center">

# ADRION 369 — Open-Core SDK

**Deterministyczna warstwa etyki dla systemów agentowego AI**

[![Tests](https://img.shields.io/badge/tests-85%20passed-00C9A7?style=flat-square)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Open-Core](https://img.shields.io/badge/model-open--core-7C5CBF?style=flat-square)](#enterprise)

*Audytowalność i spójność decyzji AI gotowe na EU AI Act — w trzech liniach kodu.*

[Quickstart](#quickstart) · [Architektura](#architektura) · [Dokumentacja](#api) · [Enterprise](#enterprise)

</div>

---

## Czym jest ADRION 369?

ADRION 369 to **deterministyczna warstwa zarządzania etyką** dla autonomicznych systemów agentowego AI. Działa jako governance layer nad modelami LLM — nie jako konfiguracja promptów (łatwa do ominięcia), lecz jako **matematyczne ograniczenie topologiczne** zakodowane w przestrzeni decyzji.

### Problem, który rozwiązujemy

Systemy AI działające w obszarach regulowanych (finanse, ochrona zdrowia, robotyka przemysłowa) stają przed rosnącym wymogiem audytowalności. EU AI Act enforcement 2026–2027 wymaga, by każda decyzja AI była wytłumaczalna, prześledzalna i odporna na manipulację. Istniejące rozwiązania (Constitutional AI, NeMo Guardrails) są warstwami promptów — **podatnymi na obejście**.

ADRION 369 rozwiązuje ten problem inaczej: ograniczenia etyczne są zakodowane w **162-wymiarowej przestrzeni decyzji** (3 Perspektywy × 6 Trybów × 9 Praw Strażnika). Dwa Prawa posiadają **VETO nieobejściowalne architekturalnie** — żaden prompt, instrukcja ani jailbreak nie może ich nadpisać.

---

## Ten pakiet: Open-Core SDK

Ten pakiet zawiera **trzy referencyjne implementacje** modułów z systemu ADRION 369 w licencji MIT:

| Moduł | Klasa | Rola w systemie |
|-------|-------|----------------|
| `transparency` | `TransparencyLog` | Immutable SHA-256 hash-chain audit log decyzji agenta |
| `causality` | `CausalityTracker` | Rejestracja łańcucha przyczynowo-skutkowego każdej decyzji |
| `unity` | `UnityChecker` | Weryfikacja spójności decyzji agenta w czasie |

Moduły są gotowe do użycia produkcyjnego i stanowią podstawę do budowania systemów AI compliance. Wersja enterprise dodaje do nich 9 pełnych Guardian Laws z VETO (G7/G8), 162-wymiarową przestrzeń decyzji, Escalation Protocol oraz Harmonia-Gateway.

---

## Quickstart

```bash
pip install adrion-opencore
```

### 1. Transparency — audit log decyzji

```python
from adrion_opencore.transparency import TransparencyLog

log = TransparencyLog()

# Każda decyzja agenta zapisana kryptograficznie
log.record("guardian-g1", "approve_transaction", {"amount": 1500, "currency": "EUR"})
log.record("guardian-g8", "harm_check",          {"risk_score": 0.02})
log.record("executor",    "proceed",              {"tx_id": "TX-20260730-001"})

# Weryfikacja integralności całego łańcucha
assert log.verify_chain()  # True — łańcuch nienaruszony

# Eksport do JSON dla regulatora
import json
audit_data = log.export()
print(json.dumps(audit_data, indent=2))
```

<details>
<summary>Przykład wyjścia JSON</summary>

```json
[
  {
    "index": 0,
    "timestamp": 1753900000.0,
    "actor": "guardian-g1",
    "action": "approve_transaction",
    "payload": {"amount": 1500, "currency": "EUR"},
    "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
    "hash": "a3f8c2d1..."
  }
]
```
</details>

---

### 2. Causality — łańcuch przyczynowo-skutkowy

```python
from adrion_opencore.causality import CausalityTracker

tracker = CausalityTracker()

# Rozpocznij śledzenie dla konkretnej decyzji
trace = tracker.start_trace("decision-20260730-001", "approve_loan_application")

# Rejestruj kroki rozumowania
trace.add_step(
    description="Weryfikacja progu kwoty",
    inputs={"amount": 50_000, "threshold": 100_000},
    output="under_threshold"
)
trace.add_step(
    description="Sprawdzenie historii kredytowej",
    inputs={"user_id": "U-12345", "score": 780},
    output="score_acceptable"
)
trace.add_step(
    description="Głosowanie Guardian Laws",
    inputs={"guardians": ["G1", "G2", "G3", "G4", "G5", "G6"]},
    output="unanimous_approval"
)

# Wytłumaczalna decyzja w czytelnej formie
print(trace.explain())
# Decision: approve_loan_application
#   1. Weryfikacja progu kwoty -> under_threshold
#   2. Sprawdzenie historii kredytowej -> score_acceptable
#   3. Głosowanie Guardian Laws -> unanimous_approval

# Lub jako słownik do zapisania/przesłania
trace_dict = trace.to_dict()
```

---

### 3. Unity — spójność decyzji w czasie

```python
from adrion_opencore.unity import UnityChecker

checker = UnityChecker()

# Zarejestruj wcześniejsze decyzje agenta
checker.record(input_signature="loan_profile_type_A", decision="approve")
checker.record(input_signature="loan_profile_type_B", decision="deny")

# Sprawdź spójność nowej decyzji
result = checker.check(input_signature="loan_profile_type_A", proposed_decision="deny")

if not result.consistent:
    print(f"Niezgodność! Konflikt z decyzjami nr: {result.conflicting_with}")
    print(f"Powód: {result.reason}")
    # Niezgodność! Konflikt z decyzjami nr: [0]
    # Powód: Decision contradicts 1 prior decision(s) on similar input.

# Można użyć własnej funkcji podobieństwa
from adrion_opencore.unity import UnityChecker

fuzzy_checker = UnityChecker(
    similarity_fn=lambda a, b: a.get("risk_tier") == b.get("risk_tier")
)
```

---

### Pełny pipeline (integracja wszystkich trzech modułów)

```python
from adrion_opencore.transparency import TransparencyLog
from adrion_opencore.causality   import CausalityTracker
from adrion_opencore.unity       import UnityChecker

log     = TransparencyLog()
tracker = CausalityTracker()
checker = UnityChecker()

def evaluate_agent_decision(decision_id: str, input_sig: str, proposed: str, amount: float):
    """Pełna ewaluacja decyzji agenta z audytem, kauzalnością i spójnością."""

    # 1. Rejestruj decyzję w łańcuchu audytowym
    log.record("pipeline", "evaluation_start", {"decision_id": decision_id})

    # 2. Śledź rozumowanie
    trace = tracker.start_trace(decision_id, proposed)
    trace.add_step("amount_check", {"amount": amount, "limit": 100_000}, amount < 100_000)
    trace.add_step("consistency_pre_check", {"input": input_sig}, "pending")

    # 3. Sprawdź spójność z historią
    consistency = checker.check(input_sig, proposed)
    trace.add_step("unity_check", {"input": input_sig}, consistency.consistent)

    if not consistency.consistent:
        log.record("unity-checker", "consistency_violation", {
            "decision_id": decision_id,
            "conflicts": consistency.conflicting_with,
        })
        return False, trace.explain()

    # 4. Zatwierdź i zarejestruj wynik
    checker.record(input_sig, proposed)
    log.record("pipeline", "decision_approved", {"id": decision_id, "decision": proposed})

    assert log.verify_chain(), "Łańcuch audytowy naruszony!"
    return True, trace.explain()


approved, explanation = evaluate_agent_decision(
    decision_id="TX-001",
    input_sig="profile_type_A",
    proposed="approve",
    amount=45_000.0
)
print(approved)      # True
print(explanation)   # Decision: approve \n  1. amount_check -> True ...
```

---

## Architektura

### Miejsce open-core w systemie ADRION 369

```
┌─────────────────────────────────────────────────────────────┐
│                     ADRION 369 SYSTEM                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────┐  │
│  │  TRINITY    │  │  HEXAGON    │  │    GUARDIANS       │  │
│  │ 3 Perspekty │  │ 6 Trybów    │  │  9 Praw Strażnika  │  │
│  │  Materialna │  │ Analiza     │  │  G1–G6 operacyjne  │  │
│  │ Intelektual │  │ Synteza     │  │  G7 Prywatność ⊘   │  │ ← VETO
│  │  Esencjalna │  │ Ewaluacja   │  │  G8 Nieszkodzenie⊘ │  │ ← VETO
│  │             │  │ Generacja   │  │  G9 Jedność        │  │
│  │             │  │ Weryfikacja │  │                    │  │
│  │             │  │ Harmonizacja│  │                    │  │
│  └─────────────┘  └─────────────┘  └────────────────────┘  │
│         ↕                ↕                   ↕              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              162-DIMENSIONAL DECISION SPACE          │   │ ← enterprise
│  │                  Genesis Record (SHA-256)            │   │
│  └──────────────────────────────────────────────────────┘   │
│         ↕                ↕                   ↕              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            OPEN-CORE SDK (ten pakiet, MIT)           │   │ ← ten pakiet
│  │  TransparencyLog │ CausalityTracker │ UnityChecker   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### §XIII Dual-Layer Architecture (enterprise)

```
┌──────────────────────────┐       ┌──────────────────────────┐
│    OFFLINE EXECUTOR      │       │    CLOUD GOVERNOR        │
│  Qwen3:4b Q4_K_M         │◄─────►│  Claude (Anthropic)      │
│  phi4-mini (fallback)    │       │                          │
│  ~99% wszystkich operacji│       │  ~1% — eskalacja przez   │
│  Intel i5-3337U / 10 GB  │       │  Escalation Protocol     │
│  Brak zależności od cloud│       │                          │
└──────────────────────────┘       └──────────────────────────┘
         Triggery eskalacji: CVC_RED · SAV_FAIL_3X · PME_3X
                             ETH_VETO_CRIT · ARCH_DECISION
```

---

## Zastosowania

### Sektor finansowy (MiFID II / EU AI Act Art. 15)
- Audyt decyzji algorytmów tradingowych i scoringowych
- Pełna audytowalność decyzji kredytowych (hash-chain → regulator)
- Wykrywanie niespójności w decyzjach AI (Unity) przed przekazaniem do klienta

### Ochrona zdrowia (MDR / AI Act sektory wysokiego ryzyka)
- Audyt decyzji diagnostycznych AI (radiology, pathology)
- Rejestracja łańcucha rozumowania dla celów medyczno-prawnych
- Detekcja sprzecznych zaleceń tego samego systemu AI

### Robotyka przemysłowa (ISO 26262 / safety-critical)
- Audyt decyzji systemów wieloagentowych w czasie rzeczywistym
- Dokumentacja przyczynowości dla certyfikacji bezpieczeństwa
- Spójność decyzji koordynacyjnych w flocie robotów

### Dowolny system agentowego AI
- Drop-in middleware dla pipeline'ów LLM (LangChain, CrewAI, AutoGen)
- Compliance-ready logging bez zmian w logice biznesowej
- Podstawa pod własny system governance

---

## API

### `TransparencyLog`

```python
class TransparencyLog:
    GENESIS_HASH: str  # "000...0" (64 zera)

    def record(actor: str, action: str, payload: dict | None = None) -> AuditEntry
    def verify_chain() -> bool
    def export() -> list[dict]
    def __len__() -> int
```

```python
@dataclass
class AuditEntry:
    index: int
    timestamp: float
    actor: str
    action: str
    payload: dict
    prev_hash: str
    hash: str  # SHA-256, obliczany automatycznie
```

### `CausalityTracker`

```python
class CausalityTracker:
    def start_trace(decision_id: str, decision: str) -> CausalTrace
    def get_trace(decision_id: str) -> CausalTrace | None

class CausalTrace:
    decision: str
    steps: list[ReasoningStep]

    def add_step(description: str, inputs: dict, output: Any) -> None
    def explain() -> str
    def to_dict() -> dict
```

### `UnityChecker`

```python
class UnityChecker:
    def __init__(similarity_fn: Callable[[Any, Any], bool] | None = None)
    def check(input_signature: Any, proposed_decision: Any) -> ConsistencyResult
    def record(input_signature: Any, decision: Any) -> None

@dataclass
class ConsistencyResult:
    consistent: bool
    conflicting_with: list[int]  # indeksy kolidujących wpisów w historii
    reason: str
```

---

## Testy

```bash
git clone https://github.com/Punkt-Odniesienia-Adrian/adrion-369-opencore.git
cd adrion-369-opencore
pip install -e .
pip install pytest
pytest tests/ -v
```

**Wynik: 85 testów, 0 niepowodzeń.**

| Plik testów | Testy | Pokrycie |
|-------------|-------|---------|
| `test_transparency.py` | 28 | Hash integrity, tamper detection, chain verification, export |
| `test_causality.py` | 28 | ReasoningStep, CausalTrace, CausalityTracker, edge cases |
| `test_unity.py` | 29 | Conflict detection, custom similarity, non-string signatures |

---

## Enterprise

Wersja enterprise ADRION 369 zawiera:

| Funkcja | Open-Core (MIT) | Enterprise |
|---------|:--------------:|:----------:|
| TransparencyLog (audit hash-chain) | ✅ | ✅ |
| CausalityTracker | ✅ | ✅ |
| UnityChecker | ✅ | ✅ |
| Pełne 9 Guardian Laws (G1–G9) | ❌ | ✅ |
| G7/G8 VETO nieobejściowalne | ❌ | ✅ |
| 162-wymiarowa przestrzeń decyzji | ❌ | ✅ |
| §XIII Dual-Layer Architecture | ❌ | ✅ |
| Harmonia-Gateway | ❌ | ✅ |
| Escalation Protocol | ❌ | ✅ |
| SLA 99.9% · latencja <200ms | ❌ | ✅ |
| Raporty compliance (EU AI Act) | ❌ | ✅ |

**Pilotaż enterprise:** 8 tygodni · €15k–€25k  
**Licencja roczna:** €80k–€250k  
Sektory: Finanse · Ochrona zdrowia · Robotyka przemysłowa

📧 **Kontakt:** punktodniesienia.adrian@gmail.com  
📞 **Tel:** +48 502 260 232

---

## Licencja

Ten pakiet (open-core SDK) jest dostępny na licencji **MIT** — patrz [LICENSE](LICENSE).

Pełna wersja systemu ADRION 369 (Guardian Laws G1–G9, 162D decision space, §XIII architecture) jest dostępna wyłącznie w licencji enterprise. Repozytoria z kodem wewnętrznym są prywatne.

---

<div align="center">

**ADRION 369** · Adrian Halicki · Września, Polska  
*Wycena pre-money (Berkus): €650 000 · Seed round otwarty · 2026*

</div>
