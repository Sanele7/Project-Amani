"""
A pure-Python n-gram language model — the real statistical foundation that
every language model builds on, trainable instantly on a small corpus.

Works for any language: it only needs text. Handles generation, next-word
prediction, and perplexity (a genuine measure of how well it fits the language).
"""
import random
import re
import math
from collections import defaultdict, Counter


def tokenize(text):
    # Words and sentence punctuation; lowercased. Unicode-aware so it works
    # for non-Latin scripts too.
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
        pad = ["<s>"] * (self.n - 1)
        seq = pad + tokens + ["</s>"]
        for i in range(len(seq) - self.n + 1):
            context = tuple(seq[i:i + self.n - 1])
            nxt = seq[i + self.n - 1]
            self.counts[context][nxt] += 1
        self.trained = True
        return {"tokens": len(tokens), "vocab": len(self.vocab), "contexts": len(self.counts)}

    def _next_distribution(self, context):
        counter = self.counts.get(context)
        if not counter:
            return None
        total = sum(counter.values())
        return [(w, c / total) for w, c in counter.most_common()]

    def predict(self, prompt, k=5):
        tokens = tokenize(prompt)
        context = tuple((["<s>"] * (self.n - 1) + tokens)[-(self.n - 1):])
        dist = self._next_distribution(context)
        if not dist:
            return []
        return dist[:k]

    def generate(self, max_words=40, seed=None):
        if seed:
            tokens = tokenize(seed)
            context = tuple((["<s>"] * (self.n - 1) + tokens)[-(self.n - 1):])
            out = list(tokens)
        else:
            context = tuple(["<s>"] * (self.n - 1))
            out = []
        for _ in range(max_words):
            dist = self._next_distribution(context)
            if not dist:
                break
            words, probs = zip(*dist)
            nxt = random.choices(words, weights=probs, k=1)[0]
            if nxt == "</s>":
                break
            out.append(nxt)
            context = tuple((list(context) + [nxt])[-(self.n - 1):])
        text = " ".join(out)
        # tidy spacing before punctuation
        return re.sub(r"\s+([.!?])", r"\1", text)

    def perplexity(self, text):
        """Lower is better. Uses add-one smoothing so unseen words don't break it."""
        tokens = tokenize(text)
        if not tokens:
            return None
        pad = ["<s>"] * (self.n - 1)
        seq = pad + tokens + ["</s>"]
        V = len(self.vocab) + 1
        log_sum = 0.0
        count = 0
        for i in range(len(seq) - self.n + 1):
            context = tuple(seq[i:i + self.n - 1])
            nxt = seq[i + self.n - 1]
            counter = self.counts.get(context, Counter())
            prob = (counter.get(nxt, 0) + 1) / (sum(counter.values()) + V)
            log_sum += math.log(prob)
            count += 1
        return round(math.exp(-log_sum / count), 2) if count else None
