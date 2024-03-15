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

#Class Definitions
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)







# Define workload params - To Do: pull from incoming Request POST 
workload_id = 'f54f24c187bd00731cbab8b1532fff59' #To Do - fetch appropriate id from API
lens_alias = 'arn:aws:wellarchitected::aws:lens/wellarchitected'
milestone_number = 2 #normally 1

if __name__ == "__main__":
    fetch_wafr_questions(workload_id,lens_alias, milestone_number)