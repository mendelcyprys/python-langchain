from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader

# load .env file into system variables
load_dotenv()

# choose our model
model = ChatOpenAI(model="gpt-3.5-turbo")

# parse the pdf
file_path = "pdf-files/bowhead-whale.pdf"
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()
full_text = "\n".join(page.page_content for page in pages)

system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

parser = StrOutputParser()

chain = prompt_template | model | parser

#result = chain.invoke({"language": "Ukrainian", "text": "How are you feeling today?"})

#print(result)
