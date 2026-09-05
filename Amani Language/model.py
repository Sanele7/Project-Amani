"""
Amani Language — n-gram language model (build-out).

Still pure Python (no heavy deps), now with temperature-controlled generation
(low = safe/repetitive, high = adventurous), top-k next-word prediction, and
perplexity scoring. Works for any language; it only needs text.
"""
import random
import re
import math
from collections import defaultdict, Counter


def tokenize(text):
    # Words and sentence punctuation, lowercased; Unicode-aware for any script.
    return re.findall(r"\w+|[.!?]", text.lower(), flags=re.UNICODE)


class NGramModel:
    def __init__(self, n=2):
        self.n = max(2, n)
        self.counts = defaultdict(Counter)   # context tuple -> Counter(next words)
        self.vocab = set()
        self.trained = False

    def train(self, text):
        tokens = tokenize(text)
        if len(tokens) < self.n:
            raise ValueError("Corpus is too short — add more text.")
        self.vocab = set(tokens)
        seq = ["<s>"] * (self.n - 1) + tokens + ["</s>"]
        self.counts.clear()
        for i in range(len(seq) - self.n + 1):
            context = tuple(seq[i:i + self.n - 1])
            self.counts[context][seq[i + self.n - 1]] += 1
        self.trained = True
        return {"tokens": len(tokens), "vocab": len(self.vocab), "contexts": len(self.counts)}

    def _dist(self, context):
        counter = self.counts.get(context)
        if not counter:
            return None
        total = sum(counter.values())
        return [(w, c / total) for w, c in counter.most_common()]

    def predict(self, prompt, k=6):
        tokens = tokenize(prompt)
        context = tuple((["<s>"] * (self.n - 1) + tokens)[-(self.n - 1):])
        dist = self._dist(context)
        return dist[:k] if dist else []

    def generate(self, max_words=40, seed=None, temperature=1.0):
        """temperature: <1 sharpens toward likely words, >1 flattens toward variety."""
        temp = max(0.1, float(temperature))
        if seed:
            tokens = tokenize(seed)
            context = tuple((["<s>"] * (self.n - 1) + tokens)[-(self.n - 1):])
            out = list(tokens)
        else:
            context = tuple(["<s>"] * (self.n - 1))
            out = []
        for _ in range(max_words):
            dist = self._dist(context)
            if not dist:
                break
            words = [w for w, _ in dist]
            weights = [p ** (1.0 / temp) for _, p in dist]  # temperature scaling
            nxt = random.choices(words, weights=weights, k=1)[0]
            if nxt == "</s>":
                break
            out.append(nxt)
            context = tuple((list(context) + [nxt])[-(self.n - 1):])
        return re.sub(r"\s+([.!?])", r"\1", " ".join(out))

    def perplexity(self, text):
        """Lower is better. Add-one smoothing so unseen words don't break it."""
        tokens = tokenize(text)
        if not tokens:
            return None
        seq = ["<s>"] * (self.n - 1) + tokens + ["</s>"]
        V = len(self.vocab) + 1
        log_sum, count = 0.0, 0
        for i in range(len(seq) - self.n + 1):
            context = tuple(seq[i:i + self.n - 1])
            nxt = seq[i + self.n - 1]
            counter = self.counts.get(context, Counter())
            prob = (counter.get(nxt, 0) + 1) / (sum(counter.values()) + V)
            log_sum += math.log(prob)
            count += 1
        return round(math.exp(-log_sum / count), 2) if count else None
