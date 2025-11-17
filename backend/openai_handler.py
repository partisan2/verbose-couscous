"""Run this model in Python

> pip install openai
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings. 
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)

def list_products(msg):
    return "We have a wide range of products including electronics, clothing, and home goods. What are you interested in?"

def product_info(msg):
    return "Please specify the product you want information about."

def pricing(msg):
    return "Could you please tell me which product's pricing you would like to know?"

def order_status(msg):
    return "Please provide your order number so I can check the status for you."

def return_policy(msg):
    return "Our return policy allows returns within 30 days of purchase with a receipt."

def product_recommendations(msg):
    return "What type of products are you interested in? I can suggest some options for you."

def other(msg):
    return "I'm here to help with any questions you have. Please let me know how I can assist you."

def get_intent_and_response(message):

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(word.lower() in message.lower() for word in greetings):
        return "Hello! How can I help you today?"

    prompt = f"""
    You are a sales assistant that helps customers.
    Your job is to classify the user's message into one of the following intents and generate a short helpful response.
    Identify the user's intent from: ["list_products", "product_info", "pricing", "order_status", "return_policy", "product_recommendations","other"].
    Return only the intent.
    User's message: "{message}"
    """

    intent_response = client.chat.completions.create(
        model="openai/gpt-4o",
        temperature=1,
        max_tokens=4096,
        top_p=1,
        messages=[{"role":"user","content":prompt}]

    )
    intent = intent_response.choices[0].message.content.strip()

    intent_handlers = {
        "list_products": list_products,
        "product_info": product_info,
        "pricing": pricing,
        "order_status": order_status,
        "return_policy": return_policy,
        "product_recommendations": product_recommendations,
        "other": other
    }

    handler = intent_handlers.get(intent, other)

    return handler(message)



# response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "",
#         },
#         {
#             "role": "user",
#             "content": "What is the capital of France?",
#         }
#     ],
#     model="openai/gpt-4o",
#     temperature=1,
#     max_tokens=4096,
#     top_p=1
# )

# print(response.choices[0].message.content)
