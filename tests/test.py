from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader

# loader = WebBaseLoader("https://www.36kr.com/p/2548722571861895")
loader = WebBaseLoader("https://www.techweb.com.cn/it/2023-12-05/2937736.shtml")
docs = loader.load()

print(docs)
# llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106")
# chain = load_summarize_chain(llm, chain_type="stuff")

# chain.run(docs)
