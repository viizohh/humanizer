#!/usr/bin/env python3
"""
AI Detection & Stylometry Research System - Demonstration

Shows the complete pipeline:
1. Load data from HC3
2. Extract stylometric features
3. Apply rewrite transformations
4. Compare before/after features

Note: Detector integration requires API keys (not included in Phase 1)
This demo shows the working pipeline with everything except live detector APIs.
"""

import sys
from modules.data_ingestion import HC3DataSource
from modules.stylometric_features import SpaCyFeatureExtractor
from modules.rewrite import RuleBasedRewriter


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def print_features(features, title="Features"):
    """Print feature vector in readable format"""
    print(f"\n{title}:")
    print(f"  Sample ID: {features.sample_id}")

    print("\n  Lexical Features:")
    for key, value in features.lexical_features.items():
        print(f"    {key}: {value:.4f}")

    print("\n  Syntactic Features (top 5):")
    syntactic_items = list(features.syntactic_features.items())[:5]
    for key, value in syntactic_items:
        print(f"    {key}: {value:.4f}")

    print("\n  Structural Features:")
    for key, value in features.structural_features.items():
        print(f"    {key}: {value:.4f}")


def main():
    print_section("AI Detection & Stylometry Research System - Demo")

    # ========================================================================
    # Step 1: Load Data
    # ========================================================================
    print_section("Step 1: Loading HC3 Dataset")
    data_source = HC3DataSource(streaming=True)

    metadata = data_source.get_metadata()
    print("Dataset Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    print("\nLoading 3 human samples and 3 AI samples...")
    human_samples = data_source.load_samples(limit=3, source_filter='human')
    ai_samples = data_source.load_samples(limit=3, source_filter='chatgpt')

    print(f"\nLoaded {len(human_samples)} human samples and {len(ai_samples)} AI samples")

    # Show sample data
    print("\n[Example Human Sample]")
    print(f"ID: {human_samples[0].sample_id}")
    print(f"Domain: {human_samples[0].metadata['domain']}")
    print(f"Text (first 200 chars):\n{human_samples[0].text[:200]}...")

    print("\n[Example AI Sample]")
    print(f"ID: {ai_samples[0].sample_id}")
    print(f"Domain: {ai_samples[0].metadata['domain']}")
    print(f"Text (first 200 chars):\n{ai_samples[0].text[:200]}...")

    # ========================================================================
    # Step 2: Extract Stylometric Features
    # ========================================================================
    print_section("Step 2: Extracting Stylometric Features")
    extractor = SpaCyFeatureExtractor()

    print("Extracting features from human sample...")
    human_features = extractor.extract_single(
        human_samples[0].text,
        human_samples[0].sample_id
    )
    print_features(human_features, "Human Sample Features")

    print("\nExtracting features from AI sample...")
    ai_features = extractor.extract_single(
        ai_samples[0].text,
        ai_samples[0].sample_id
    )
    print_features(ai_features, "AI Sample Features")

    # ========================================================================
    # Step 3: Compare Key Metrics
    # ========================================================================
    print_section("Step 3: Comparing Human vs AI Metrics")

    print("Key Stylometric Differences:")
    print(f"\nType-Token Ratio (vocabulary diversity):")
    print(f"  Human: {human_features.lexical_features.get('type_token_ratio', 0):.4f}")
    print(f"  AI:    {ai_features.lexical_features.get('type_token_ratio', 0):.4f}")
    print(f"  → Higher TTR typically indicates more diverse vocabulary")

    print(f"\nSentence Length Variance (burstiness):")
    human_variance = human_features.structural_features.get('sentence_length_variance', 0)
    ai_variance = ai_features.structural_features.get('sentence_length_variance', 0)
    print(f"  Human: {human_variance:.4f}")
    print(f"  AI:    {ai_variance:.4f}")
    print(f"  → Higher variance indicates more varied sentence structure")

    print(f"\nBurstiness Score:")
    human_burst = human_features.structural_features.get('burstiness', 0)
    ai_burst = ai_features.structural_features.get('burstiness', 0)
    print(f"  Human: {human_burst:.4f}")
    print(f"  AI:    {ai_burst:.4f}")
    print(f"  → Research shows AI typically has lower burstiness")

    # ========================================================================
    # Step 4: Apply Rewrite Transformations
    # ========================================================================
    print_section("Step 4: Testing Rewrite Transformations")

    rewriter = RuleBasedRewriter()

    print("Original AI Text:")
    print(f"{ai_samples[0].text[:300]}...")

    print("\n--- Applying Surface-Level Transformation ---")
    surface_result = rewriter.transform(ai_samples[0].text, 'surface')
    print(f"\nTransformed Text:")
    print(f"{surface_result.transformed_text[:300]}...")
    print(f"\nSemantic Similarity: {surface_result.semantic_similarity:.4f}")

    print("\n--- Applying Structural Transformation ---")
    structural_result = rewriter.transform(ai_samples[0].text, 'structural')
    print(f"\nTransformed Text:")
    print(f"{structural_result.transformed_text[:300]}...")
    print(f"\nSemantic Similarity: {structural_result.semantic_similarity:.4f}")

    # ========================================================================
    # Step 5: Feature Comparison Before/After Rewrite
    # ========================================================================
    print_section("Step 5: Features Before/After Rewrite")

    print("Extracting features from transformed text...")
    transformed_features = extractor.extract_single(
        surface_result.transformed_text,
        ai_samples[0].sample_id + "_transformed"
    )

    print(f"\nBurstiness Comparison (AI Sample):")
    original_burst = ai_features.structural_features.get('burstiness', 0)
    transformed_burst = transformed_features.structural_features.get('burstiness', 0)
    print(f"  Original:    {original_burst:.4f}")
    print(f"  Transformed: {transformed_burst:.4f}")
    print(f"  Change:      {transformed_burst - original_burst:+.4f}")

    # ========================================================================
    # Summary & Next Steps
    # ========================================================================
    print_section("Summary & Next Steps")

    print("✓ Successfully demonstrated:")
    print("  1. HC3 dataset loading with streaming support")
    print("  2. Stylometric feature extraction (lexical, syntactic, structural)")
    print("  3. Rule-based text transformations")
    print("  4. Before/after feature comparison")

    print("\n⚠ Missing components (require API keys/budget):")
    print("  - Live detector integration (GPTZero, Copyleaks, etc.)")
    print("  - Detector score comparison before/after rewrite")
    print("  - Interactive visualization dashboards")

    print("\n→ To integrate detectors:")
    print("  1. Obtain API keys for GPTZero, Copyleaks, or Originality.ai")
    print("  2. Implement detector modules following the Detector protocol")
    print("  3. Run comparative benchmarking across detectors")

    print("\n→ For research use:")
    print("  - See README.md for ethical disclosures")
    print("  - Detectors have 15-61% false positive rates")
    print("  - Results are probabilistic, not definitive")
    print("  - 25+ universities have banned AI detectors")

    print("\n" + "="*70)
    print(" Demo complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        print("\nNote: Ensure you have installed dependencies:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
        sys.exit(1)
