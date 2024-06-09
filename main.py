from dotenv import load_dotenv
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
import prompt_templates

# load .env file into environment variables
# langchain is configured to look for OPENAI_API_KEY in environment variables
# if not supplied explicitly
load_dotenv()

# parse the pdf
file_path = (
    "pdf-files/bowhead-whale.pdf"  # <<<<< change source pdf file path here <<<<<
)
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()
full_text = "\n".join(page.page_content for page in pages)

# gpt-3.5-turbo has a context window of 16,385 tokens
# becuase I don't want to use a more expensive model for testing,
# I will only send the first 8,000 words to the model

clipped_text = " ".join(full_text.split(" ")[:8000])

# Note: there are more sophisticated ways of dealing with this
# for example, splitting into chunks and doing a recursive summarisation
# request to the LLM


def generateSummary(src_text: str, model_identifier: str):
    model = ChatOpenAI(model=model_identifier)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_templates.summary_system_template),
            ("user", prompt_templates.summary_user_template),
        ]
    )

    class Summary(BaseModel):
        missingEntities: str
        denserSummary: str

    class Result(BaseModel):
        summaryList: List[Summary]
        title: str
        authors: List[str]
        slug: str
        introduction: str
        publicationDate: Optional[str]
        keywords: List[str]
        link: Optional[str]

    parser = JsonOutputParser(pydantic_object=Result)
    chain = prompt_template | model | parser
    result = chain.invoke({"text": src_text})
    return result

# summary_result = generateSummary(clipped_text, "gpt-3.5-turbo")

def print_for_summary(summary_result):
    print("--- The result as a JSON object ---")
    print(json.dumps(summary_result, indent=4), "\n")
    print("--- Final summary ---")
    print(summary_result["summaryList"][-1]["denserSummary"], "\n")

    for key in [key for key in summary_result.keys() if key != "summaryList"]:
        print(f"{key}: {summary_result[key]}", "\n")

    print("--- Full summary list ---\n")
    for summary in summary_result["summaryList"]:
        print("Missing entities:", summary["missingEntities"])
        print("The new denser summary:", summary["denserSummary"], "\n")

# print_for_summary(summary_result)

def generateContent(src_text: str, model_identifier: str):
    model = ChatOpenAI(model=model_identifier)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_templates.content_chain_system_first),
            ("user", prompt_templates.content_chain_user_first),
        ]
    )

    class Summary(BaseModel):
        missingEntities: str
        newSummary: str

    class Result(BaseModel):
        summaries: List[Summary]

    parser = JsonOutputParser(pydantic_object=Result)
    chain = prompt_template | model | parser
    first_result = chain.invoke({"text": src_text})

    ### Debugging output section
    print("--- Result of first iteration ---\n")
    for content in first_result["summaries"]:
        print("--- Iteration ---\n")
        print(f"Missing entities: {content["missingEntities"]}")
        print(f"New content:\n{content["newSummary"]}")

    # pull out the final version from the first iteration
    iteration_text = first_result["summaries"][-1]["newSummary"]

    class Summary(BaseModel):
        missingEntities: str
        newSummary: str

    class Result(BaseModel):
        summaries: List[Summary]

    prompt_template_iteration = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_templates.content_chain_system_recursive),
            ("user", prompt_templates.content_chain_user_recursive),
        ]
    )
    chain_recursive = prompt_template | model | parser

    # repeat the iteration step three times
    for i in range(3):
        result = chain_recursive.invoke({"text": src_text, "content": iteration_text})
        iteration_text = result["summaries"][-1]["newSummary"]

        ### Debugging output section
        print(f"--- Result of {i + 2} iteration ---\n")
        for content in result["summaries"]:
            print("--- Iteration ---\n")
            print(f"Missing entities: {content["missingEntities"]}")
            print(f"New content:\n{content["newSummary"]}")

    return iteration_text


content_result = generateContent(clipped_text, "gpt-3.5-turbo")

print("--- Final text repeated ---\n")
print(content_result)