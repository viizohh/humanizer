"""
Stylometric Feature Extractor

Implements FeatureExtractor protocol using spaCy + NLTK
Extracts lexical, syntactic, and structural features per research findings
"""

from typing import List, Dict, Any
from interfaces import TextSample, FeatureVector
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class SpaCyFeatureExtractor:
    """Extract stylometric features using spaCy + NLTK"""

    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize with spaCy model"""
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            print(f"Downloading {model_name}...")
            import os
            os.system(f"python -m spacy download {model_name}")
            self.nlp = spacy.load(model_name)

    def extract(self, samples: List[TextSample]) -> List[FeatureVector]:
        """Extract features from multiple samples"""
        return [self.extract_single(s.text, s.sample_id) for s in samples]

    def extract_single(self, text: str, sample_id: str = "unknown") -> FeatureVector:
        """Extract features from single text"""
        doc = self.nlp(text)

        # Lexical features
        lexical = self._extract_lexical(text, doc)

        # Syntactic features
        syntactic = self._extract_syntactic(doc)

        # Structural features
        structural = self._extract_structural(text, doc)

        return FeatureVector(
            sample_id=sample_id,
            lexical_features=lexical,
            syntactic_features=syntactic,
            structural_features=structural,
            metadata={'feature_version': '1.0'}
        )

    def _extract_lexical(self, text: str, doc) -> Dict[str, float]:
        """Lexical diversity metrics"""
        words = [token.text for token in doc if token.is_alpha]
        if not words:
            return {}

        unique_words = set(words)
        ttr = len(unique_words) / len(words) if words else 0

        return {
            'type_token_ratio': ttr,
            'vocabulary_size': len(unique_words),
            'word_count': len(words),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0
        }

    def _extract_syntactic(self, doc) -> Dict[str, float]:
        """Syntactic patterns (POS tags, dependencies)"""
        pos_counts = {}
        for token in doc:
            pos_counts[token.pos_] = pos_counts.get(token.pos_, 0) + 1

        total_tokens = len(doc)
        pos_ratios = {f'pos_{k.lower()}_ratio': v/total_tokens
                      for k, v in pos_counts.items()} if total_tokens > 0 else {}

        # Dependency tree depth
        depths = [len(list(token.ancestors)) for token in doc]
        avg_depth = np.mean(depths) if depths else 0

        return {
            **pos_ratios,
            'avg_dependency_depth': avg_depth,
            'max_dependency_depth': max(depths) if depths else 0
        }

    def _extract_structural(self, text: str, doc) -> Dict[str, float]:
        """Structural features (sentence variance, burstiness)"""
        sentences = list(doc.sents)
        sent_lengths = [len(list(sent)) for sent in sentences]

        if not sent_lengths:
            return {}

        return {
            'sentence_count': len(sentences),
            'avg_sentence_length': np.mean(sent_lengths),
            'sentence_length_variance': np.var(sent_lengths),
            'sentence_length_std': np.std(sent_lengths),
            'burstiness': np.std(sent_lengths) / np.mean(sent_lengths) if np.mean(sent_lengths) > 0 else 0
        }

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        sample = self.extract_single("Sample text for feature names.")
        return (list(sample.lexical_features.keys()) +
                list(sample.syntactic_features.keys()) +
                list(sample.structural_features.keys()))
