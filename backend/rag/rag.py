from langchain_community.vectorstores import Redis
from langchain_community.embeddings import OpenAIEmbeddings
import redis

# Split text into smaller chunks (LangChain standard practice)
from langchain.text_splitter import CharacterTextSplitter

import os

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not found")


class RAG:
    def __init__(self):
        # Redis setup
        self.redis_host = "redis"
        self.redis_port = 6379
        self.redis_password = None

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()

        # Initialize Redis connection
        self.redis_conn = redis.Redis(
            host=self.redis_host, port=self.redis_port, password=self.redis_password)

        # Initialize vector store
        self.vector_store = Redis(index_name="test", embedding=self.embeddings,
                                  redis_url=f"redis://{self.redis_host}:{self.redis_port}")

        # Initialize text splitter
        self.text_splitter = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)

    def vectorize_and_store(self, text):
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)

            # Store chunks in Redis VectorStore
            for chunk in chunks:
                self.vector_store.add_texts([chunk])

            print(f"Vectorized {len(chunks)} chunks and stored in Redis.")

            return {"status": "success"}
        except Exception as e:
            return {"status": "failure", "error": str(e)}

    def get_similar_results(self, query):
        # Query the vector store for similar text
        results = self.vector_store.similarity_search(query, k=5)

        print("Similar results:")
        for result in results:
            print(result.page_content)
