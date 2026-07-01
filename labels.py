# Create a user-friendly transparency label based on the attribution result.
def generate_label(attribution, confidence):
    percent = round(confidence * 100)

    if attribution == "likely_ai":
        return (
            f"Likely AI-generated: Our system found strong evidence that this "
            f"content may have been generated using AI. Confidence: {percent}%. "
            f"Creators may appeal this decision if they believe it is incorrect."
        )

    if attribution == "likely_human":
        return (
            f"Likely human-written: Our system found strong evidence that this "
            f"content was written by a person. Confidence: {percent}%."
        )

    return (
        f"Uncertain attribution: Our system could not confidently determine "
        f"whether this content was written by a human or generated using AI. "
        f"Confidence: {percent}%. This label is not a final judgment."
    )