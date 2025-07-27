# examples/demo_translate.py

from neetechs_tokenizer import translator, grammar_corrector, diacritics

text = "انا يحب الذكاء الاصطناعي"
corrected = grammar_corrector.correct_grammar(text)
diacritic_text = diacritics.restore_diacritics(corrected)
translated = translator.translate(corrected)

print("📝 Original: ", text)
print("✅ Corrected: ", corrected)
print("🔡 With Diacritics: ", diacritic_text)
print("🌍 English Translation: ", translated)
