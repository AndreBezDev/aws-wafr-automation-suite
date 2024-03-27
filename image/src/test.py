from dotenv import load_dotenv, dotenv_values
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
print(os.getenv("HOST"))

num_remediation_pts = 10

# Insert QW Remediation sections
for i in range(num_remediation_pts):
    print(i)