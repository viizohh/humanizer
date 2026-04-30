#!/usr/bin/env python3
"""
AI Text Humanizer - Minimal Interface
"""

import streamlit as st
import sys
from modules.data_ingestion import HC3DataSource
from modules.stylometric_features import SpaCyFeatureExtractor
from modules.rewrite import RuleBasedRewriter

# Page config
st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="⬜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal white design
st.markdown("""
<style>
    /* Hide Streamlit branding and unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Base styles */
    .stApp {
        background-color: #ffffff;
        max-width: 900px;
        margin: 0 auto;
        padding: 60px 80px;
    }

    /* Typography */
    body, .stMarkdown, p, div, span, label {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: #000000 !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        letter-spacing: 0.3px;
    }

    h1, h2, h3 {
        font-weight: 400 !important;
        letter-spacing: 0.5px;
    }

    h1 {
        font-size: 24px !important;
        margin-bottom: 40px !important;
    }

    h2 {
        font-size: 18px !important;
        margin-bottom: 30px !important;
    }

    /* Navigation */
    .nav-container {
        margin-bottom: 80px;
        display: flex;
        gap: 30px;
        font-size: 14px;
        letter-spacing: 0.5px;
    }

    .nav-link {
        color: #000000;
        text-decoration: none;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .nav-link:hover {
        opacity: 0.6;
    }

    /* Text areas */
    .stTextArea textarea {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        border-radius: 0 !important;
        color: #000000 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-size: 16px !important;
        padding: 15px !important;
    }

    .stTextArea textarea:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }

    /* Buttons */
    .stButton button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 10px 30px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
        transition: opacity 0.2s !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }

    .stButton button p {
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .stButton button:hover {
        opacity: 0.8 !important;
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Navigation buttons - special styling */
    [data-testid="column"] .stButton button {
        background-color: transparent !important;
        color: #000000 !important;
        border: none !important;
        padding: 0 !important;
        font-size: 14px !important;
        text-decoration: underline !important;
    }

    [data-testid="column"] .stButton button:hover {
        opacity: 0.6 !important;
        background-color: transparent !important;
    }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        border-radius: 0 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border: none !important;
        border-bottom: 1px solid #000000 !important;
        border-radius: 0 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
    }

    /* Metrics */
    .stMetric {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        padding: 15px !important;
        border-radius: 0 !important;
    }

    .stMetric label {
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #666666 !important;
    }

    .stMetric div {
        font-size: 18px !important;
        color: #000000 !important;
    }

    /* Links */
    a {
        color: #000000 !important;
        text-decoration: underline !important;
        transition: opacity 0.2s !important;
    }

    a:hover {
        opacity: 0.6 !important;
    }

    /* Remove padding from columns */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Hide sidebar */
    section[data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components (with caching)
@st.cache_resource
def load_components():
    """Load feature extractor and rewriter (cached)"""
    try:
        extractor = SpaCyFeatureExtractor()
        rewriter = RuleBasedRewriter()
        return extractor, rewriter
    except Exception as e:
        st.error(f"Error loading components: {e}")
        st.info("Run: pip install -r requirements.txt && python -m spacy download en_core_web_sm")
        return None, None

# Session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Navigation
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 8])

with nav_col1:
    if st.button("home", key="nav_home", use_container_width=True):
        st.session_state.page = 'home'

with nav_col2:
    if st.button("about", key="nav_about", use_container_width=True):
        st.session_state.page = 'about'

with nav_col3:
    if st.button("research", key="nav_research", use_container_width=True):
        st.session_state.page = 'research'

st.markdown("<br>", unsafe_allow_html=True)

# HOME PAGE
if st.session_state.page == 'home':
    st.markdown("## AI Text Humanizer")

    # Load components
    extractor, rewriter = load_components()

    if extractor is None or rewriter is None:
        st.stop()

    # Input
    # Sample text button
    if st.button("Load Sample Text", help="Load AI-generated sample text to test transformations"):
        st.session_state.sample_text = """It is important to note that artificial intelligence has fundamentally transformed numerous aspects of modern society. Furthermore, these technological advancements have facilitated unprecedented opportunities for innovation across various sectors. Additionally, it should be noted that machine learning algorithms utilize vast datasets to identify patterns and make predictions with remarkable accuracy.

Moreover, the implementation of AI systems requires careful consideration of several key factors. For instance, organizations must obtain sufficient computational resources and ensure that their infrastructure can facilitate the processing of large amounts of data. It is worth mentioning that the deployment of these technologies necessitates substantial investments in both hardware and personnel training.

Nevertheless, despite these challenges, the potential benefits are quite significant. Organizations that successfully implement AI solutions can demonstrate improved efficiency and enhanced decision-making capabilities. However, it is essential to acknowledge that there are also very important ethical considerations that must be addressed. For example, concerns regarding privacy, bias, and transparency require thorough investigation and ongoing monitoring.

In order to maximize the effectiveness of AI implementations, stakeholders should establish comprehensive frameworks for governance and oversight. Additionally, it is crucial to recognize that continuous evaluation and refinement of these systems is necessary to maintain optimal performance. Therefore, organizations must remain committed to adapting their approaches as the technology continues to evolve and as new challenges emerge in this rapidly changing landscape."""

    input_text = st.text_area(
        "Paste text here",
        value=st.session_state.get('sample_text', ''),
        height=300,
        placeholder="Enter AI-generated text to transform...",
        label_visibility="collapsed"
    )

    # Settings in expander
    with st.expander("settings"):
        transformation_level = st.selectbox(
            "Transformation Type",
            ["surface", "structural"],
            help="Surface: Remove AI patterns. Structural: Vary sentence structure."
        )

        intensity = st.select_slider(
            "Transformation Intensity",
            options=["minimal", "light", "medium", "heavy", "aggressive"],
            value="medium",
            help="How aggressively to transform the text. Higher = more changes but potentially less natural."
        )

        show_analysis = st.checkbox("Show detailed analysis", value=False)

    # Transform button
    if st.button("Transform Text"):
        if not input_text or len(input_text.strip()) < 20:
            st.error("Please enter at least 20 characters of text.")
        else:
            with st.spinner("Processing..."):
                try:
                    # Transform
                    result = rewriter.transform(input_text, transformation_level, intensity)

                    # Output
                    st.markdown("### Transformed Text")
                    st.text_area(
                        "Output",
                        value=result.transformed_text,
                        height=300,
                        label_visibility="collapsed"
                    )

                    # Metrics in columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Semantic Similarity",
                            f"{result.semantic_similarity:.1%}",
                            help="How similar the transformed text is to the original (word overlap)"
                        )

                    with col2:
                        change_amount = 1 - result.semantic_similarity
                        st.metric(
                            "Change Amount",
                            f"{change_amount:.1%}",
                            help="How much the text was changed"
                        )

                    with col3:
                        orig_words = len(input_text.split())
                        trans_words = len(result.transformed_text.split())
                        word_diff = trans_words - orig_words
                        st.metric(
                            "Word Count",
                            f"{trans_words}",
                            delta=f"{word_diff:+d}" if word_diff != 0 else "0",
                            help="Number of words in transformed text"
                        )

                    # Analysis
                    if show_analysis:
                        st.markdown("---")
                        st.markdown("### Analysis")

                        # Extract features
                        original_features = extractor.extract_single(input_text, "original")
                        transformed_features = extractor.extract_single(
                            result.transformed_text,
                            "transformed"
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**Original**")
                            st.metric(
                                "Type-Token Ratio",
                                f"{original_features.lexical_features.get('type_token_ratio', 0):.3f}"
                            )
                            st.metric(
                                "Burstiness",
                                f"{original_features.structural_features.get('burstiness', 0):.3f}"
                            )

                        with col2:
                            st.markdown("**Transformed**")
                            trans_ttr = transformed_features.lexical_features.get('type_token_ratio', 0)
                            orig_ttr = original_features.lexical_features.get('type_token_ratio', 0)
                            st.metric(
                                "Type-Token Ratio",
                                f"{trans_ttr:.3f}",
                                delta=f"{trans_ttr - orig_ttr:+.3f}"
                            )

                            trans_burst = transformed_features.structural_features.get('burstiness', 0)
                            orig_burst = original_features.structural_features.get('burstiness', 0)
                            st.metric(
                                "Burstiness",
                                f"{trans_burst:.3f}",
                                delta=f"{trans_burst - orig_burst:+.3f}"
                            )

                except Exception as e:
                    st.error(f"Error processing text: {e}")

# ABOUT PAGE
elif st.session_state.page == 'about':
    st.markdown("## About")

    st.markdown("""
    ### What makes this different

    This is a research system for analyzing stylometric and statistical differences between human-written and AI-generated text.
    Unlike commercial "humanizers", this system is:

    **Research-based**
    Built on peer-reviewed papers (GLTR, DetectGPT, Ghostbuster) analyzing linguistic patterns, probability distributions, and structural features.

    **Transparent about limitations**
    AI detectors have 15-61% false positive rates and systematically bias against ESL writers. 25+ universities have banned them.

    **Not a detector bypass tool**
    This exists to illuminate how detection mechanisms work and their fundamental limitations, not to circumvent academic integrity systems.

    **Open about what it does**
    Surface transformations remove AI-typical patterns (filler phrases, overly formal transitions). Structural transformations vary sentence length to increase burstiness.

    ### What it doesn't do

    This is **not** for plagiarism, academic misconduct, or guaranteed detector bypassing. AI detectors are probabilistic tools, not truth systems.
    Detection results are confidence scores based on training data, not proof of authorship.

    ### Research foundation

    - Type-token ratio and lexical diversity analysis
    - Burstiness and sentence structure variation
    - Rule-based transformations (no neural models required)
    - Real labeled data (HC3 dataset: 48k human-ChatGPT samples)
    - Stylometric feature extraction using spaCy and NLTK

    See the research page for papers and ethical disclosures.
    """)

# RESEARCH PAGE
elif st.session_state.page == 'research':
    st.markdown("## Research")

    st.markdown("""
    ### Key Papers

    **Detection Methods**
    - [GLTR: Statistical Detection and Visualization of Generated Text](https://arxiv.org/abs/1906.04043)
    - [DetectGPT: Zero-Shot Machine-Generated Text Detection](https://arxiv.org/abs/2301.11305)
    - [Ghostbuster: Detecting Text Ghostwritten by Large Language Models](https://arxiv.org/abs/2305.15047)

    **Stylometric Analysis**
    - [Stylometry in the Age of LLMs (ACL 2025)](https://aclanthology.org/2025.cl-1.8/)

    **Adversarial Methods**
    - [DIPPER: Paraphrasing to Evade Detectors](https://arxiv.org/abs/2303.13408)
    - [StealthRL: Reinforcement Learning for Detector Evasion](https://arxiv.org/abs/2602.08934)

    ### Neural Paraphrasing Methods

    **DIPPER (Discourse Paraphraser)**

    DIPPER is an 11B parameter (11 billion learned weights) neural paraphrasing model built by fine-tuning T5-XXL. Published at NeurIPS 2023, it demonstrates how neural approaches can bypass AI detection.

    Key features:
    - Context-aware paragraph-level paraphrasing
    - Controllable lexical diversity (word variation) and content reordering
    - Trained on PAR3 dataset (parallel English translations used as paraphrase pairs)
    - Reduces DetectGPT detector accuracy from 70.3% to 4.6% (at 1% false positive rate)

    **T5 and PEGASUS Alternatives**

    Other transformer-based models for paraphrasing:
    - T5 (Text-to-Text Transfer Transformer) variants
    - PEGASUS (abstractive summarization model adapted for paraphrasing)
    - BART (bidirectional and auto-regressive transformers)

    Available on HuggingFace:
    - `kalpeshk2011/dipper-paraphraser-xxl`
    - `tuner007/pegasus_paraphrase`
    - Various T5 fine-tuned models

    **Implementation Process**

    Basic usage workflow:

    ```python
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

    # Load model (one-time download, ~20GB)
    tokenizer = AutoTokenizer.from_pretrained("kalpeshk2011/dipper-paraphraser-xxl")
    model = AutoModelForSeq2SeqLM.from_pretrained("kalpeshk2011/dipper-paraphraser-xxl")

    # Paraphrase text
    input_text = "Your paragraph here..."
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=512, num_beams=5)
    paraphrased = tokenizer.decode(outputs[0], skip_special_tokens=True)
    ```

    Process steps:
    1. Input preparation - chunk long texts into 512-token segments
    2. Model inference - GPU processes each chunk through neural network
    3. Output assembly - combine paraphrased chunks with context preservation
    4. Quality validation - verify semantic similarity preserved

    **Technical Requirements**

    Dependencies:
    ```
    pip install transformers torch sentencepiece
    ```

    Hardware:
    - CUDA-compatible GPU with 16GB+ VRAM (for 11B parameter models)
    - Quantized 8-bit models can run on 8GB VRAM with quality tradeoff
    - CPU inference possible but 50-100x slower
    - Cloud GPU instances (A100, V100) recommended for production

    Limitations:
    - Most models limited to 512-1024 tokens per pass
    - Longer documents require chunking strategies
    - First inference includes 20GB model download

    **Why This System Uses Rule-Based Approach**

    This system deliberately uses rule-based transformations instead of neural paraphrasing:

    Transparency:
    - Every transformation is explainable and auditable
    - No black-box neural models obscuring changes
    - Users see exactly what patterns are being modified

    Accessibility:
    - No GPU required - runs on any laptop
    - No 20GB model downloads
    - Instant transformation without inference time

    Research Focus:
    - Demonstrates detection mechanisms through transparent methods
    - Educational tool, not detection bypass system
    - Ethical alignment with research transparency

    Trade-offs:
    - Rule-based: Lower bypass effectiveness, full transparency, zero infrastructure
    - Neural: Higher bypass effectiveness, black-box operation, significant GPU requirements

    **Ethical Considerations**

    Neural paraphrasing has both legitimate and problematic uses:

    Legitimate applications:
    - Accessibility tools for non-native English speakers
    - Translation refinement and multilingual communication
    - Creative writing assistance and ideation
    - Simplifying complex technical content

    Ethical concerns:
    - Frequently misused to bypass academic integrity systems
    - Enables plagiarism at scale
    - Defeats detector tools without addressing underlying dishonesty
    - Creates arms race between detection and evasion
    - Obscures human vs AI authorship boundaries

    This system exists to understand detection mechanisms and their limitations through transparent methods, not to facilitate academic misconduct.

    ### Critical Limitations

    **False Positive Rates**
    - 15-45% general population
    - 61% for ESL (non-native English) writers
    - Systematic bias against formal writing styles

    **Institutional Response**
    - 25+ universities banned AI detectors
    - MIT, Yale, Stanford, Johns Hopkins official statements
    - Cited: unreliability, procedural fairness, systematic bias

    **Bypass Trivially**
    - DIPPER reduces DetectGPT accuracy from 70.3% to 4.6%
    - Simple paraphrasing defeats most detection
    - Watermarking defeated by back-translation

    ### Ethical Disclosures

    Full disclosures available in:
    - [ETHICAL_DISCLOSURES.md](ETHICAL_DISCLOSURES.md)
    - [README.md](README.md)

    **Required context for any use:**
    - Detectors are probabilistic, not truth systems
    - Results are confidence scores, not proof
    - High false positive rates (15-61%)
    - Systematic bias against marginalized groups
    - Trivially bypassable with simple methods
    - 25+ universities have banned detectors
    """)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
<div style="font-size: 12px; color: #666666; letter-spacing: 0.5px;">
Research system for understanding AI detection mechanisms. Not for plagiarism or academic misconduct.
<a href="README.md" style="color: #666666;">README</a> ·
<a href="ETHICAL_DISCLOSURES.md" style="color: #666666;">Ethical Disclosures</a> ·
<a href="demo.py" style="color: #666666;">CLI Demo</a>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
