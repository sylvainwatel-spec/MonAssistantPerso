
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.vector_store_service import VectorStoreService

def test_persistence():
    print("Initializing VectorStoreService...")
    service = VectorStoreService()
    
    kb_id = "test_persistence_id"
    
    # 1. Create KB
    print(f"Creating KB {kb_id}...")
    try:
        service.create_knowledge_base(kb_id, "Test Persistence", "Test Description")
    except Exception as e:
        print(f"Creation failed (maybe exists): {e}")

    # 2. Add Data
    print("Adding document...")
    embedding = [0.1] * 384 # Dummy embedding
    doc = {
        "id": "doc1",
        "text": "This is a test document",
        "metadata": {"source": "test"}
    }
    
    service.add_documents(kb_id, [doc], [embedding])
    
    # 3. Check Stats immediately
    stats = service.get_stats(kb_id)
    print(f"Stats immediate: {stats}")
    
    if stats['chunk_count'] == 0:
        print("FAIL: Data not added immediately.")
        return

    # 4. Re-initialize Service to simulate app restart/new instance
    print("Re-initializing service...")
    service2 = VectorStoreService()
    stats2 = service2.get_stats(kb_id)
    print(f"Stats after re-init: {stats2}")
    
    if stats2['chunk_count'] > 0:
        print("SUCCESS: Data persisted.")
    else:
        print("FAIL: Data did NOT persist.")

    # Cleanup
    # service.delete_knowledge_base(kb_id)

if __name__ == "__main__":
    test_persistence()
