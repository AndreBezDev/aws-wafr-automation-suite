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
from wafr_tool_api import extracted_data_by_pillar, filter_high_risk_questions, filter_medium_risk_questions

#Class Definitions
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


###Workflow
# Copy template to customer folder
# then edit the customer one
# Pull in AWS WAFR Report - extract data

# Function to create customer copy from base template
def copy_template_to_output_bucket(input_bucket, input_key, output_bucket, customer_folder):
    #To Do - create distinct files everytime
    copy_source = {'Bucket': input_bucket, 'Key': input_key}
    output_key = f'{customer_folder}/CCL_WAFR_Report.docx'  # Adjust the output key as needed
    s3.copy_object(CopySource=copy_source, Bucket=output_bucket, Key=output_key)

    print(f"Template copied successfully to {output_bucket}/{output_key}")

# Function to download wip doc into container runtime
def download_docx_from_s3(bucket_name, key, local_path):
    # Download the document from S3
    s3.download_file(bucket_name, key, local_path)

    #stored in container filesystem - no external volumes / mnt
    print(f"Document downloaded from S3 to {local_path}")


# Function to create a Word document with a heading and a table
def modify_word_document():
    #trigger wafr extraction
    filtered_data = filter_high_risk_questions(extracted_data_by_pillar)
    
    # Create a new Word document
    doc = Document(f'{local_path}')

    # Add a heading "WAFR Risk Breakdown"
    doc.add_heading('WAFR Risk Breakdown Yeehaw', level=1)

    # Save the document
    doc.save(f'{local_path}')
    print(f"Document modified at {local_path}")


if __name__ == "__main__":
    #initialise clients
    s3 = boto3.client('s3')

     #config vars
    input_bucket = 'aws-wafr-automation-base-templates'
    input_key = 'CCL-2024/CCL AWS WAFR - Report Template v0.1.docx'
    output_bucket = 'aws-wafr-automation-output-reports'  # Replace with your output bucket name
    customer_folder = 'CCL'  # Specify customer-specific folder name
    
    # Copy the template to the output bucket under the customer-specific folder
    copy_template_to_output_bucket(input_bucket, input_key, output_bucket, customer_folder)
    
    # Specify S3 bucket details and local file path
    bucket_name = f'{output_bucket}'  # Replace with your S3 bucket name
    key = f'{customer_folder}/CCL_WAFR_Report.docx'      # Replace with the key of the document in your S3 bucket
    local_path = 'tmp/wip_document.docx' # Specify the local file path where the document will be saved

    # Download the document from S3
    download_docx_from_s3(bucket_name, key, local_path)


    # Modify the Word document
    modify_word_document()

    # # Generate the bar chart
    # generate_bar_chart()

    # print("Word document and bar chart generated successfully.")