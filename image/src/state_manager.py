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


# # Define workload params - To Do: pull from incoming Request POST 
# workload_id = 'bcc6bf1d68218b99986acca5ffb711f7' #To Do - fetch appropriate id from API
# lens_alias = 'arn:aws:wellarchitected::aws:lens/wellarchitected'
# milestone_number = 1 #normally 1

# # Define s3 artefact params - To Do enable selection of templates 
# input_bucket = 'aws-wafr-automation-base-templates'
# input_key = 'CCL-2024/CCL AWS WAFR - Report Template v0.1.docx'
# output_bucket = 'aws-wafr-automation-output-reports' 
# customer_folder = 'Test'  # Specify customer-specific folder name

def get_wafr_report(workload_id, milestone_number, customer):
    #hard coded consts
    lens_alias = 'arn:aws:wellarchitected::aws:lens/wellarchitected'
    input_bucket = 'aws-wafr-automation-base-templates' #bucket for input cust Word template
    input_key = 'CCL-2024/CCL AWS WAFR - Report Template v0.1.docx' #s3 path to cust template
    output_bucket = 'aws-wafr-automation-output-reports'  # default output bucket location

    #fetch params from api: workload_id, milestone_number, customer_folder
    fetch_wafr_questions(workload_id,lens_alias, milestone_number)
    initialise_docs(input_bucket, input_key, output_bucket, customer)

    #return downloadlink (presigned URL)
# if __name__ == "__main__":
#     get_wafr_report(workload_id, milestone_number, customer_folder)