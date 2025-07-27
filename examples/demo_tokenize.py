# examples/demo_tokenize.py

from neetechs_tokenizer import tokenizer

text = "استكتب المعلم الطالب الدرس"

tokens = tokenizer.tokenize(text)
print("🔹 Tokens:", tokens)

analysis = tokenizer.analyze_tokens(tokens)
print("\n🔍 Analysis:")
for item in analysis:
    print(item)
