import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Union

class ParagraphMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))

    def find_similar_paragraphs(self, input_paragraphs: List[str], reference_paragraphs: Union[str, List[str]]) -> List[Dict]:
        if isinstance(reference_paragraphs, str):
            reference_paragraphs = [reference_paragraphs]

        all_texts = input_paragraphs + reference_paragraphs
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)

        input_vectors = tfidf_matrix[:len(input_paragraphs)]
        reference_vectors = tfidf_matrix[len(input_paragraphs):]

        similarities = cosine_similarity(input_vectors, reference_vectors)

        results = []
        for ref_idx, ref_para in enumerate(reference_paragraphs):
            ref_similarities = similarities[:, ref_idx]
            most_similar_idx = np.argmax(ref_similarities)
            max_similarity = ref_similarities[most_similar_idx]

            results.append({
                'reference_paragraph': ref_para,
                'most_similar_paragraph': input_paragraphs[most_similar_idx],
                'similarity_score': float(max_similarity),
                'paragraph_index': most_similar_idx
            })

        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results