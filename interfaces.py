"""
Data Contracts for AI Detection Research System

Versioned interfaces following the Council's architectural principles:
- Data contracts first (Serena)
- Real detectors, no mocks (Ava)
- Library-first, decoupled (Marcus)

Version: 1.0.0
"""

from typing import Protocol, List, Dict, Any, Iterator, Optional
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TextSample:
    """Atomic unit of text with metadata"""
    text: str
    source: str  # 'human' or 'ai'
    metadata: Dict[str, Any]
    sample_id: Optional[str] = None


@dataclass
class FeatureVector:
    """Stylometric features extracted from text"""
    sample_id: str
    lexical_features: Dict[str, float]  # TTR, MTLD, vocab_richness, etc.
    syntactic_features: Dict[str, float]  # POS distributions, parse depth, etc.
    structural_features: Dict[str, float]  # Sentence variance, burstiness, etc.
    metadata: Dict[str, Any]


@dataclass
class DetectionResult:
    """Detection output from any detector"""
    sample_id: str
    detector_name: str
    ai_probability: float  # 0.0 to 1.0
    confidence: str  # 'low', 'medium', 'high'
    sentence_level_scores: Optional[List[float]] = None
    metadata: Dict[str, Any] = None


@dataclass
class TransformationResult:
    """Result of text transformation"""
    original_text: str
    transformed_text: str
    transformation_type: str  # 'surface', 'structural', 'semantic', etc.
    semantic_similarity: float  # 0.0 to 1.0
    metadata: Dict[str, Any]


# ============================================================================
# Module Interfaces (Protocols)
# ============================================================================

class DataSource(Protocol):
    """
    Interface for data ingestion modules.

    Implementations: HC3DataSource, FineWebDataSource, LocalFileDataSource
    """

    def load_samples(
        self,
        limit: Optional[int] = None,
        source_filter: Optional[str] = None,
        domain_filter: Optional[str] = None
    ) -> List[TextSample]:
        """Load text samples with optional filtering"""
        ...

    def stream_samples(
        self,
        source_filter: Optional[str] = None,
        domain_filter: Optional[str] = None
    ) -> Iterator[TextSample]:
        """Stream samples without loading everything into memory"""
        ...

    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata (size, domains, sources, etc.)"""
        ...


class CorpusBuilder(Protocol):
    """
    Interface for corpus construction modules.

    Implementations: HumanCorpusBuilder, AICorpusBuilder
    """

    def build_corpus(
        self,
        data_source: DataSource,
        output_dir: str,
        max_samples: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build corpus from data source.

        Returns metadata about constructed corpus.
        """
        ...

    def get_statistics(self) -> Dict[str, Any]:
        """Get corpus statistics (sample count, domains, etc.)"""
        ...


class FeatureExtractor(Protocol):
    """
    Interface for stylometric feature extraction.

    Implementations: SpaCyFeatureExtractor, NLTKFeatureExtractor
    """

    def extract(self, samples: List[TextSample]) -> List[FeatureVector]:
        """Extract features from text samples"""
        ...

    def extract_single(self, text: str) -> FeatureVector:
        """Extract features from single text"""
        ...

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names this extractor produces"""
        ...


class Detector(Protocol):
    """
    Interface for AI text detectors.

    Implementations: GPTZeroDetector, ZeroGPTDetector, PerplexityDetector
    """

    def detect(self, samples: List[TextSample]) -> List[DetectionResult]:
        """Run detection on multiple samples"""
        ...

    def detect_single(self, text: str) -> DetectionResult:
        """Run detection on single text"""
        ...

    def get_detector_info(self) -> Dict[str, Any]:
        """Get detector metadata (name, version, API endpoint, etc.)"""
        ...


class TextTransformer(Protocol):
    """
    Interface for text transformation/rewrite modules.

    Implementations: SurfaceRewriter, StructuralRewriter, SemanticRewriter
    """

    def transform(
        self,
        text: str,
        transformation_level: str = 'surface'
    ) -> TransformationResult:
        """
        Transform text at specified level.

        Levels: 'surface', 'structural', 'semantic', 'discourse'
        """
        ...

    def batch_transform(
        self,
        samples: List[TextSample],
        transformation_level: str = 'surface'
    ) -> List[TransformationResult]:
        """Transform multiple samples"""
        ...


class Visualizer(Protocol):
    """
    Interface for visualization modules.

    Implementations: PlotlyVisualizer, DashboardGenerator
    """

    def plot_detection_scores(
        self,
        results: List[DetectionResult],
        output_path: Optional[str] = None
    ) -> Any:
        """
        Create visualization of detection scores.

        Returns plotly figure or saves to file if output_path provided.
        """
        ...

    def plot_feature_distributions(
        self,
        features: List[FeatureVector],
        feature_names: List[str],
        output_path: Optional[str] = None
    ) -> Any:
        """Plot feature distributions comparing human vs AI"""
        ...

    def plot_transformation_effectiveness(
        self,
        before_results: List[DetectionResult],
        after_results: List[DetectionResult],
        output_path: Optional[str] = None
    ) -> Any:
        """Plot before/after transformation detection scores"""
        ...


# ============================================================================
# Classifier Interfaces (Future modules)
# ============================================================================

class Classifier(Protocol):
    """
    Interface for binary classifiers (human vs AI).

    Implementations: XGBoostClassifier, LogisticClassifier
    """

    def train(
        self,
        features: List[FeatureVector],
        labels: List[str]
    ) -> None:
        """Train classifier on features and labels"""
        ...

    def predict(self, features: List[FeatureVector]) -> List[str]:
        """Predict labels for features"""
        ...

    def predict_proba(self, features: List[FeatureVector]) -> List[float]:
        """Predict probabilities"""
        ...

    def explain(self, feature_vector: FeatureVector) -> Dict[str, float]:
        """Get feature importance/SHAP values for prediction"""
        ...


# ============================================================================
# Version Info
# ============================================================================

INTERFACE_VERSION = "1.0.0"

def get_version() -> str:
    """Get interface version"""
    return INTERFACE_VERSION
