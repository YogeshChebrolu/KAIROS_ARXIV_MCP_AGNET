# pdf_extractor.py
import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import init_chat_model
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.prompts import PromptTemplate

map_prompt_template = """
You are a researcher summarizing a scientific paper. Your task is to read the following text from a single page and extract the key points.
Focus on identifying the core arguments, experimental methods, key results, and conclusions presented on this page.
If the page contains the introduction, state the problem statement and objectives.
If it discusses methods, describe the methodology.
If it presents results, list the key findings and data points.

Do not create a narrative. Output a concise, structured list of these points.

Text:
"{text}"

DETAILED AND STRUCTURED SUMMARY OF THIS PAGE:
"""
MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])

combine_prompt_template = """
You are a skilled science communicator. You have been given a series of key points extracted from each page of a research paper.
Your task is to synthesize these points into a single, detailed, and well-structured summary.

The final summary should be organized into the following sections:
- **Introduction**: The core problem the paper addresses and its main objectives.
- **Methodology**: The key techniques, datasets, and experimental setup used.
- **Key Findings & Results**: The primary outcomes and data presented in the paper.
- **Conclusion & Implications**: The authors' conclusions and the broader implications of their work.

Do not miss any important details from the provided points. The summary should be both detailed and concise.

Key points from each page:
"{text}"

DETAILED FINAL SUMMARY:
"""
COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])


os.environ["GROQ_API_KEY"] = "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"
MODEL_PROVIDER = "groq"
MODEL_NAME = "llama3-8b-8192"
llm = init_chat_model(
    MODEL_PROVIDER+":"+MODEL_NAME,
    temperature=0.2

)

# os.environ["GOOGLE_API_KEY"] = "AIzaSyCxIoKyBiD23aNdfU9aDvdfOBgTV7Rtbok"

# MODEL_PROVIDER = "google_genai"
# MODEL_NAME = "gemini-1.5-pro"
# llm = init_chat_model(
#     MODEL_PROVIDER+":"+MODEL_NAME,
#     temperature=0.2

# )
class ExtractRequest(BaseModel):
    pdf_url: str  # e.g. "https://arxiv.org/pdf/2506.06941.pdf"


def extract_pdf(req: ExtractRequest):
    loader = PyMuPDFLoader(req.pdf_url)
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

    # return {
    #     "page_count": len(docs),
    #     "metadata": doc.metadata,
    #     "text": doc.page_content
    # }



summary = extract_pdf(ExtractRequest(pdf_url="https://www.arxiv.org/pdf/2506.06941"))
print(summary)



