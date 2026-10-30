"""Reproducible microbenchmark for repeated Arabic sentence analysis.

Run: python -m scripts.benchmark_sentence_cache
Results are environment-dependent; no performance threshold is asserted.
"""
import argparse
import statistics
import time

from neetechs_tokenizer import analyze_text


def benchmark(repeats: int = 100, iterations: int = 10) -> dict:
    if repeats < 1 or iterations < 1:
        raise ValueError("repeats and iterations must be positive")
    sentence = " ".join(["مكتوب", "الكاتب", "مكتوب", "الكاتب"] * repeats)
    measurements = []
    # Warm up the lexicon's one-time loading overhead.
    analyze_text(sentence)
    for _ in range(iterations):
        start = time.perf_counter()
        result = analyze_text(sentence)
        measurements.append(time.perf_counter() - start)
        if len(result) != 4 * repeats:
            raise RuntimeError("unexpected token count")
    return {
        "tokens_per_run": 4 * repeats,
        "iterations": iterations,
        "median_seconds": statistics.median(measurements),
        "min_seconds": min(measurements),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=10)
    args = parser.parse_args()
    for key, value in benchmark(args.repeats, args.iterations).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
