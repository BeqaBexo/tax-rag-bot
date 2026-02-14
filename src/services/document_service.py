"""
Document Service - დოკუმენტების მენეჯმენტი
"""
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from config.settings import settings


class DocumentService:
    """დოკუმენტების ჩატვირთვა და დამუშავება"""
    
    def __init__(self):
        self.documents_dir = settings.DOCUMENTS_DIR
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def load_documents(self, directory_path=None):
        """
        ტვირთავს ყველა PDF ფაილს
        
        Args:
            directory_path: საქაღალდის გზა (None = default)
        
        Returns:
            list: დოკუმენტების chunks
        """
        if directory_path is None:
            directory_path = self.documents_dir
        
        print(f"📂 ვტვირთავ დოკუმენტებს: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"საქაღალდე ვერ მოიძებნა: {directory_path}")
        
        # ვტვირთავ PDF-ებს
        loader = DirectoryLoader(
            str(directory_path),
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        
        try:
            documents = loader.load()
            print(f"✅ ჩაიტვირთა {len(documents)} გვერდი")
        except Exception as e:
            print(f"❌ შეცდომა: {e}")
            return []
        
        if len(documents) == 0:
            print("⚠️ არცერთი დოკუმენტი ვერ მოიძებნა!")
            return []
        
        # ვყოფთ chunks-ად
        chunks = self._split_documents(documents)
        print(f"✂️ შეიქმნა {len(chunks)} ტექსტური ნაწილი")
        
        return chunks
    
    def _split_documents(self, documents):
        """ტექსტის chunks-ად დაყოფა"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        return text_splitter.split_documents(documents)
    
    def get_documents_info(self):
        """დოკუმენტების შესახებ ინფორმაცია"""
        if not os.path.exists(self.documents_dir):
            return {"count": 0, "files": []}
        
        pdf_files = list(Path(self.documents_dir).glob("**/*.pdf"))
        
        return {
            "count": len(pdf_files),
            "files": [f.name for f in pdf_files],
            "total_size_mb": sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
        }


# ტესტი
if __name__ == "__main__":
    service = DocumentService()
    
    print("📊 დოკუმენტების ინფო:")
    info = service.get_documents_info()
    print(f"  ფაილები: {info['count']}")
    print(f"  ზომა: {info['total_size_mb']:.2f} MB")
    print(f"  სახელები: {info['files']}")
    
    print("\n📂 დოკუმენტების ჩატვირთვა:")
    docs = service.load_documents()
    
    if len(docs) > 0:
        print(f"\n📄 პირველი chunk:")
        print(docs[0].page_content[:200])
        print(f"\n📌 Metadata: {docs[0].metadata}")