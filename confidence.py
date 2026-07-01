# Combine both detection signals into one confidence score.
def calculate_confidence(llm_score, stylometric_score):
    final_score = (llm_score * 0.60) + (stylometric_score * 0.40)
    return round(final_score, 2)

# Convert the confidence score into one of the three attribution categories.
def get_attribution(confidence):
    if confidence >= 0.70:
        return "likely_ai"
    elif confidence <= 0.39:
        return "likely_human"
    else:
        return "uncertain"