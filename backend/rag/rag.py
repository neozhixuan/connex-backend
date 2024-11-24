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
        # - returns results in order, from highest similarity
        results = self.vector_store.similarity_search(query, k=self.numResults)

        res = []
        for i, result in enumerate(results):
            res.append({i: result.page_content})

        return res

    def get_rag_response(self, query):
        # 1. Connect to Redis VectorStore
        # 2. Initialize the retriever
        retriever = self.vector_store.as_retriever(
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
