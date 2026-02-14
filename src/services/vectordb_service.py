"""
Vector Database Service
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config.settings import settings
from src.services.document_service import DocumentService
import os
import shutil


class VectorDBService:
    """Vector Database მენეჯმენტი"""
    
    def __init__(self):
        self.persist_directory = settings.VECTOR_DB_DIR
        self.collection_name = settings.COLLECTION_NAME
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embedding_device = settings.EMBEDDING_DEVICE
        self._embeddings = None
        self._vectordb = None
    
    @property
    def embeddings(self):
        """Lazy load embeddings"""
        if self._embeddings is None:
            print("🧮 ვქმნი embeddings...")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                model_kwargs={'device': self.embedding_device}
            )
        return self._embeddings
    
    def create_database(self, documents=None, force_recreate=False):
        """
        ვექტორული ბაზის შექმნა
        
        Args:
            documents: დოკუმენტები (თუ None, ჩაიტვირთება)
            force_recreate: თუ True, წაშლის ძველ ბაზას
        """
        print("🔧 ვქმნი ვექტორულ ბაზას...")
        
        # წავშალოთ ძველი თუ force_recreate
        if force_recreate and os.path.exists(self.persist_directory):
            print(f"🗑️ ვშლი ძველ ბაზას...")
            shutil.rmtree(self.persist_directory)
        
        # ჩავტვირთოთ დოკუმენტები თუ არ არის
        if documents is None:
            doc_service = DocumentService()
            documents = doc_service.load_documents()
        
        if len(documents) == 0:
            raise ValueError("❌ დოკუმენტები ცარიელია!")
        
        print(f"📊 ვქმნი ვექტორულ ბაზას {len(documents)} დოკუმენტიდან...")
        
        # ვქმნით ბაზას
        self._vectordb = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
            collection_name=self.collection_name
        )
        
        print(f"✅ ბაზა შეიქმნა: {self.persist_directory}")
        print(f"📊 დოკუმენტები: {self._vectordb._collection.count()}")
        
        return self._vectordb
    
    def load_database(self):
        """არსებული ბაზის ჩატვირთვა"""
        print(f"📂 ვტვირთავ ბაზას: {self.persist_directory}")
        
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"❌ ბაზა ვერ მოიძებნა: {self.persist_directory}")
        
        self._vectordb = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )
        
        print(f"✅ ბაზა ჩაიტვირთა! დოკუმენტები: {self._vectordb._collection.count()}")
        
        return self._vectordb
    
    def search(self, query, k=3):
        """ძებნა ვექტორულ ბაზაში"""
        if self._vectordb is None:
            self.load_database()
        
        return self._vectordb.similarity_search(query, k=k)
    
    def get_database_info(self):
        """ბაზის შესახებ ინფორმაცია"""
        if not os.path.exists(self.persist_directory):
            return {"exists": False}
        
        if self._vectordb is None:
            self.load_database()
        
        return {
            "exists": True,
            "documents_count": self._vectordb._collection.count(),
            "collection_name": self.collection_name,
            "path": str(self.persist_directory)
        }


# ტესტი
if __name__ == "__main__":
    service = VectorDBService()
    
    print("="*60)
    print("🗄️ Vector Database Service - ტესტი")
    print("="*60)
    
    # შექმნა
    db = service.create_database(force_recreate=True)
    
    # ტესტ ძებნა
    print("\n🔍 ტესტ ძებნა:")
    results = service.search("რა არის დღგ?", k=2)
    
    for i, doc in enumerate(results, 1):
        print(f"\n--- შედეგი {i} ---")
        print(doc.page_content[:150] + "...")
        print(f"წყარო: {doc.metadata.get('source', 'N/A')}")
    
    print("\n✅ ტესტი წარმატებული!")