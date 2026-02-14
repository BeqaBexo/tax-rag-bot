"""
RAG Service - მთავარი RAG ლოგიკა
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config.settings import settings
from src.core.prompt_manager import PromptManager
from src.services.vectordb_service import VectorDBService


class RAGService:
    """RAG სისტემა"""
    
    def __init__(self, prompt_type="base"):
        print("🚀 ვაქტიურებ RAG სერვისს...")
        
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("❌ ANTHROPIC_API_KEY არ არის დაყენებული!")
        
        self.prompt_manager = PromptManager()
        self.prompt_type = prompt_type
        
        self.vectordb_service = VectorDBService()
        self.vectordb = self.vectordb_service.load_database()
        
        prompt_metadata = self.prompt_manager.get_metadata(prompt_type)
        self.llm = ChatAnthropic(
            model=settings.CLAUDE_MODEL,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=prompt_metadata['temperature'],
            max_tokens=prompt_metadata['max_tokens']
        )
        
        self.retriever = self.vectordb.as_retriever(
            search_kwargs={"k": settings.TOP_K_RESULTS}
        )
        
        self._build_chain()
        print("✅ RAG სერვისი მზადაა!")
    
    def _build_chain(self):
        prompt_config = self.prompt_manager.get_prompt(self.prompt_type)
        full_prompt = prompt_config['system'] + "\n\n" + prompt_config['template']
        
        self.prompt_template = ChatPromptTemplate.from_template(full_prompt)
        
        self.chain = (
            {
                "context": self.retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def _format_docs(self, docs):
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'უცნობი')
            if '/' in source or '\\' in source:
                source = Path(source).name
            page = doc.metadata.get('page', 'N/A')
            formatted.append(
                f"[დოკუმენტი {i}: {source}, გვ. {page}]\n{doc.page_content}\n"
            )
        return "\n".join(formatted)
    
    def ask(self, question):
        print(f"\n❓ კითხვა: {question}")
        print("🔍 ვეძებ რელევანტურ დოკუმენტებს...")
        
        relevant_docs = self.retriever.invoke(question)
        
        print(f"📚 ვიპოვე {len(relevant_docs)} რელევანტური დოკუმენტი")
        print("🤖 ვეკითხები Claude-ს...")
        
        answer = self.chain.invoke(question)
        
        response = {
            "question": question,
            "answer": answer,
            "sources": []
        }
        
        for doc in relevant_docs:
            source = doc.metadata.get("source", "უცნობი")
            if '/' in source or '\\' in source:
                source = Path(source).name
            
            source_info = {
                "file": source,
                "page": doc.metadata.get("page", "N/A"),
                "content_preview": doc.page_content[:200] + "..."
            }
            response["sources"].append(source_info)
        
        return response
    
    def print_response(self, response):
        print("\n" + "="*70)
        print("📋 პასუხი:")
        print("="*70)
        print(response["answer"])
        print("\n" + "="*70)
        print("📚 წყაროები:")
        print("="*70)
        
        for i, source in enumerate(response["sources"], 1):
            print(f"\n{i}. ფაილი: {source['file']}")
            print(f"   გვერდი: {source['page']}")
            print(f"   ამონარიდი: {source['content_preview']}")
    
    def get_stats(self):
        db_info = self.vectordb_service.get_database_info()
        
        return {
            "model": settings.CLAUDE_MODEL,
            "prompt_type": self.prompt_type,
            "documents_in_db": db_info.get("documents_count", 0),
            "top_k": settings.TOP_K_RESULTS,
            "chunk_size": settings.CHUNK_SIZE
        }


if __name__ == "__main__":
    print("="*70)
    print("🤖 RAG Service - ტესტირება")
    print("="*70)
    
    try:
        rag = RAGService(prompt_type="base")
        
        print("\n📊 სისტემის ინფო:")
        stats = rag.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        test_questions = [
            "რა არის დღგ?",
        ]
        
        for question in test_questions:
            response = rag.ask(question)
            rag.print_response(response)
            print("\n" + "="*70 + "\n")
        
        print("✅ RAG სისტემა წარმატებით მუშაობს!")
        
    except Exception as e:
        print(f"❌ შეცდომა: {e}")
        import traceback
        traceback.print_exc()