import base64
import requests
import json
import os
import datetime

# Define the desired skill and minimum experience years
desired_skill = "software developer"  # Adjust as needed (make sure it matches the skill name in resumes)
min_experience_years = 1  # Adjust as needed

# Function to extract skills from text
def extract_skills(text):
    # Define a list of common skills (you can expand this list)
    common_skills = ["java", "python", "javascript", "html", "css", "sql", "c++", "php"]

    # Extract skills by matching keywords
    extracted_skills = [skill for skill in common_skills if skill.lower() in text.lower()]

    return extracted_skills

# Option 2: Process all resume files in a directory
resume_directory = 'resumes'

# Get a list of all files in the directory if Option 2 is chosen
if os.path.isdir(resume_directory):
    resume_files = os.listdir(resume_directory)
else:
    print("No resume files found in the specified directory.")
    exit(1)

# Flag to check if a candidate with the desired skill is found
skill_found = False

# Iterate through each resume file
for resume_file in resume_files:
    # Construct the full path to the resume file
    file_path = os.path.join(resume_directory, resume_file)

    base64str = ''

    # Open the file, encode the bytes to base64, then decode that to a UTF-8 string
    with open(file_path, 'rb') as f:
        base64str = base64.b64encode(f.read()).decode('UTF-8')

    epochSeconds = os.path.getmtime(file_path)
    lastModifiedDate = datetime.datetime.fromtimestamp(epochSeconds).strftime("%Y-%m-%d")

    # Use https://eu-rest.resumeparsing.com/v10/parser/resume if your account is in the EU data center or
    # Use https://au-rest.resumeparsing.com/v10/parser/resume if your account is in the AU data center
    url = "https://rest.resumeparsing.com/v10/parser/resume"
    payload = {
        'DocumentAsBase64String': base64str,
        'DocumentLastModified': lastModifiedDate
        # Other options here (see https://sovren.com/technical-specs/latest/rest-api/resume-parser/api/)
    }

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'sovren-accountid': "41332881",
        'sovren-servicekey': "6I3Fp3yQF1EFqOyvjL7N6DAPrvaQ8r3wds34uKYe",
    }

    # Make the request, NOTE: the payload must be serialized to a JSON string
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        try:
            responseJson = json.loads(response.content)
            # Now, you can access the JSON data
            resumeData = responseJson.get('Value', {}).get('ResumeData', {})

            # Read the content of the resume file with 'ISO-8859-1' encoding
            with open(file_path, 'rb') as f:
                resume_text = f.read().decode('ISO-8859-1')

            # Extract candidate skills from the text
            candidate_skills = extract_skills(resume_text)

            # Check if the candidate has the desired skill (case-insensitive comparison)
            if desired_skill.lower() in [skill.lower() for skill in candidate_skills]:
                skill_found = True

                # Calculate the candidate's experience years based on resumeData
                # You need to implement logic to calculate experience years based on the resumeData
                # For example, you can calculate the difference between the current year and the start year of relevant work experience.
                # This is a simplified example and may not work for all scenarios.
                experience_years = 0
                work_experiences = resumeData.get('WorkExperience', [])
                current_year = datetime.datetime.now().year
                for experience in work_experiences:
                    start_date = experience.get('StartDate')
                    if start_date:
                        start_year = int(start_date.split('-')[0])
                        experience_years += current_year - start_year

                # Print the candidate's information
                print(f"Candidate with desired skill ({desired_skill}) found in {resume_file}:")
                print(f"Skills: {', '.join(candidate_skills)}")
                print(f"Experience Years: {experience_years}")

        except json.JSONDecodeError:
            print(f"Error processing {resume_file}: Unable to decode JSON response")
    else:
        print(f"Error processing {resume_file}: API request failed with status code {response.status_code}")

# Print the result based on whether a candidate with the desired skill was found
if not skill_found:
    print(f"No candidates with the desired skill ({desired_skill}) were found.")
