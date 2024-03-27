#third-party imports
from fastapi import FastAPI, BackgroundTasks
from mangum import Mangum

#system imports
from io import BytesIO
import json
from datetime import datetime

#local/user imports
from docx_helper_functions import add_empty_line, add_heading, add_page_break, add_paragraph, add_subheading
from gpt_magic import quick_wins_section_prep
from state_manager import get_wafr_report

#Class Definitions


app = FastAPI()
handler = Mangum(app)



@app.get('/')
async def hello():
    return {
        "message": "Hello from WAFR Bot"
    }


#127.0.0.1:8000/getWafrReport?workload_id=bcc6bf1d68218b99986acca5ffb711f7&milestone_number=1&customer=Test
# @app.get('/getWafrReport')
# async def getWafrReport(workload_id, milestone_number:int, customer): #add llm as param
#     await get_wafr_report(workload_id, milestone_number, customer)
#     return {
#         "message": "WAFR report generated - here's your download link: (to-do)"
#     }

@app.get('/getWafrReport')
async def getWafrReport_background(workload_id, milestone_number:int, customer, background_tasks: BackgroundTasks): #add llm as param
    background_tasks.add_task(get_wafr_report, workload_id, milestone_number, customer)
    return {
        "message": "WAFR report generation started - check S3 in about 2 mins Lol, async innit"
    }

#uvicorn main:app --reload

#use backgroundTasks to bypass async conditions for FastAPI. Otherwise EventLoop, await, asyncio, async...not fun