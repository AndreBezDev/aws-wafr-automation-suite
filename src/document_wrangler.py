#third-party imports
import boto3
from botocore.exceptions import NoCredentialsError
from docx.api import Document
from docx.shared import Pt
from docx.shared import RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.table import WD_ALIGN_VERTICAL
import matplotlib.pyplot as plt

#system imports
from io import BytesIO
import json
from datetime import datetime

#local/user imports


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

    #initialise S3 client
    s3 = boto3.client('s3')

    copy_source = {'Bucket': input_bucket, 'Key': input_key}
    output_key = f'{customer_folder}/CCL_WAFR_Report.docx'  # Adjust the output key as needed
    s3.copy_object(CopySource=copy_source, Bucket=output_bucket, Key=output_key)

    print(f"Template copied successfully to {output_bucket}/{output_key}")

# Function to download wip doc into container runtime
def download_docx_from_s3(bucket_name, key, local_path):
    #initialise S3 client
    s3 = boto3.client('s3')

    # Download the document from S3
    s3.download_file(bucket_name, key, local_path)

    #stored in container filesystem - no external volumes / mnt
    print(f"Document downloaded from S3 to {local_path}")


#store file in s3
def upload_to_s3(file_path, bucket_name, object_name):
    """
    Upload a file to an S3 bucket

    :param file_path: Path to the file to upload
    :param bucket_name: S3 bucket name
    :param object_name: S3 object name (key)
    :return: True if the file was uploaded successfully, else False
    """

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file to S3
        s3_client.upload_file(file_path, bucket_name, object_name)
    except FileNotFoundError:
        print(f"The file '{file_path}' was not found.")
        return False
    except NoCredentialsError:
        print("AWS credentials not available.")
        return False
    
    print(f"File uploaded successfully to S3 bucket '{bucket_name}' with key '{object_name}'")
    return True


# Point to a JSON file and convert to usable table in word
def json_to_word_table(json_data, doc, doc_path):

    # Create a new Word document
    doc = Document(doc_path)

    # Iterate over each key-value pair in the JSON data
    for key, value in json_data.items():
        # Add key as a heading to the document
        doc.add_heading(key.capitalize(), level=1)

        # Create a table with two columns: Key and Value
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Key'
        hdr_cells[1].text = 'Value'

        # Function to recursively add rows for nested dictionaries
        def add_rows(data, table):
            for k, v in data.items():
                if isinstance(v, dict):
                    # If the value is a dictionary, add a row with the key and 'Dict'
                    row_cells = table.add_row().cells
                    row_cells[0].text = k
                    row_cells[1].text = 'Dict'
                    # Recursively add rows for the nested dictionary
                    add_rows(v, table)
                elif isinstance(v, list):
                    # If the value is a list, add a row with the key and 'List'
                    row_cells = table.add_row().cells
                    row_cells[0].text = k
                    row_cells[1].text = 'List'
                    # Iterate over each element in the list
                    for item in v:
                        # Add a row for each element
                        row_cells = table.add_row().cells
                        row_cells[0].text = ''
                        row_cells[1].text = str(item)
                else:
                    # For other types, add a row with the key and the value
                    row_cells = table.add_row().cells
                    row_cells[0].text = k
                    row_cells[1].text = str(v)

        # Call the add_rows function to populate the table
        add_rows(value, table)

    # Save the document
    doc.save(doc_path)
    


# Function to create a Word document with a heading and a table
def modify_word_document(local_path):
        
    # Create a new Word document
    doc = Document(f'{local_path}')

    # Add a heading "WAFR Risk Breakdown"
    doc.add_heading('WAFR Risk Breakdown Yeehoooowsa', level=1)

    # Save the document
    doc.save(f'{local_path}')
    print(f"Document modified at {local_path}")


#test func
def json_to_flat_table(json_data, doc, doc_path):
    """
    Convert JSON data to a flat table in a Word document.

    :param json_data: JSON data to convert to a flat table.
    :param doc: Word document object to write the table to.
    :param doc_path: Path to save the Word document.
    """
    # Create a table with number of rows as the length of the JSON data
    table = doc.add_table(rows=1, cols=len(json_data) + 1)
    table.style = 'Table Grid'

    # Add column headers
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Question'
    for idx, key in enumerate(json_data.keys()):
        header_cells[idx + 1].text = key

    # Add data to the table
    for row_idx, (question, values) in enumerate(json_data.items()):
        cells = table.add_row().cells
        cells[0].text = question
        for col_idx, (header, value) in enumerate(values.items()):
            cells[col_idx + 1].text = str(value)

    # Save the document
    doc.save(doc_path)

#test func2
    
def json_to_table2(json_data, doc, doc_path):
    """
    Convert JSON data to a table in a Word document with vertical cell merging and separated best practice choices.

    :param json_data: JSON data to convert to a table.
    :param doc: Word document object to write the table to.
    :param doc_path: Path to save the Word document.
    """
    # Initialize the table
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'

    #pillar mapping
    pillar_mapping = {
        "operationalExcellence": "Operational Excellence",
        "security": "Security",
        "reliability": "Reliability",
        "performance": "Performance Efficiency",
        "costOptimization": "Cost Optimisation",
        "sustainability": "Sustainability"
    }

    # Add column headers
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Pillar Name'
    header_cells[1].text = 'Question Title'
    header_cells[2].text = 'Best Practice Choice'

    merge_ranges = {}

    for pillar, questions in json_data.items():
        for question, details in questions.items():
            # Find the start and end row index for the current cell
            start_row_index = len(table.rows)
            for choice in details.get("UnselectedChoices", []):
                cells = table.add_row().cells
                cells[0].text = pillar
                cells[1].text = question
                cells[2].text = choice
            
            end_row_index = len(table.rows)
            
            # Update merge ranges dictionary
            key = (pillar, question)
            if key in merge_ranges:
                merge_ranges[key] = (min(merge_ranges[key][0], start_row_index), max(merge_ranges[key][1], end_row_index))
            else:
                merge_ranges[key] = (start_row_index, end_row_index)

    # Merge cells vertically for each unique value
    for key, (start_row, end_row) in merge_ranges.items():
    # Replace the incorrect pillar name with the correct one
        pillar = key[0]
        correct_pillar = pillar_mapping.get(pillar, pillar)
        question = key[1]
        for col in range(2):  # Merge only first two columns
            start_cell = table.cell(start_row, col)
            end_cell = table.cell(end_row - 1, col)  # Subtract 1 to get the last cell
            start_text = start_cell.text
            # Replace the pillar name with the correct one
            start_text = start_text.replace(pillar, correct_pillar)
            start_cell.merge(end_cell)
            merged_cell = table.cell(start_row, col)  # Use start row for the merged cell
            merged_cell.text = start_text  # Set the text of the merged cell to the start cell's text

    # Set vertical alignment for all cells
    for row in table.rows:
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Save the document
    doc.save(doc_path)

def initialise_docs(inputBucket, inputKey, outputBucket,customerFoler):
    #initialise clients
    s3 = boto3.client('s3')

     #config vars
    input_bucket = inputBucket
    input_key = inputKey
    output_bucket = outputBucket  # Replace with your output bucket name
    customer_folder = customerFoler  # Specify customer-specific folder name
    
    # Copy the template to the output bucket under the customer-specific folder
    copy_template_to_output_bucket(input_bucket, input_key, output_bucket, customer_folder)
    
    # Specify S3 bucket details and local file path
    bucket_name = f'{output_bucket}'  # Replace with your S3 bucket name
    key = f'{customer_folder}/CCL_WAFR_Report.docx'      # Replace with the key of the document in your S3 bucket
    local_path = 'tmp/wip_document.docx' # Specify the local file path where the document will be saved

    # Download the document from S3
    download_docx_from_s3(bucket_name, key, local_path)

    # Open Doc for WIP
    doc = Document(f'{local_path}')

    #choose JSON file to convert to table
    # Load the JSON data
    json_file_path = 'tmp/json/filter_high_risk_questions.json'
    with open(json_file_path) as json_file:
        json_data = json.load(json_file)
    doc_path = f'{local_path}'
    #json_to_word_table(json_data, doc, doc_path)
    json_to_table2(json_data, doc, doc_path)
    #json_to_flat_table(json_data, doc, doc_path)

    #store WIP doc in S3
    upload_to_s3(local_path, bucket_name, key)


    # Modify the Word document
    #modify_word_document(local_path)

    # # Generate the bar chart
    # generate_bar_chart()

    # print("Word document and bar chart generated successfully.")

