import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.utilities.arxiv import ArxivAPIWrapper
from mcp.server.fastmcp import FastMCP
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import init_chat_model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from prompts import map_prompt_template, combine_prompt_template


load_dotenv()

mcp = FastMCP("Arxiv MCP Server")

# Configure the wrapper with desired settings
arxiv_wrapper = ArxivAPIWrapper(
    top_k_results=5,
    load_all_available_meta=True,
    doc_content_chars_max=None,
    continue_on_failure=False
)

@mcp.tool()
def search_papers(query: str, max_results: int):
    # Set dynamic result limit
    arxiv_wrapper.top_k_results = max_results

    # Directly get LangChain Documents with metadata
    documents = arxiv_wrapper.load(query)

    # Extract useful fields into structured dictionaries
    research_papers = []
    for doc in documents:
        research_papers.append({
            "title": doc.metadata.get("Title"),
            "authors": doc.metadata.get("Authors"),
            "summary": doc.metadata.get("Summary"),
            "pdf_url": doc.metadata.get("links")[1],
            "published": doc.metadata.get("Published"),
            "arxiv_url": doc.metadata.get("links")[0],
        })

    return research_papers




MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])
COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER_FOR_SUMMARY")
MODEL_NAME = os.getenv("MODEL_NAME_FOR_SUMMARY")

llm = init_chat_model(
    MODEL_PROVIDER+":"+MODEL_NAME,
    temperature=0.2
)

@mcp.tool()
def pdf_summarize(pdf_url):
    loader = PyMuPDFLoader(pdf_url)
    docs = loader.load()
    if not docs:
        return {"error": "Failed to load PDF"}
    print(f"The length of docs is: {len(docs)}")
    doc = docs[0]

    full_text = "\n".join([doc.page_content for doc in docs])
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap = 500)
    chunks = text_splitter.create_documents([full_text])
    print(f"Document split into {len(chunks)} chunks for processing.")

    map_reduce_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
         map_prompt=MAP_PROMPT,
        combine_prompt=COMBINE_PROMPT,
        verbose=False
    )

    summary = map_reduce_chain.invoke(chunks)
    return summary["output_text"]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    # query = "The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity"
    # result = search_papers(query, 3) 
    # print(result)
    # for i, p in enumerate(result, start=1):
    #     print(f"[{i}] {p['title']} — {(p['authors'])} ({p['published']})")
    #     print(f"    PDF: {p['pdf_url']}")
    #     print(f"    Abstract: {p['summary'][:200]}…\n")