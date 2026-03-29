from sklearn.feature_extraction.text import CountVectorizer

class SyscallFeatureExtractor:
    """
    Extracts N-gram frequency features from system call sequences.
    Treats the sequence of syscalls like a document of text.
    """
    def __init__(self, ngram_range=(1, 3), max_features=500):
        # We use N-grams (1 to 3 syscalls in sequence) to capture behavioral patterns
        self.vectorizer = CountVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            token_pattern=r"(?u)\b\w+\b" # capture standard word tokens
        )
        self.is_fitted = False

    def fit_transform(self, sequences):
        """Fit the vectorizer and transform sequences into feature vectors."""
        X = self.vectorizer.fit_transform(sequences)
        self.is_fitted = True
        return X.toarray()

    def transform(self, sequences):
        """Transform new sequences using the fitted vectorizer."""
        if not self.is_fitted:
            raise ValueError("Extractor must be fitted before transform can be called.")
        X = self.vectorizer.transform(sequences)
        return X.toarray()

    def get_feature_names(self):
        if not self.is_fitted:
            return []
        return self.vectorizer.get_feature_names_out()
