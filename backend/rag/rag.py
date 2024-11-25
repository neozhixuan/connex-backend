from langchain_community.vectorstores import Redis
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models import ChatOpenAI
import redis

# Split text into smaller chunks (LangChain standard practice)
from langchain.text_splitter import CharacterTextSplitter

import os

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not found")


class RAG:
    def __init__(self):
        # Globals
        self.numResults = 3

        # Redis setup
        self.redis_host = "redis"
        self.redis_port = 6379
        self.redis_password = None

        # Initialize OpenAI embeddings
        # self.embeddings = OpenAIEmbeddings()
        self.embeddings = GPT4AllEmbeddings()

        # Initialize Redis connection
        self.redis_conn = redis.Redis(
            host=self.redis_host, port=self.redis_port, password=self.redis_password)

    def vectorize_and_store(self, text, index_name, chunk_size, metadata=None):
        try:
            print("Starting to vectorize text...")

            # Initialize text splitter
            text_splitter = CharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=200)

            # Split text into chunks
            chunks = text_splitter.split_text(text)
            print(f"Text split into {len(chunks)} chunks")

            # Initialize Redis VectorStore
            vector_store = Redis(
                index_name=index_name,
                embedding=self.embeddings,
                redis_url=f"redis://{self.redis_host}:{self.redis_port}"
            )
            print(
                f"Redis VectorStore initialized with index name: '{index_name}'")
            print(f"VectorStore key prefix: '{vector_store.key_prefix}'")

            print("Storing chunks in Redis...")

            # Store chunks in Redis VectorStore
            for i, chunk in enumerate(chunks):
                # Preview chunk content
                print(f"Processing chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
                if metadata:
                    # Customize this as needed
                    myMetadata = {"source": metadata}
                    print(f"Storing with metadata: {myMetadata}")
                    vector_store.add_texts([chunk], metadatas=[myMetadata])
                else:
                    print("Storing without metadata")
                    vector_store.add_texts([chunk])
                print(f"Chunk {i+1} stored")

            print(
                f"Successfully vectorized {len(chunks)} chunks and stored in Redis.")

            # Debug: Verify keys in Redis after storing
            search_pattern = f"{vector_store.key_prefix}:*"
            print(
                f"Using search pattern: '{search_pattern}' to fetch keys from Redis")

            stored_keys = self.redis_conn.keys(search_pattern)
            if stored_keys:
                print(
                    f"Keys in Redis after storage: {[key.decode('utf-8') for key in stored_keys]}")
            else:
                print(
                    f"No keys found in Redis for pattern '{search_pattern}' after storage.")

            return {"status": "success"}

        except Exception as e:
            print(f"Error during vectorization or storage: {e}")
            return {"status": "failure", "error": str(e)}

    def get_similar_results(self, query, index_name):
        # Query the vector store for similar text
        # - returns results in order, from highest similarity
        vector_store = Redis(index_name=index_name, embedding=self.embeddings,
                             redis_url=f"redis://{self.redis_host}:{self.redis_port}")

        results = vector_store.similarity_search(query, k=self.numResults)

        res = []
        for i, result in enumerate(results):
            if "metadata" in result:
                print("Metadata found")
                res.append(
                    {i: {"page_content": result.page_content, "metadata": result.metadata["source"]}})
            else:
                res.append({i: {"page_content": result.page_content}})

        return res

    def get_rag_response(self, query, index_name):
        # 1. Connect to Redis VectorStore
        # 2. Initialize the retriever
        vector_store = Redis(index_name=index_name, embedding=self.embeddings,
                             redis_url=f"redis://{self.redis_host}:{self.redis_port}")

        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": self.numResults})

        # 3. Define the language model
        llm = ChatOpenAI(model="gpt-4", temperature=0)

        # 4. Define a template for RAG
        system_prompt = (
            "Use the given context to answer the question. "
            "If you don't know the answer, say you don't know. "
            "Use three sentence maximum and keep the answer concise. "
            "Context: {context}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        # 5. Create RetrievalQA chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain = create_retrieval_chain(retriever, question_answer_chain)

        # 6. Query the RAG pipeline
        result = qa_chain.invoke({"input": query})
        print("here is result")
        print(result)
        print(type(result))
        return result["answer"]

    def clear_keys(self, index_name):
        try:
            # Define the prefix used for keys
            key_prefix = f"doc:{index_name}:*"

            # Match keys with the proper prefix
            keys = self.redis_conn.keys(key_prefix)
            print(f"Keys matching pattern '{key_prefix}': {keys}")

            if not keys:
                print(f"No keys found for index '{index_name}'")
                return {"status": "success", "message": "No keys to clear"}

            # Decode keys if necessary
            keys_to_delete = [key.decode(
                'utf-8') if isinstance(key, bytes) else key for key in keys]
            print(f"Decoded keys: {keys_to_delete}")

            # Delete the keys
            self.redis_conn.delete(*keys_to_delete)
            print(f"Cleared all keys for index '{index_name}'")
            return {"status": "success", "message": f"Cleared all keys for index '{index_name}'"}
        except Exception as e:
            print(f"Error while clearing keys: {e}")
            return {"status": "failure", "error": str(e)}
