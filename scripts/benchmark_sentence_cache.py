"""Compare cached sentence analysis with a per-token uncached baseline.

Run: python -m scripts.benchmark_sentence_cache
Timing is machine-dependent; no speedup is guaranteed.
"""
import argparse
from copy import deepcopy
import statistics
import time

from neetechs_tokenizer import analyze_text, word_analyzer
from neetechs_tokenizer.tokenizer import WORD_RE
from neetechs_tokenizer.utils import clean_text, is_arabic_word


def uncached_analysis(text: str) -> list[dict]:
    """Independent baseline using the same token boundaries and analyzer."""
    normalized = clean_text(text)
    return [
        {
            "token": match.group(),
            "start": match.start(),
            "end": match.end(),
            "analyses": (deepcopy(word_analyzer(match.group())["analyses"])
                         if is_arabic_word(match.group()) else []),
        }
        for match in WORD_RE.finditer(normalized)
    ]


def build_workload_words(repeats: int, workload: str) -> list[str]:
    """Generate reproducible benchmark tokens without running morphology."""
    if repeats < 1:
        raise ValueError("repeats must be positive")
    if workload not in {"repeated", "distinct"}:
        raise ValueError("workload must be repeated or distinct")
    if workload == "repeated":
        return ["مكتوب", "الكاتب", "مكتوب", "الكاتب"] * repeats
    alphabet = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
    base = len(alphabet)

    def suffix(index: int) -> str:
        digits = []
        while True:
            index, remainder = divmod(index, base)
            digits.append(alphabet[remainder])
            if index == 0:
                return "".join(reversed(digits))
            index -= 1

    return ["كلمة" + suffix(index) for index in range(4 * repeats)]


def benchmark(repeats: int = 100, iterations: int = 10, *, workload: str = "repeated") -> dict:
    if repeats < 1 or iterations < 1:
        raise ValueError("repeats and iterations must be positive")
    if workload not in {"repeated", "distinct"}:
        raise ValueError("workload must be repeated or distinct")
    words = build_workload_words(repeats, workload)
    sentence = " ".join(words)
    # Verify equivalent results before collecting timings.
    if analyze_text(sentence) != uncached_analysis(sentence):
        raise RuntimeError("cached and uncached results differ")
    timings = {"cached": [], "uncached": []}
    for _ in range(iterations):
        # Alternate order to reduce systematic timing bias.
        modes = ("cached", "uncached") if _ % 2 == 0 else ("uncached", "cached")
        for mode in modes:
            start = time.perf_counter()
            result = analyze_text(sentence) if mode == "cached" else uncached_analysis(sentence)
            elapsed = time.perf_counter() - start
            if len(result) != 4 * repeats:
                raise RuntimeError("unexpected token count")
            timings[mode].append(elapsed)
    cached = statistics.median(timings["cached"])
    uncached = statistics.median(timings["uncached"])
    return {
        "workload": workload,
        "tokens_per_run": 4 * repeats,
        "iterations": iterations,
        "median_seconds": cached,
        "min_seconds": min(timings["cached"]),
        "uncached_median_seconds": uncached,
        "speedup_ratio": (uncached / cached if cached > 0 else None),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--workload", choices=("repeated", "distinct"), default="repeated")
    args = parser.parse_args()
    for key, value in benchmark(args.repeats, args.iterations, workload=args.workload).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
