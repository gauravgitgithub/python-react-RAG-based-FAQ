import re
from typing import List, Dict


class TextChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[Dict[str, any]]:
        """Split text into overlapping chunks"""
        if not text.strip():
            return []
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        start_pos = 0
        
        for sentence in sentences:
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "start": start_pos,
                        "end": start_pos + len(current_chunk.strip())
                    })
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and chunks:
                    # Get last chunk's end portion for overlap
                    last_chunk = chunks[-1]["text"]
                    overlap_text = last_chunk[-self.chunk_overlap:] if len(last_chunk) > self.chunk_overlap else last_chunk
                    
                    # Find the last sentence boundary in overlap
                    overlap_sentences = self._split_into_sentences(overlap_text)
                    if overlap_sentences:
                        current_chunk = overlap_sentences[-1] + " "
                        start_pos = chunks[-1]["end"] - len(overlap_sentences[-1])
                    else:
                        current_chunk = sentence + " "
                        start_pos = chunks[-1]["end"]
                else:
                    current_chunk = sentence + " "
                    start_pos = len(" ".join([chunk["text"] for chunk in chunks])) + 1
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "start": start_pos,
                "end": start_pos + len(current_chunk.strip())
            })
        
        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[\r\n\t]', ' ', text)
        
        return text.strip()

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be improved with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Add back the punctuation
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences

    def split_by_paragraphs(self, text: str) -> List[Dict[str, any]]:
        """Split text by paragraphs"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_pos = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                chunks.append({
                    "text": paragraph,
                    "start": current_pos,
                    "end": current_pos + len(paragraph)
                })
                current_pos += len(paragraph) + 2  # +2 for '\n\n'
        
        return chunks

    def split_by_words(self, text: str, words_per_chunk: int = 200) -> List[Dict[str, any]]:
        """Split text by word count"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), words_per_chunk):
            chunk_words = words[i:i + words_per_chunk]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "start": i,
                "end": i + len(chunk_words)
            })
        
        return chunks 