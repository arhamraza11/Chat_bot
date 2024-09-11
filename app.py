import json
import requests
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

class DoctorChatBot:
    def __init__(self):
        self.mistral_client = MistralClient(api_key='uAyQH2qjnN5Batgf1YDp24KB3BLKLHBK')
        self.model = "open-mistral-7b"
        self.message_history = []
        self.user_context = {}
        self.claim_data = {}
        self.claim_stage = None

    def get_llm_response(self, prompt, context=""):
        """Get response from the LLM based on the prompt and context."""
        self.message_history.append(ChatMessage(role="user", content=prompt))
        chat_response = self.mistral_client.chat(
            model=self.model,
            messages=[ChatMessage(role="system", content=context), *self.message_history]
        )
        response_content = chat_response.choices[0].message.content
        self.message_history.append(ChatMessage(role="assistant", content=response_content))
        return response_content.strip()

    def fetch_user_info(self, phone_number):
        """Fetch user info from the API based on phone number."""
        url = f"https://dev.nayacms.com/api/v1/beneficiary/employee-details?contact_no={phone_number}"
        response = requests.get(url)
        return response.json()

    def process_input(self, user_input, phone_number="0312-1758206"):
        """Process user input, validate for claim creation, or handle general queries."""
        #user_info = self.fetch_user_info(phone_number)
        user_info_context = {
                            "id": 87157,
                            "cnic": "4240135849851",
                            "name": "MUHAMMAD ZUBAIR",
                            "contact_no": "0312-1758206",
                            "email": "null",
                            "designation": "Orderbooker",
                            "date_of_birth": "1992-01-17",
                            "policies": [
                                {
                                    "id": 268140,
                                    "start_date": "2024-06-01",
                                    "expiry_date": "2025-05-31",
                                    "available_limit": 24000,
                                    "policy_type_id": 1
                                },
                                {
                                    "id": 268141,
                                    "start_date": "2024-06-01",
                                    "expiry_date": "2025-05-31",
                                    "available_limit": 300000,
                                    "policy_type_id": 2
                                }
                            ],
                            "dependents": [
                                {
                                    "id": 221198,
                                    "name": "SHAZIA WAHID",
                                    "date_of_birth": "1988-03-24",
                                    "relationship_master_id": 5
                                }
                            ],
                            "claims": [
                                {
                                    "id": 43462490,
                                    "policy_id": 268140,
                                    "amount_claimed": 1000,
                                    "is_opd_claim": 1,
                                    "status": {
                                        "id": 43451291,
                                        "status_master_code": 0,
                                        "master": {
                                            "name": "Pending For Checker"
                                        }
                                    }
                                }
                            ]
                        }


        # Handle greetings
        

        # Check if the user wants to create a claim
        if "claim" in user_input.lower() and "make" in user_input.lower():
            if not self.claim_stage:
                self.claim_stage = "start"
                return "Let's start the claim process. Please provide the following details:\n- Claim Type\n- Claim Request For\n- Total Requested Amount\n- Date of Intimation\n- Consultancy Charges\n- Medicine Charges\n- Lab Charges\n- Description\n- Attachments (if any)"
            else:
                # Collecting claim information
                return self.collect_claim_info(user_input)

        # Handle other queries
        prompt = (f"you must respond in raw html with <br> as line breaker,strictly adhere to this rule.You are an assistant for employee benefits and claims. You should only display user-friendly information. "
                  f"Respond to the user query based on the provided context.Dont include id and any non user friendly things in your responses.if the user ask for personal information like tell me about myself or something about his policy so tell him using the context i provided ."
                  f"Your Responses should be always in points and not a paragraph so user can understand it in a nice way.Regards should always be from DoctHers Bot.\n\n"
                  f"provided context.\n\nContext:\n{user_info_context}\n\nUser Query:\n{user_input}" 
                  f"lastly dont just tell the whole context use your own knowledge to analyze the user question first such as if user ask about himself try to just give a precise and nice response."
                  )
        return self.get_llm_response(prompt)

    def collect_claim_info(self, user_input):
        """Collect claim information from the user."""
        if self.claim_stage == "start":
            self.claim_data = {field: None for field in [
                "Claim Type", "Claim Request For", "Total Requested Amount", "Date of Intimation", 
                "Consultancy Charges", "Medicine Charges", "Lab Charges", "Description", "Attachments (if any)"
            ]}
            self.claim_stage = "collecting"
            return f"Please provide the details for each field: {list(self.claim_data.keys())}"

        # Assume user_input is in JSON format for simplicity; adjust based on actual input format
        try:
            user_claim_info = json.loads(user_input)
            self.claim_data.update(user_claim_info)
            return self.confirm_claim()
        except json.JSONDecodeError:
            return "There was an error processing the claim information. Please provide details in JSON format."

    def confirm_claim(self):
        """Ask for confirmation before submitting the claim."""
        confirmation_message = f"Here are the claim details:\n{json.dumps(self.claim_data, indent=2)}\n\nDo you confirm these details? Reply with 'yes' to confirm or 'no' to start over."
        self.claim_stage = "confirming"
        return confirmation_message

    def save_claim(self):
        """Submit the claim to the API if confirmed."""
        url = "https://dev.nayacms.com/api/v1/beneficiary/save-claim"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json.dumps(self.claim_data), headers=headers)
        return f"Claim saved successfully: {json.dumps(response.json(), indent=2)}"

bot = DoctorChatBot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"message": "No message received"}), 400

    response_message = bot.process_input(user_message)
    print(response_message)
   # formatted_response = response_message.replace('/c', '<br>')
    return jsonify({"message": response_message})

if __name__ == '__main__':
    app.run(host="173.208.167.7",debug=True,port=5000)
