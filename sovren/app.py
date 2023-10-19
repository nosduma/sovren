import os
import base64
import requests
import json
import datetime

# Function to generate a resume summary from the response data
def generate_resume_summary(resume_data):
    # Implement your logic to generate a summary here
    # You can modify this function to format the summary as you like
    # For example, you can concatenate relevant fields from the resume data
    summary = f"Name: {resume_data.get('ContactInformation', {}).get('CandidateName', {}).get('FormattedName', 'N/A')}\n"
    summary += f"Phone: {', '.join(phone['Raw'] for phone in resume_data.get('ContactInformation', {}).get('Telephones', []))}\n"
    summary += f"Email: {', '.join(resume_data.get('ContactInformation', {}).get('EmailAddresses', []))}\n"
    # Add more fields as needed
    return summary

# Define the required education and experience
required_education = "Information and Communication Technology"  # Modify as needed
required_experience = "service desk consultant"  # Modify as needed

# Specify the directory path containing resume files
directory_path = "resumes"

# Initialize variables to keep track of the best candidate and score
best_candidate = None
best_score = 0  # You can set an initial score, or use a different value depending on your scoring logic

# Iterate through the files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(('.docx', '.pdf')):
        # Construct the full file path
        file_path = os.path.join(directory_path, filename)

        # Encode the resume file as base64
        with open(file_path, 'rb') as f:
            base64str = base64.b64encode(f.read()).decode('UTF-8')

        # Get the last modified date of the file
        epoch_seconds = os.path.getmtime(file_path)
        last_modified_date = datetime.datetime.fromtimestamp(epoch_seconds).strftime("%Y-%m-%d")

        # Define the API endpoint URL based on your account data center
        # Use https://eu-rest.resumeparsing.com/v10/parser/resume if your account is in the EU data center
        # Use https://au-rest.resumeparsing.com/v10/parser/resume if your account is in the AU data center
        url = "https://rest.resumeparsing.com/v10/parser/resume"

        payload = {
            'DocumentAsBase64String': base64str,
            'DocumentLastModified': last_modified_date,
            # Other options here (see https://sovren.com/technical-specs/latest/rest-api/resume-parser/api/)
        }

        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'sovren-accountid': "41332881",  # Replace with your Sovren account ID
            'sovren-servicekey': "6I3Fp3yQF1EFqOyvjL7N6DAPrvaQ8r3wds34uKYe",  # Replace with your Sovren API key
        }

        # Make the request to the Sovren API
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            try:
                response_json = json.loads(response.content)
                # Extract the resume data from the API response
                resume_data = response_json.get('Value', {}).get('ResumeData', {})

                # Check if EducationDetails exist in the resume data
                education_details = resume_data.get('Education', {}).get('EducationDetails', [])
                relevant_experience = any(
                    required_experience.lower() in position.get('Description', '').lower()
                    for position in resume_data.get('EmploymentHistory', {}).get('Positions', [])
                )

                # Check if the education and experience criteria match
                if any(
                    required_education.lower() in ed.get('Education', {}).get('Name', '').lower()
                    for ed in education_details
                ) and relevant_experience:

                    candidate_score = 2  # Both criteria met
                elif any(
                    required_education.lower() in ed.get('Education', {}).get('Name', '').lower()
                    for ed in education_details
                ) or relevant_experience:

                    candidate_score = 1  # One of the criteria met
                else:
                    candidate_score = 0  # Neither criteria met

                # Update the best candidate if necessary
                if candidate_score > best_score:
                    best_candidate = generate_resume_summary(resume_data)
                    best_score = candidate_score

            except json.JSONDecodeError as e:
                print(f"Error parsing the response: {e}")
        else:
            print(f"Error: {response.status_code}, {response.text}")

# Print the best candidate's summary
if best_candidate:
    print("Best Candidate:")
    print(best_candidate)
else:
    print("No candidate met the criteria")
