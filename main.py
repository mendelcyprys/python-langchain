from dotenv import load_dotenv
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader

# load .env file into system variables
load_dotenv()

# choose our model
model = ChatOpenAI(model="gpt-3.5-turbo")

# parse the pdf
file_path = "pdf-files/bowhead-whale.pdf"   # <<<<< change source pdf file path here <<<<<
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

system_template = """Your task is to generate increasingly concise, entity-dense summaries of a research paper.
You will repeat the following 2 steps 5 times.
Step 1. Identify 1 to 3 informative Entities (";" delimited) from the article which are missing from the previously generated summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.
A Missing Entity is:
- relevant to the research paper, and relevant to being included in a high-level summary
- specific yet concise (5 words or fewer),
- novel (not in the previous summary),
- faithful (present in the article),
- anywhere (can be located anywhere in the article).
A Missing Entity is not an email, or something about FIGURE x, it must be relevant to the paper and relevant to being part of a high-level summary.

Guidelines:
- The first summary should be long (6 to 8 sentences, about 120 words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach approximately 120 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
- Make sure the text is clear of HTML Character Entities (avoid for example &quot; or &#x27)

Remember, use exactly the same number of words for each summary.

Answer in JSON. The JSON object should have an entry "summaryList", which should be a list (length 5) of dictionaries whose keys are "missingEntities" and "denserSummary".
The JSON object should also contain the following keys:
- "title": This should be the title of the article, without any changes. Double check to make sure that the title is correct and does not include bits that are not part of the title.
- "authors": A list containing the names of the authors of the aritcle.
- "slug": A slug URL for a webpage fitting for this article (lowercase, dashes instead of spaces).
- "introduction": A 1-2 sentence summary of the article, 20 to 40 words long.
- "publicationDate": The publication date of the article in the format "DD/MM/YYYY". If only the year is available then in the format "YYYY". If no date information is available, this should be null.
- "keywords": A list of the 5 most revelant keywords relating to the article.
- "link": The link to the DOI, and if not available, to the journal. If link not available, should be null.

The JSON should look like this:
{{
    summaryList: [
        {{
            missingEntities: "...",
            denserSummary: "..."
        }},
        ...
    ],
    title: "...",
    authors: ["...", ...],
    slug: "...",
    introduction: "...",
    publicationDate: "...",
    keywords: ["...", ...],
    link: "..."
}}

Write only valid JSON. Remember that summaryList should be a list of length 5.
"""

user_template = """Article: <<< {text} >>>
You will generate increasingly concise, entity-dense summaries of the above research paper.
Repeat the following 2 steps 5 times.
Step 1. Identify 1 to 3 informative Entities (";" delimited) from the article which are missing from the previously generated summary.
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the Missing Entities.
A Missing Entity is:
- relevant to the research paper, and relevant to being included in a high-level summary
- specific yet concise (5 words or fewer),
- novel (not in the previous summary),
- faithful (present in the article),
- anywhere (can be located anywhere in the article).
A Missing Entity is not an email, or something about FIGURE x, it must be relevant to the paper and relevant to being part of a high-level summary.

Guidelines:
- The first summary should be long (6 to 8 sentences, about 120 words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach approximately 120 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the article.
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities.
- Make sure the text is clear of HTML Character Entities (avoid for example &quot; or &#x27)

Remember, use exactly the same number of words for each summary.

Answer in JSON. The JSON object should have an entry "summaryList", which should be a list (length 5) of dictionaries whose keys are "missingEntities" and "denserSummary".
The JSON object should also contain the following keys:
- "title": This should be the title of the article, without any changes. Double check to make sure that the title is correct and does not include bits that are not part of the title.
- "authors": A list containing the names of the authors of the aritcle.
- "slug": A slug URL for a webpage fitting for this article (lowercase, dashes instead of spaces).
- "introduction": A 1-2 sentence summary of the article, 20 to 40 words long.
- "publicationDate": The publication date of the article in the format "DD/MM/YYYY". If only the year is available then in the format "YYYY". If no date information is available, this should be null.
- "keywords": A list of the 5 most revelant keywords relating to the article.
- "link": The link to the DOI, and if not available, to the journal. If link not available, should be null.

The JSON should look like this:
{{
    summaryList: [
        {{
            missingEntities: "...",
            denserSummary: "..."
        }},
        ...
    ],
    title: "...",
    authors: ["...", ...],
    slug: "...",
    introduction: "...",
    publicationDate: "...",
    keywords: ["...", ...],
    link: "..."
}}

Write only valid JSON. Remember that summaryList should be a list of length 5.
"""

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", user_template)]
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
    publicationDate: str
    keywords: List[str]
    link: str

parser = JsonOutputParser(pydantic_object=Result)

chain = prompt_template | model | parser

result: Result = chain.invoke({"text": clipped_text})

# Print result details to the terminal
print("--- The result as a JSON object ---")
print(json.dumps(result, indent=4), "\n")
print("--- Final summary ---")
print(result["summaryList"][-1]["denserSummary"], "\n")

for key in [key for key in result.keys() if key != "summaryList"]:
    print(f"{key}: {result[key]}", "\n")

print("--- Full summary list ---\n")
for summary in result["summaryList"]:
    print("Missing entities:", summary["missingEntities"])
    print("The new denser summary:", summary["denserSummary"], "\n")