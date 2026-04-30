# AI Detection & Stylometry Research System

**Purpose:** Research system for analyzing statistical, stylometric, and probabilistic differences between human and AI-generated text.

**Ethical Scope:** Research, benchmarking, interpretability, detector robustness evaluation. NOT for plagiarism, academic misconduct, or guaranteed detector bypassing.

## Architecture

**Design Principles:**
- **Data contracts first:** Versioned interfaces enable parallel development
- **Library-first, decoupled:** Each module operates independently
- **Real detectors, no mocks:** Use free APIs (GPTZero, ZeroGPT) from day one
- **Visualization after data flows:** Build pipeline first, then UI

## Modules (Phase 1 Implementation)

1. **Data Ingestion** (`modules/data_ingestion/`)
   - HC3 dataset streaming (48k labeled human-ChatGPT pairs)
   - Interface: `DataSource` protocol

2. **Human Corpus Construction** (`modules/human_corpus/`)
   - Extract and organize human_answers from HC3
   - Interface: `CorpusBuilder` protocol

3. **AI Corpus Construction** (`modules/ai_corpus/`)
   - Extract chatgpt_answers with generation metadata
   - Interface: `CorpusBuilder` protocol

4. **Stylometric Feature Extraction** (`modules/stylometric_features/`)
   - Lexical: Type-token ratio, MTLD, vocabulary richness (NLTK)
   - Syntactic: POS tags, dependency trees, parse complexity (spaCy)
   - Interface: `FeatureExtractor` protocol

5. **Detector Integration** (`modules/detectors/`)
   - Free detector APIs: GPTZero, ZeroGPT
   - Open-source methods: perplexity-based detection
   - Interface: `Detector` protocol

6. **Rewrite Engine** (`modules/rewrite/`)
   - Rule-based transformations (no GPU required)
   - Surface: Remove repetition, vary openings
   - Structural: Vary sentence lengths, restructure clauses
   - Interface: `TextTransformer` protocol

7. **Visualization** (`modules/visualization/`)
   - Basic Plotly charts with real detector data
   - Before/after comparison displays
   - Interface: `Visualizer` protocol

## Research Findings Integration

**Detection Methods:**
- GLTR (probability ranking), DetectGPT (0.95 AUROC), Ghostbuster (99.0 F1)
- Vulnerable to adversarial paraphrasing (64-99% effectiveness reduction)

**Datasets:**
- HC3: 48k labeled samples across 6 domains (reddit_eli5, finance, medicine, open_qa, wiki_csai)
- FineWeb-Edu: 1.3T tokens (Llama-3 filtered) for quality human corpus

**Tooling:**
- Tier 1 (Lexical): NLTK + scikit-learn
- Tier 2 (Syntactic): spaCy
- Tier 3 (Semantic): transformers + sentence-transformers
- Tier 4 (Classification): XGBoost + SHAP

**Critical Limitations:**
- Detector false positive rates: 15-61% (ESL writers disproportionately affected)
- 25+ universities banned detectors (MIT, Yale, Stanford, Johns Hopkins)
- Detectors are probabilistic, NOT truth systems

**Adversarial Methods:**
- DIPPER paraphrasing reduces DetectGPT from 70.3% to 4.6%
- StealthRL achieves 97.6% attack success
- Neural paraphrase with embedding similarity >0.85 maintains semantic fidelity

## Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

```python
from modules.data_ingestion import HC3DataSource
from modules.detectors import GPTZeroDetector
from modules.stylometric_features import SpaCyFeatureExtractor

# Load data
data_source = HC3DataSource()
samples = data_source.load_samples(limit=100)

# Extract features
extractor = SpaCyFeatureExtractor()
features = extractor.extract(samples)

# Run detection
detector = GPTZeroDetector()
results = detector.detect(samples)

print(f"Detection results: {results}")
```

## Ethical Disclosures

1. **AI detectors are probabilistic, not truth systems**
   - False positive rates: 15-61%
   - Detectors frequently disagree on same text
   - No detector achieves 100% accuracy

2. **Systematic bias exists**
   - ESL writers: 61% false positive rate (Stanford study)
   - Neurodivergent students disproportionately flagged
   - Formal writing styles trigger higher detection

3. **Trivial bypass methods exist**
   - Simple paraphrasing defeats most detectors
   - Google Translate back-translation bypasses watermarks
   - Detection effectiveness drops 64-99% with adversarial methods

4. **Institutional abandonment**
   - 25+ major universities banned/restricted AI detectors
   - Johns Hopkins: "No products can effectively identify generative AI"
   - Detection ≠ proof of authorship

5. **Research purpose only**
   - This system is for understanding detection mechanisms
   - Not for plagiarism detection or academic misconduct prevention
   - Results should not be used punitively

## References

- GLTR: https://arxiv.org/abs/1906.04043
- DetectGPT: https://arxiv.org/abs/2301.11305
- Ghostbuster: https://arxiv.org/abs/2305.15047
- HC3 Dataset: https://huggingface.co/datasets/Hello-SimpleAI/HC3
- Stylometry Survey: https://aclanthology.org/2025.cl-1.8/

## License

Research use only. See ethical disclosures above.
