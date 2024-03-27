import boto3
import json
from datetime import datetime

# Class Definitions
# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

client = boto3.client(service_name='wellarchitected', region_name="ap-southeast-2")


# def get_report():
    # response_list_workloads = client.list_workloads(
    #     #Params
    # )
            
    # response_consolidated_report = client.get_consolidated_report(
    #     Format='JSON',
    #     IncludeSharedResources=True,
    # )

    # response_get_lens_report = client.get_lens_review_report(
    #     WorkloadId='f54f24c187bd00731cbab8b1532fff59',
    #     LensAlias='arn:aws:wellarchitected::aws:lens/wellarchitected', #lens ARN
    #     MilestoneNumber=1 #starts at 1
    # )

    # response_get_lens_review = client.get_lens_review(
    #     WorkloadId='f54f24c187bd00731cbab8b1532fff59',
    #     LensAlias='arn:aws:wellarchitected::aws:lens/wellarchitected',
    #     MilestoneNumber=1
    # )
    
    # return response_get_lens_review

# Export JSON file for troubleshooting / inspection
# def json_dump(response_name):
#     with open(f'{response_name}_response_output.json', 'w') as f:
#         json.dump(response_name, f, cls=DateTimeEncoder)


# Extract Answers from Workload (Formatting of Questions included)
def extract_answers_items(workload_id, lens_alias, milestone_number):
    pillar_ids = ['operationalExcellence', 'security', 'reliability', 'performance', 'costOptimization', 'sustainability']
    pillar_short_codes = ['OPS', 'SEC', 'REL', 'PERF', 'COST', 'SUS']

    # Initialize an empty dictionary to store extracted data for each pillar
    extracted_data_by_pillar = {}

    for pillar_id, pillar_short_code in zip(pillar_ids, pillar_short_codes):
        response_answers_pillar = client.list_answers(
            WorkloadId=workload_id,
            LensAlias=lens_alias,
            PillarId=pillar_id,
            MilestoneNumber=milestone_number,
        )

        # Initialize an empty dictionary to store the extracted information for this pillar
        extracted_data = {}

        # Initialize a counter for numbering the questions
        question_number = 1

        # Iterate over each question in the AnswerSummaries
        for answer_summary in response_answers_pillar["AnswerSummaries"]:
            # Extract the question title
            question_title = f"{pillar_short_code} {question_number}. {answer_summary['QuestionTitle']}"
            
            # Initialize an empty list to store unselected choices
            unselected_choices = []
            
            # Iterate over each choice for the question
            for choice in answer_summary["Choices"]:
                # Check if the choice is not in the list of selected choices
                if choice["ChoiceId"] not in answer_summary["SelectedChoices"]:
                    if choice["Title"] != "None of these":
                        # Append the title of the unselected choice to the list
                        unselected_choices.append(choice["Title"])
            
            # Extract the risk value
            risk = answer_summary["Risk"]
            
            # Store the extracted information in the dictionary
            extracted_data[question_title] = {
                "UnselectedChoices": unselected_choices,
                "Risk": risk
            }

            # Increment the question number
            question_number += 1
        
        # Store the extracted data for this pillar in the dictionary of extracted data by pillar
        extracted_data_by_pillar[pillar_id] = extracted_data
    
    with open('/tmp/pillar_answers.json', 'w') as f:
        json.dump(extracted_data_by_pillar, f, cls=DateTimeEncoder)

    return extracted_data_by_pillar
    


# Filter out HRIs into Py Struct
def filter_high_risk_questions(extracted_data_by_pillar):
    filtered_data_by_pillar = {}

    for pillar_id, extracted_data in extracted_data_by_pillar.items():
        filtered_data = {}

        for question_title, info in extracted_data.items():
            if info["Risk"] == "HIGH":
                filtered_data[question_title] = info

        if filtered_data:
            filtered_data_by_pillar[pillar_id] = filtered_data

    with open('/tmp/filter_high_risk_questions.json', 'w') as f:
        json.dump(filtered_data_by_pillar, f, cls=DateTimeEncoder)
    return filtered_data_by_pillar 

# Filter out MRIs into Py Struct
def filter_medium_risk_questions(extracted_data_by_pillar):
    filtered_data_by_pillar = {}

    for pillar_id, extracted_data in extracted_data_by_pillar.items():
        filtered_data = {}

        for question_title, info in extracted_data.items():
            if info["Risk"] == "MEDIUM":
                filtered_data[question_title] = info

        if filtered_data:
            filtered_data_by_pillar[pillar_id] = filtered_data

    with open('/tmp/filter_medium_risk_questions.json', 'w') as f:
        json.dump(filtered_data_by_pillar, f, cls=DateTimeEncoder)
    return filtered_data_by_pillar 


# Extract Risk Metrics into Dict (Combined HRI and MRIs)
def extract_risk_table_items(workload_id, lens_alias,milestone_number):
    
    #Get correct workload and lens from WA Tool API
    response_get_lens_review = client.get_lens_review(
        WorkloadId= workload_id,
        LensAlias= lens_alias,
        MilestoneNumber=milestone_number
    )

    # Build Pillar Risk Metrics Dict
    pillars_risk_dict = [] #Risk dictionary
    for pillar_num in range(1, 7):  # Pillar numbers range from 1 to 6
        pillar_name = response_get_lens_review["LensReview"]["PillarReviewSummaries"][pillar_num - 1]["PillarName"]
        risk_counts = response_get_lens_review["LensReview"]["PillarReviewSummaries"][pillar_num - 1]["RiskCounts"]
        pillar_metrics = {
            "Name": pillar_name,
            "Unanswered": risk_counts.get("UNANSWERED", None),
            "High": risk_counts.get("HIGH", None),
            "Medium": risk_counts.get("MEDIUM", None),
            "None": risk_counts.get("NONE", None),
            "NotApplicable": risk_counts.get("NOT_APPLICABLE", None)
        }
        pillars_risk_dict.append(pillar_metrics) #pillar = pillars_risk_dict[0] #hri_count = pillar['High']
    with open('/tmp/risk_metrics.json', 'w') as f:
        json.dump(pillars_risk_dict, f, cls=DateTimeEncoder)
    return pillars_risk_dict
   
########################################
#__main__

def fetch_wafr_questions(workloadId, lensAlias, milestoneNumber):
    #Review Selection defaults - incase custom overrides / testing

    #Note: questions are being chopped off at 10 per pillar - need to consider pag
    workload_id = workloadId
    lens_alias = lensAlias
    milestone_number = milestoneNumber

    extract_risk_table_items(workload_id, lens_alias,milestone_number)
    extracted_data_by_pillar = extract_answers_items(workload_id, lens_alias,milestone_number)
    filter_high_risk_questions(extracted_data_by_pillar)
    filter_medium_risk_questions(extracted_data_by_pillar)

    print("WAFR Workload pulled - Questions extracted, HRI and MRI filters extracted")