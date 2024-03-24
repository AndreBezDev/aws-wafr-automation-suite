#third-party imports
import boto3
from docx.api import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import matplotlib.pyplot as plt

#system imports
from io import BytesIO
import json
from datetime import datetime

#local/user imports
from wafr_tool_api import fetch_wafr_questions
from document_wrangler import initialise_docs

#Class Definitions
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)







# Define workload params - To Do: pull from incoming Request POST 
workload_id = '66658f2b4909462a1bc9a50349bcaec7' #To Do - fetch appropriate id from API
lens_alias = 'arn:aws:wellarchitected::aws:lens/wellarchitected'
milestone_number = 1 #normally 1

# Define s3 artefact params - To Do enable selection of templates 
input_bucket = 'aws-wafr-automation-base-templates'
input_key = 'CCL-2024/CCL AWS WAFR - Report Template v0.1.docx'
output_bucket = 'aws-wafr-automation-output-reports'  # Replace with your output bucket name
customer_folder = 'KMD'  # Specify customer-specific folder name

if __name__ == "__main__":
    fetch_wafr_questions(workload_id,lens_alias, milestone_number)
    initialise_docs(input_bucket, input_key, output_bucket, customer_folder)