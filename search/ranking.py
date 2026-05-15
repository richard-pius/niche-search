import re
from math import log

def tokenize(text):
    """Return list of lowercase words from a string."""
    if not text:
        return []
    return re.findall(r'\b\w+\b', text.lower())

def tf(word, tokens):
    """Term frequency – simple count of a word in a token list."""
    return tokens.count(word)

def calculate_relevance(query, result, static_boost=0.0):
    """
    Score a SearchResult against a search query.

    Scoring factors:
    - exact phrase match in title (big boost)
    - word frequency in title (double weight)
    - word frequency in description
    - length penalty for very long descriptions
    - static rank from model (if used)
    """
    if not query:
        return 0.0

    query = query.lower().strip()
    query_tokens = tokenize(query)

    title = result.title or ''
    description = result.description or ''
    title_tokens = tokenize(title)
    desc_tokens = tokenize(description)

    # 1. Exact phrase match in title (highest boost)
    exact_match_boost = 3.0 if query in title.lower() else 0.0

    # 2. Title TF score – twice as important
    title_score = sum(tf(word, title_tokens) for word in query_tokens) * 2.0

    # 3. Description TF score
    desc_score = sum(tf(word, desc_tokens) for word in query_tokens)

    # 4. Length penalty (longer descriptions get slightly lower scores)
    desc_length = len(desc_tokens) + 1
    length_penalty = 1.0 / log(desc_length + 1)

    # 5. Static boost from database field
    static_score = static_boost

    # Combine everything
    total = exact_match_boost + title_score + desc_score * length_penalty + static_score
    return total