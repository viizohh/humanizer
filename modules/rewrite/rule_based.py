"""
Rule-Based Text Rewriter

Implements TextTransformer protocol without neural models (no GPU required)
Applies surface and structural transformations per research findings

Phase 1 + Phase 2 Implementation:
- Fixed regex patterns (no word boundary after punctuation)
- Smart contractions (pronouns only, not nouns)
- Paragraph preservation (split/process/rejoin on double newlines)
- Sentence length variation (split >25 words, combine <8 words)
- Smart transition handling (probabilistic replacement/removal)
- Intensity level differentiation (minimal to aggressive)
"""

from typing import List, Tuple
from interfaces import TextSample, TransformationResult
import re
import random


class RuleBasedRewriter:
    """Rule-based text transformation (no GPU/neural models required)"""

    def transform(self, text: str, transformation_level: str = 'surface', intensity: str = 'medium') -> TransformationResult:
        """Transform text at specified level and intensity"""
        if not text or not text.strip():
            return TransformationResult(
                original_text=text,
                transformed_text=text,
                transformation_type=transformation_level,
                semantic_similarity=1.0,
                metadata={'method': 'rule_based', 'intensity': intensity, 'error': 'empty_input'}
            )

        # Set seed based on hash of text for deterministic but varied results
        random.seed(hash(text) % (2**32))

        try:
            if transformation_level == 'surface':
                transformed = self._surface_transform(text, intensity)
            elif transformation_level == 'structural':
                transformed = self._structural_transform(text, intensity)
            else:
                transformed = text

            # Word-based Jaccard similarity
            similarity = self._calculate_similarity(text, transformed)

            return TransformationResult(
                original_text=text,
                transformed_text=transformed,
                transformation_type=transformation_level,
                semantic_similarity=similarity,
                metadata={'method': 'rule_based', 'intensity': intensity}
            )
        except Exception as e:
            # Error handling: return original text with error metadata
            return TransformationResult(
                original_text=text,
                transformed_text=text,
                transformation_type=transformation_level,
                semantic_similarity=1.0,
                metadata={'method': 'rule_based', 'intensity': intensity, 'error': str(e)}
            )

    def batch_transform(self, samples: List[TextSample], transformation_level: str = 'surface') -> List[TransformationResult]:
        """Transform multiple samples"""
        return [self.transform(s.text, transformation_level) for s in samples]

    def _split_paragraphs(self, text: str) -> List[str]:
        """
        Split text on double newlines to preserve paragraph structure.

        Returns list of paragraphs (non-empty strings).
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs if paragraphs else [text.strip()]

    def _smart_transitions(self, sentence: str, intensity_factor: float, sentence_idx: int) -> str:
        """
        Smart transition word handling with probabilistic replacement/removal.

        Strategy per transition word:
        - 50% chance: replace with casual alternative
        - 30% chance: remove transition entirely
        - 20% chance: keep but lowercase

        Uses sentence_idx to vary random behavior across sentences.
        """
        # Seed based on sentence index for varied behavior per sentence
        random.seed(hash(sentence) + sentence_idx)

        # Transition words with their casual alternatives
        transitions = [
            ('Furthermore', 'Also'),
            ('Additionally', 'Plus'),
            ('Moreover', 'Also'),
            ('Therefore', 'So'),
            ('Nevertheless', 'Still'),
            ('However', 'But'),
        ]

        for formal, casual in transitions:
            # Pattern: word boundary before, comma after (no word boundary after punctuation)
            pattern = r'\b' + formal + r','

            if re.search(pattern, sentence):
                choice = random.random()

                if choice < 0.5:  # 50% - replace with casual
                    sentence = re.sub(pattern, casual + ',', sentence)
                elif choice < 0.8:  # 30% - remove (0.5 to 0.8)
                    sentence = re.sub(pattern + r'\s*', '', sentence)
                else:  # 20% - keep but lowercase
                    sentence = re.sub(pattern, formal.lower() + ',', sentence)

        return sentence

    def _vary_sentence_length(self, sentences: List[str], intensity_factor: float) -> List[str]:
        """
        Vary sentence length based on word count thresholds.

        Rules:
        - Sentences >25 words: split at first conjunction (and, but, because, while)
        - Consecutive sentences <8 words: combine with connector

        Application frequency based on intensity:
        - minimal (0.2): never
        - light (0.4): 10%
        - medium (0.6): 30%
        - heavy (0.8): 60%
        - aggressive (1.0): 90%
        """
        if intensity_factor < 0.2:
            return sentences

        # Determine application probability
        variation_probability = {
            0.2: 0.0,   # minimal - never
            0.4: 0.1,   # light - 10%
            0.6: 0.3,   # medium - 30%
            0.8: 0.6,   # heavy - 60%
            1.0: 0.9,   # aggressive - 90%
        }

        # Find closest intensity level
        prob = 0.0
        for threshold in sorted(variation_probability.keys()):
            if intensity_factor >= threshold:
                prob = variation_probability[threshold]

        varied_sentences = []
        i = 0

        while i < len(sentences):
            sentence = sentences[i]
            words = sentence.split()
            word_count = len(words)

            # Split long sentences (>25 words) at first conjunction
            if word_count > 25 and random.random() < prob:
                conjunctions = [' and ', ' but ', ' because ', ' while ']
                split_done = False

                for conj in conjunctions:
                    if conj in sentence:
                        parts = sentence.split(conj, 1)
                        if len(parts) == 2 and len(parts[0].split()) > 5:
                            first = parts[0].strip()
                            second = parts[1].strip()
                            # Capitalize second part
                            if second:
                                second = second[0].upper() + second[1:] if len(second) > 1 else second.upper()
                            varied_sentences.append(first)
                            varied_sentences.append(second)
                            split_done = True
                            break

                if not split_done:
                    varied_sentences.append(sentence)
                i += 1

            # Combine consecutive short sentences (<8 words each)
            elif (word_count < 8 and
                  i < len(sentences) - 1 and
                  len(sentences[i + 1].split()) < 8 and
                  random.random() < prob):

                next_sent = sentences[i + 1]
                connectors = [', and ', ' – ', ', so ']
                connector = random.choice(connectors)

                # Lowercase first letter of second sentence
                next_lower = next_sent[0].lower() + next_sent[1:] if len(next_sent) > 1 else next_sent.lower()
                combined = sentence + connector + next_lower

                varied_sentences.append(combined)
                i += 2

            else:
                varied_sentences.append(sentence)
                i += 1

        return varied_sentences

    def _surface_transform(self, text: str, intensity: str = 'medium') -> str:
        """
        Surface-level transformations with intensity differentiation.

        Intensity levels:
        - minimal (0.2): Only hedging removal
        - light (0.4): + pattern replacements + negative contractions only
        - medium (0.6): + smart pronoun contractions + 30% sentence variation
        - heavy (0.8): + 60% sentence variation + aggressive transition removal
        - aggressive (1.0): + 90% sentence variation + maximum all transformations
        """
        intensity_map = {
            'minimal': 0.2,
            'light': 0.4,
            'medium': 0.6,
            'heavy': 0.8,
            'aggressive': 1.0
        }
        intensity_factor = intensity_map.get(intensity, 0.6)

        # Phase 1 Fix: Split on \n\n BEFORE sentence processing
        paragraphs = self._split_paragraphs(text)
        transformed_paragraphs = []

        for para_idx, paragraph in enumerate(paragraphs):
            # Split into sentences
            sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
            transformed_sentences = []

            for sent_idx, sentence in enumerate(sentences):
                modified = sentence

                # MINIMAL (0.2): Only hedging removal
                if intensity_factor >= 0.2:
                    hedging_patterns = [
                        (r'\bIt is important to note that\b', ''),
                        (r'\bIt\'s important to note that\b', ''),
                        (r'\bIt should be noted that\b', ''),
                        (r'\bIt is worth mentioning that\b', ''),
                        (r'\bIt\'s worth noting that\b', ''),
                    ]
                    for pattern, replacement in hedging_patterns:
                        modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)

                    # Clean up double spaces after hedging removal
                    modified = re.sub(r'\s+', ' ', modified).strip()

                # LIGHT (0.4): + pattern replacements + negative contractions
                if intensity_factor >= 0.4:
                    # Phase 1 Fix: Patterns with \b before comma, NO \b after punctuation
                    patterns = [
                        (r'\bFurthermore,', 'Also,'),
                        (r'\bAdditionally,', 'Plus,'),
                        (r'\bMoreover,', 'Also,'),
                        (r'\bHowever,', 'But'),
                        (r'\bNevertheless,', 'Still,'),
                        (r'\bTherefore,', 'So'),
                        (r'\bFor example,', 'Like,'),
                        (r'\bFor instance,', 'Say,'),
                        (r'\bIn order to\b', 'to'),
                        (r'\bas well as\b', 'and'),
                        (r'\bdue to the fact that\b', 'because'),
                        (r'\bin the event that\b', 'if'),
                        (r'\bat this point in time\b', 'now'),
                        (r'\bat the present time\b', 'now'),
                        (r'\bfor the purpose of\b', 'to'),
                    ]
                    for pattern, replacement in patterns:
                        modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)

                    # Vocabulary simplification
                    vocab_swaps = {
                        'utilize': 'use', 'utilizes': 'uses', 'utilized': 'used', 'utilizing': 'using',
                        'facilitate': 'help', 'facilitates': 'helps', 'facilitated': 'helped',
                        'numerous': 'many', 'various': 'different',
                        'obtain': 'get', 'obtains': 'gets', 'obtained': 'got',
                        'purchase': 'buy', 'purchases': 'buys', 'purchased': 'bought',
                        'demonstrate': 'show', 'demonstrates': 'shows', 'demonstrated': 'showed',
                        'investigate': 'check', 'approximately': 'about', 'sufficient': 'enough',
                        'attempt': 'try', 'attempts': 'tries', 'attempted': 'tried',
                        'assist': 'help', 'assists': 'helps', 'assisted': 'helped',
                        'commence': 'start', 'commences': 'starts', 'commenced': 'started',
                        'terminate': 'end', 'terminates': 'ends', 'terminated': 'ended',
                        'prior to': 'before', 'subsequent to': 'after',
                        'in addition to': 'besides', 'with regard to': 'about',
                        'concerning': 'about', 'regarding': 'about',
                    }
                    for formal, casual in vocab_swaps.items():
                        modified = re.sub(r'\b' + formal + r'\b', casual, modified, flags=re.IGNORECASE)

                    # Negative contractions only
                    negative_contractions = [
                        (' are not ', " aren't "), (' is not ', " isn't "),
                        (' was not ', " wasn't "), (' were not ', " weren't "),
                        (' have not ', " haven't "), (' has not ', " hasn't "),
                        (' had not ', " hadn't "), (' will not ', " won't "),
                        (' would not ', " wouldn't "), (' should not ', " shouldn't "),
                        (' could not ', " couldn't "), (' do not ', " don't "),
                        (' does not ', " doesn't "), (' did not ', " didn't "),
                        (' cannot ', " can't "),
                    ]
                    for full, contracted in negative_contractions:
                        modified = modified.replace(full, contracted)

                # MEDIUM (0.6): + smart pronoun contractions
                if intensity_factor >= 0.6:
                    # Phase 1 Fix: Smart contractions - ONLY after pronouns
                    # Pattern matches pronouns followed by "are", "is", "will", "have", "would", "had"
                    pronoun_contractions = [
                        (r'\b(they|we|you|who|that|which) are\b', r"\1're"),
                        (r'\b(he|she|it|that|which|who) is\b', r"\1's"),
                        (r'\b(I|you|we|they|he|she|it) will\b', r"\1'll"),
                        (r'\b(I|you|we|they) have\b', r"\1've"),
                        (r'\b(I|you|we|they|he|she) would\b', r"\1'd"),
                        (r'\b(I|you|we|they|he|she) had\b', r"\1'd"),
                    ]
                    for pattern, replacement in pronoun_contractions:
                        modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)

                    # Remove filler words
                    modified = re.sub(r'\b(very|really|quite|rather|somewhat|fairly|pretty)\s+', '', modified, flags=re.IGNORECASE)

                # HEAVY (0.8): More aggressive transformations
                if intensity_factor >= 0.8:
                    # Phase 2: Smart transition handling
                    modified = self._smart_transitions(modified, intensity_factor, sent_idx)

                # AGGRESSIVE (1.0): Maximum transformations
                # Note: Informal slang (wanna, gonna, gotta) removed - inappropriate for written text
                # Aggressive relies on 90% sentence variation + all other transformations

                transformed_sentences.append(modified)

            # Phase 2: Sentence length variation (applied to each paragraph)
            transformed_sentences = self._vary_sentence_length(transformed_sentences, intensity_factor)

            # Rejoin sentences in paragraph
            paragraph_text = '. '.join(transformed_sentences)
            if not paragraph_text.endswith('.'):
                paragraph_text += '.'

            transformed_paragraphs.append(paragraph_text)

        # Phase 1 Fix: Rejoin paragraphs with \n\n to preserve structure
        result = '\n\n'.join(transformed_paragraphs)

        # Clean up spaces and punctuation (preserve paragraph breaks)
        # Split on paragraph breaks, clean each paragraph, rejoin
        paragraphs_for_cleanup = result.split('\n\n')
        cleaned_paragraphs = []
        for para in paragraphs_for_cleanup:
            # Clean up multiple spaces within paragraph
            para = re.sub(r' +', ' ', para)
            para = re.sub(r'\s+([.,!?;:])', r'\1', para)
            para = re.sub(r'\.{2,}', '.', para)
            cleaned_paragraphs.append(para.strip())

        result = '\n\n'.join(cleaned_paragraphs)
        return result.strip()

    def _structural_transform(self, text: str, intensity: str = 'medium') -> str:
        """
        Structural transformations (combines surface + additional structural changes).

        Currently applies surface transformations with sentence variation.
        Future: clause reordering, passive/active voice conversion.
        """
        # For now, structural just applies surface with full sentence variation
        return self._surface_transform(text, intensity)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Word-based Jaccard similarity (0.0 to 1.0)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
