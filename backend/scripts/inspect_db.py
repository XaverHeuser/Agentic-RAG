import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.database import AgentStore


def run_inspection():
    """Prints database statistics and a sample entry."""
    config = Config()

    # Access ChromaDB via AgentStore
    store = AgentStore(config)
    content = store.vector_db.get()

    count = len(content['ids'])
    print('\n---Database Statistics ---')
    print(f'Total Chunks: {count}')

    if count > 0:
        print('\n--- Sample Entry (First Chunk) ---')
        print(f'ID:       {content["ids"][0]}')
        print(f'Metadata: {content["metadatas"][0]}')
        print(f'Content:  {content["documents"][0][:500]}...')
    else:
        print('\nThe database is currently empty.')


if __name__ == '__main__':
    run_inspection()
