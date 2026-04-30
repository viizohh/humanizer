"""
HC3 Dataset Loader

Implements DataSource protocol for HC3 (Human ChatGPT Comparison Corpus)
- 48,644 labeled human vs ChatGPT samples
- Domains: reddit_eli5, finance, medicine, open_qa, wiki_csai
- Streaming support to avoid memory issues

Reference: https://huggingface.co/datasets/Hello-SimpleAI/HC3
"""

from typing import List, Dict, Any, Iterator, Optional
from datasets import load_dataset
from interfaces import DataSource, TextSample
import uuid


class HC3DataSource:
    """
    HC3 dataset loader with streaming support.

    Follows Ava's principle: "Use real data from day one, no mocking"
    """

    def __init__(self, streaming: bool = True):
        """
        Initialize HC3 data source.

        Args:
            streaming: If True, use dataset streaming to avoid large downloads
        """
        self.streaming = streaming
        self._dataset = None
        self._metadata = None

    def load_samples(
        self,
        limit: Optional[int] = None,
        source_filter: Optional[str] = None,  # 'human' or 'chatgpt'
        domain_filter: Optional[str] = None  # e.g., 'reddit_eli5', 'finance'
    ) -> List[TextSample]:
        """
        Load HC3 samples into memory.

        Args:
            limit: Maximum number of samples to load
            source_filter: Filter by 'human' or 'chatgpt'
            domain_filter: Filter by domain (reddit_eli5, finance, etc.)

        Returns:
            List of TextSample objects
        """
        samples = []
        count = 0

        for sample in self.stream_samples(source_filter, domain_filter):
            samples.append(sample)
            count += 1
            if limit and count >= limit:
                break

        return samples

    def stream_samples(
        self,
        source_filter: Optional[str] = None,
        domain_filter: Optional[str] = None
    ) -> Iterator[TextSample]:
        """
        Stream HC3 samples without loading everything into memory.

        Yields:
            TextSample objects one at a time
        """
        # Load dataset with streaming
        dataset = load_dataset(
            "Hello-SimpleAI/HC3",
            split="all",
            streaming=self.streaming
        )

        for item in dataset:
            # HC3 structure: question, human_answers (list), chatgpt_answers (list), source
            question = item.get('question', '')
            source_domain = item.get('source', 'unknown')

            # Apply domain filter
            if domain_filter and source_domain != domain_filter:
                continue

            # Yield human answers
            if not source_filter or source_filter == 'human':
                human_answers = item.get('human_answers', [])
                for answer in human_answers:
                    if answer and answer.strip():  # Skip empty answers
                        yield TextSample(
                            text=f"Q: {question}\nA: {answer}",
                            source='human',
                            metadata={
                                'domain': source_domain,
                                'question': question,
                                'answer_only': answer,
                                'dataset': 'HC3'
                            },
                            sample_id=f"hc3_human_{str(uuid.uuid4())[:8]}"
                        )

            # Yield ChatGPT answers
            if not source_filter or source_filter == 'chatgpt':
                chatgpt_answers = item.get('chatgpt_answers', [])
                for answer in chatgpt_answers:
                    if answer and answer.strip():
                        yield TextSample(
                            text=f"Q: {question}\nA: {answer}",
                            source='ai',
                            metadata={
                                'domain': source_domain,
                                'question': question,
                                'answer_only': answer,
                                'model': 'ChatGPT',
                                'dataset': 'HC3'
                            },
                            sample_id=f"hc3_ai_{str(uuid.uuid4())[:8]}"
                        )

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get HC3 dataset metadata.

        Returns:
            Dictionary with dataset statistics
        """
        if self._metadata is None:
            # Calculate metadata by sampling
            domains = set()
            sample_count = 0

            for sample in self.stream_samples():
                domains.add(sample.metadata['domain'])
                sample_count += 1
                if sample_count >= 1000:  # Sample first 1000 for speed
                    break

            self._metadata = {
                'name': 'HC3',
                'full_name': 'Human ChatGPT Comparison Corpus',
                'total_samples': '48,644 (approx)',
                'domains': list(domains),
                'source_types': ['human', 'chatgpt'],
                'url': 'https://huggingface.co/datasets/Hello-SimpleAI/HC3',
                'streaming_enabled': self.streaming
            }

        return self._metadata

    def get_domain_statistics(self) -> Dict[str, int]:
        """
        Get sample counts per domain.

        Returns:
            Dictionary mapping domain to sample count
        """
        domain_counts = {}

        for sample in self.stream_samples():
            domain = sample.metadata['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        return domain_counts


# Quick test/demo function
def demo():
    """Demonstrate HC3 data source"""
    print("Loading HC3 dataset...")
    source = HC3DataSource(streaming=True)

    print("\nDataset metadata:")
    metadata = source.get_metadata()
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    print("\nLoading 5 human samples:")
    human_samples = source.load_samples(limit=5, source_filter='human')
    for i, sample in enumerate(human_samples, 1):
        print(f"\n[Sample {i}] {sample.sample_id}")
        print(f"Domain: {sample.metadata['domain']}")
        print(f"Text (first 100 chars): {sample.text[:100]}...")

    print("\nLoading 5 AI samples:")
    ai_samples = source.load_samples(limit=5, source_filter='chatgpt')
    for i, sample in enumerate(ai_samples, 1):
        print(f"\n[Sample {i}] {sample.sample_id}")
        print(f"Domain: {sample.metadata['domain']}")
        print(f"Text (first 100 chars): {sample.text[:100]}...")


if __name__ == "__main__":
    demo()
