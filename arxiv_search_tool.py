import requests
import feedparser
from urllib.parse import urlencode
from langchain_community.utilities.arxiv import ArxivAPIWrapper


arxiv_wrapper = ArxivAPIWrapper(
    top_k_results=5,
    load_all_available_meta=True,
    doc_content_chars_max=None,
    continue_on_failure=False
)

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


if __name__ == "__main__":
    query = "The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity"
    result = search_papers(query, 3) 
    for i, p in enumerate(result, start=1):
        print(f"[{i}] {p['title']} — {(p['authors'])} ({p['published']})")
        print(f"    PDF: {p['pdf_url']}")
        print(f"    Abstract: {p['summary'][:200]}…\n")
