import boto3
import json
import os
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain.prompts import PromptTemplate
from langchain.chains import SimpleSequentialChain
from langchain.chains import LLMChain
from langchain.chat_models.openai import ChatOpenAI
from langchain.llms.bedrock import Bedrock
#from langchain_community.chat_models import BedrockChat
from langchain.llms.openai import OpenAI
from langchain_core.output_parsers import JsonOutputParser
from langsmith import Client

from dotenv import load_dotenv, dotenv_values


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

#initialise LangSmith
langsmith_client = Client()

#OpenAI
llm_open_ai = OpenAI(temperature=0.0) #OpenAI(max_tokens=3500, model='gpt-3.5-turbo', temperature=0.0)

#Bedrock
BEDROCK_CLAUDE_MODEL = "anthropic.claude-v2:1"
llm_bedrock = Bedrock(
    credentials_profile_name="default",
    region_name="us-east-1",
    model_id=BEDROCK_CLAUDE_MODEL,
    model_kwargs={"max_tokens_to_sample": 5120},
)


def save_json_to_file(data, file_path):
    """
    Save JSON data to a JSON file.

    Args:
    - data: The JSON data to be saved.
    - file_path: The path to save the JSON file.
    """
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def get_top_10_quick_wins(llm):
    
    class QuickWins(BaseModel):
        quick_win_id: str = Field(description="index of quick wins for numbered list")
        best_practice_question: str = Field(description="best practice question from hri or mri filtered views")
        unselected_best_practice_item: str = Field(description="The unselected choice of best practice")
        effort_estimate: str = Field(description="classify effort into quick-wins, or longer project")

    parser = JsonOutputParser(pydantic_object=QuickWins)

    #get prompt input data
    #read json
    json_file_path = 'tmp/json/filter_high_risk_questions.json'
    with open(json_file_path) as json_file:
            json_data = json.load(json_file)
    
    #prompt template
    PROMPT_TEMPLATE_TEXT = "From the provided json, figure out which of these items are quick wins. Give me the best 10 quick wins:\n{format_instructions}\n{input_json}"

    prompt = PromptTemplate(
        template = PROMPT_TEMPLATE_TEXT,
        input_variables=["input_json"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    quick_wins_output_json = chain.invoke({"input_json": str(json_data)})
    
    return(quick_wins_output_json)

def get_quick_wins_remediation_plan(input_quick_win,llm):
    #Define parser class (Pydantic) i.e. what should the llm output be

    class QuickWinsRemediation(BaseModel):
        quick_win_id: str = Field(description="index of quick wins for numbered list")
        best_practice_option: str = Field(description="best practice option from hri or mri filtered views")
        remediation_description: str = Field(description="A description of the remediation plan")
        remediation_solution: str = Field(description="A detailed multi-paragraph elaboration on the implementation of an actual solution")
        remediation_general_considerations: str = Field(description="General best practice considerations that supplement the remediation")
        effort_estimate: str = Field(description="a detailed breakdown of the effort in terms of core milestones")
        resources_needed: str = Field(description="a list of AWS skills and roles needed to perform this remediation")
        domain_impact: str = Field(description="The area/domain it would mostly impact from the customer's business i.e. Security, Finance, etc")

    parser = JsonOutputParser(pydantic_object=QuickWinsRemediation)

    
    #prompt template
    PROMPT_TEMPLATE_TEXT = "For the item in the input json, generate a technical detailed remediation plan :\n{format_instructions}\n{input_json}"

    prompt = PromptTemplate(
        template = PROMPT_TEMPLATE_TEXT,
        input_variables=["input_json"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    quick_wins_remediation_plan_json = chain.invoke({"input_json": str(input_quick_win)})
    
    return(quick_wins_remediation_plan_json)


def quick_wins_section_prep():
    # #Choose LLM
    # #llm = llm_open_ai
    llm = llm_bedrock
    #Get quick wins
    quick_wins_output = get_top_10_quick_wins(llm)
    file_path = "tmp/json/top_10_quick_wins.json"
    save_json_to_file(quick_wins_output, file_path)
    print("quick wins top 10 file saved")

    # #Get remediation plan
    # Read JSON file
    json_file_path = 'tmp/json/top_10_quick_wins.json'
    with open(json_file_path) as json_file:
        json_data = json.load(json_file)

    # Loop through each item in the JSON data
    remediation_pts_file_paths = []
    for item in json_data:
        remediation_item = get_quick_wins_remediation_plan(item,llm)
        index = item["quick_win_id"]
        file_path = f"tmp/json/quickwins/quick_wins_remediation_pt{index}.json"
        save_json_to_file(remediation_item, file_path)
        print(f"{file_path} saved successfully")
        remediation_pts_file_paths.append(file_path)
    
    # get sparccl products mapped
    get_sparkccl_products(llm)
    return(remediation_pts_file_paths)


#### Get CCL / Spark Products
def get_sparkccl_products(llm):
    #Define parser class (Pydantic) i.e. what should the llm output be

    class SparkCCLProducts(BaseModel):
        product_title: str = Field(description="SparkCCL product title")
        description: str = Field(description="description of SparkCCL product or service")
        key_deliverables: str = Field(description="Key Deliverables as part of product")
        artefacts: str = Field(description="artefacts from product or service")
        justification: str = Field(description="Why is this product selected against this report")
        applicable_qws: str = Field(description="list of applicable quick win items and their best practice item covered by this specific product")
        

    parser = JsonOutputParser(pydantic_object=SparkCCLProducts)

    #get prompt input data
    #read json
    json_file_path = 'sparkccl_products_services.json'
    with open(json_file_path) as json_file:
            ccl_json_data = json.load(json_file)
    
    #read json
    json_file_path = 'tmp/json/top_10_quick_wins.json'
    with open(json_file_path) as json_file:
            qw_json_data = json.load(json_file)

    #prompt template
    PROMPT_TEMPLATE_TEXT = """
    We are CCL, an AWS Consultancy. We have the following products:{SparkCCL_products}. \n
    Please consider the customer WAFR quick wins report: \n{input_json} and suggest as many suitabale CCL products as possible. 
    \n{format_instructions}
    """

    prompt = PromptTemplate(
        template = PROMPT_TEMPLATE_TEXT,
        input_variables=["input_json","SparkCCL_products"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser

    sparkccl_product_mapping_json = chain.invoke({"input_json": str(qw_json_data), "SparkCCL_products": str(ccl_json_data)})
    
    #save json file
    file_path = "tmp/json/sparkccl_product_mapping.json"
    save_json_to_file(sparkccl_product_mapping_json, file_path)
    print("spark products mapped and saved to json")
    return(sparkccl_product_mapping_json)

#### Generate conclusion
    #To do



# if __name__ == "__main__":
#     #nada
#     print("yo wassup")
