import re
import string

# Calculate a stylometric score based on writing patterns
def get_stylometric_score(text):

    # Split the text into sentences and remove empty values
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Extract all words from the text
    words = re.findall(r"\b\w+\b", text.lower())

    # Return a neutral score if there is not enough text to analyze
    if len(words) < 20 or len(sentences) < 2:
        return 0.5

    # Calculate sentence length variance
    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]
    avg_length = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)

    # Measure vocabulary diversity
    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    # Measure punctuation density
    punctuation_count = sum(1 for char in text if char in string.punctuation)
    punctuation_density = punctuation_count / len(words)

    # Start with a neutral score and adjust it based on the metrics
    score = 0.5

    # Lower sentence variation may indicate AI-generated text
    if variance < 8:
        score += 0.2
    else:
        score -= 0.1

    # Lower vocabulary diversity may indicate AI-generated text
    if type_token_ratio < 0.55:
        score += 0.15
    else:
        score -= 0.1

    # Lower punctuation density may indicate AI-generated text
    if punctuation_density < 0.12:
        score += 0.1
    else:
        score -= 0.05

    # Keep the final score between 0.0 and 1.0
    return max(0.0, min(1.0, round(score, 2)))