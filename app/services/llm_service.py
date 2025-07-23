import asyncio
from typing import List
from app.core.config import settings
from app.schemas.document import SourceChunk


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_api_key = settings.OPENAI_API_KEY
        self.cohere_api_key = settings.COHERE_API_KEY

    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using the configured LLM provider"""
        if settings.is_openai_available:
            answer = await self._generate_openai_answer(question, context)
        elif settings.is_cohere_available:
            answer = await self._generate_cohere_answer(question, context)
        else:
            answer = await self._generate_stubbed_answer(question, context)
        
        # Validate and enhance answer
        return await self._validate_answer(answer, question)

    async def _generate_openai_answer(self, question: str, context: str) -> str:
        """Generate answer using OpenAI API with enhanced prompt"""
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            # Enhanced prompt for better answers
            prompt = f"""You are a helpful FAQ assistant. Answer the question based on the provided context.

Instructions:
1. Use only information from the provided context
2. If the context doesn't contain enough information, say "I don't have enough information to answer this question"
3. Be concise but comprehensive
4. If multiple sources provide different information, mention this
5. Cite the source document when possible
6. Structure your answer clearly and logically

            Context:
            {context}

            Question: {question}

            Answer:"""

            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always be accurate and cite sources when possible."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to stubbed answer if OpenAI fails
            return await self._generate_stubbed_answer(question, context)

    async def _generate_cohere_answer(self, question: str, context: str) -> str:
        """Generate answer using Cohere API with improved prompt"""
        try:
            import cohere
            
            co = cohere.Client(self.cohere_api_key)
            
            # Simplified and more effective prompt for Cohere
            prompt = f"""Based on the following information, answer the question. If the information doesn't contain enough details to answer the question, say "I don't have enough information to answer this question."

Information:
{context}

Question: {question}

Answer:"""

            response = await asyncio.to_thread(
                co.generate,
                model="command",
                prompt=prompt,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            answer = response.generations[0].text.strip()
            
            # Clean up the answer if it starts with "Answer:" or similar
            if answer.lower().startswith('answer:'):
                answer = answer[7:].strip()
            
            return answer
            
        except Exception as e:
            print(f"Cohere API error: {e}")
            # Fallback to stubbed answer if Cohere fails
            return await self._generate_stubbed_answer(question, context)

    async def _generate_stubbed_answer(self, question: str, context: str) -> str:
        """Generate a stubbed answer for testing purposes with improved logic"""
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simple template-based answer generation
        if not context.strip():
            return "I don't have enough information to answer this question."
        
        # Extract key information from context
        context_lines = context.split('\n')
        relevant_info = []
        
        for line in context_lines:
            if line.strip() and not line.startswith('Source'):
                relevant_info.append(line.strip())
        
        if not relevant_info:
            return "I don't have enough information to answer this question."
        
        # Generate a more structured answer based on the context
        answer_parts = [
            "Based on the available information:",
            " ".join(relevant_info[:3])  # Use first 3 relevant lines
        ]
        
        # Add source citation if available
        if "from" in context:
            source_info = [line for line in context_lines if "from" in line]
            if source_info:
                answer_parts.append(f"\n[Source: {source_info[0].split('from')[1].split(',')[0].strip()}]")
        
        return " ".join(answer_parts)

    async def _validate_answer(self, answer: str, question: str) -> str:
        """Validate and improve answer quality"""
        if not answer or len(answer.strip()) < 10:
            return "I don't have enough information to provide a meaningful answer."
        
        if "don't have enough information" in answer.lower():
            return answer
        
        # Add confidence indicator for non-LLM answers
        if not settings.is_llm_available:
            answer += "\n\n[This answer is based on the available documents in the system.]"
        
        return answer

    async def generate_summary(self, text: str) -> str:
        """Generate a summary of the given text"""
        if settings.is_openai_available:
            return await self._generate_openai_summary(text)
        elif settings.is_cohere_available:
            return await self._generate_cohere_summary(text)
        else:
            return await self._generate_stubbed_summary(text)

    async def _generate_openai_summary(self, text: str) -> str:
        """Generate summary using OpenAI API"""
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            prompt = f"Please provide a brief summary of the following text:\n\n{text[:1000]}..."
            
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return await self._generate_stubbed_summary(text)

    async def _generate_cohere_summary(self, text: str) -> str:
        """Generate summary using Cohere API"""
        try:
            import cohere
            
            co = cohere.Client(self.cohere_api_key)
            
            prompt = f"Please provide a brief summary of the following text:\n\n{text[:1000]}..."
            
            response = await asyncio.to_thread(
                co.generate,
                model="command",
                prompt=prompt,
                max_tokens=200,
                temperature=0.5,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            
            return response.generations[0].text.strip()
            
        except Exception as e:
            return await self._generate_stubbed_summary(text)

    async def _generate_stubbed_summary(self, text: str) -> str:
        """Generate a stubbed summary"""
        await asyncio.sleep(0.05)
        
        # Simple summary: first 100 characters + "..."
        if len(text) > 100:
            return text[:100] + "..."
        return text 