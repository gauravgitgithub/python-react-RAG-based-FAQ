import asyncio
from typing import List
from app.core.config import settings
from app.schemas.document import SourceChunk


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_api_key = settings.OPENAI_API_KEY

    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using the configured LLM provider"""
        if self.provider == "openai" and self.openai_api_key:
            return await self._generate_openai_answer(question, context)
        else:
            return await self._generate_stubbed_answer(question, context)

    async def _generate_openai_answer(self, question: str, context: str) -> str:
        """Generate answer using OpenAI API"""
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            prompt = f"""Based on the following context, please answer the question. 
            If the context doesn't contain enough information to answer the question, 
            say "I don't have enough information to answer this question."

            Context:
            {context}

            Question: {question}

            Answer:"""

            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to stubbed answer if OpenAI fails
            return await self._generate_stubbed_answer(question, context)

    async def _generate_stubbed_answer(self, question: str, context: str) -> str:
        """Generate a stubbed answer for testing purposes"""
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
        
        # Generate a simple answer based on the context
        answer_parts = [
            "Based on the available information:",
            " ".join(relevant_info[:3])  # Use first 3 relevant lines
        ]
        
        return " ".join(answer_parts)

    async def generate_summary(self, text: str) -> str:
        """Generate a summary of the given text"""
        if self.provider == "openai" and self.openai_api_key:
            return await self._generate_openai_summary(text)
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

    async def _generate_stubbed_summary(self, text: str) -> str:
        """Generate a stubbed summary"""
        await asyncio.sleep(0.05)
        
        # Simple summary: first 100 characters + "..."
        if len(text) > 100:
            return text[:100] + "..."
        return text 