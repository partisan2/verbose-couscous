"""Run this model in Python

> pip install openai
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
from difflib import get_close_matches
from function_handler import build_product_index,convert_list_to_category_dict,product_info,ai_product_recommender
load_dotenv()

# To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings. 
# Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)

import json
from difflib import get_close_matches

selected_intent = None
selected_category = None

def list_products(msg):
    global selected_intent
    selected_intent = "list_products"
    print("----list products-----")
    return "We have Laptops, Smartphones, Audio Devices, Wearables, Cameras, Gaming, Smart Home and Accessories. What category are you interested in?"

def compare_products(msg):
    try:
        # Load products
        with open('./resources/productlists.json', 'r', encoding='utf-8') as file:
            raw = json.load(file)

        data = raw if isinstance(raw, dict) else convert_list_to_category_dict(raw)
        index = build_product_index(data)

        # Normalize message
        text = msg.lower()

        # Detect products mentioned
        found_products = []
        for key, product in index.items():
            if key in text and product not in found_products:
                found_products.append(product)

        # Not enough products?
        if len(found_products) < 2:
            return "Please mention at least **two products** to compare."

        # Ensure all products share the same category
        categories = {p["category"] for p in found_products}
        if len(categories) > 1:
            return "These products are from **different categories**. Comparison requires same category."

        # Build comparison table
        header = "Comparing: " + " | ".join([p["name"] for p in found_products])

        # Common fields
        fields = ["price", "brand", "rating"]
        specs = set()

        # collect all spec keys
        for p in found_products:
            specs.update(p.get("specs", {}).keys())

        # Start response
        response = f"📊 Product Comparison\n{header}\n\n"

        # Compare main fields
        response += "🔹 General Details\n"
        for field in fields:
            row = f"{field.capitalize()}:\n"
            for p in found_products:
                row += f"- {p['name']}: {p.get(field, 'N/A')}\n"
            response += row + "\n"

        # Compare specs
        response += "🔧 Specifications\n"
        for s in specs:
            row = f"{s.capitalize()}:\n"
            for p in found_products:
                val = p.get("specs", {}).get(s, "N/A")
                row += f"- {p['name']}: {val}\n"
            response += row + "\n"

        return response.strip()

    except Exception as e:
        return f"Error in comparing products: {str(e)}"


# def pricing(msg):
#     return "Could you please tell me which product's pricing you would like to know?"

def order_status(msg):
    print("------order status---------") 
    try:
        with open('./resources/orders.json','r',encoding='utf-8') as file:
            raw_data = json.load(file)
            orders = []
            for order in raw_data:
                orderid = order["order_id"]
                orderStatus = order["order_status"]
                if orderStatus == "Shipped" or orderStatus == "Delivered" or orderStatus == "Cancelled":
                    continue
                orderLine = f"Order Details: Id:{orderid}, Status: {orderStatus}"
                orders.append(orderLine)
            return "\n".join(orders)
    except Exception as e:
        return None

    return "Please provide your order number so I can check the status for you."

def return_policy(msg):
    return "Our return policy allows returns within 30 days of purchase with a receipt."

def product_recommendations(msg):
    print("In recommend")
    return ai_product_recommender(msg)

def other(msg):
    return "I'm here to help with any questions you have. Please let me know how I can assist you."

def get_intent_and_response(message):
    global selected_intent
    if selected_intent == None:
        print(selected_intent)
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
        if any(word.lower() in message.lower() for word in greetings):
            return "Hello! How can I help you today?"

        prompt = f"""
        You are a sales assistant that helps customers.
        Your job is to classify the user's message into one of the following intents and generate a short helpful response.
        Identify the user's intent from: ["list_products_question", "product_info", "compare_products", "order_status", "return_policy", "product_recommendations","other"].
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
            "list_products_question": list_products,
            "product_info": product_info,
            "compare_products": compare_products,
            "order_status": order_status,
            "return_policy": return_policy,
            "product_recommendations": product_recommendations,
            "other": other
        }

        handler = intent_handlers.get(intent, other)

        return handler(message)
    
    elif selected_intent == "list_products":
        return productList(message)

def extract_category(message, categories):
    message = message.lower()
    for cat in categories:
        if cat.lower() in message:
            return cat
    return None


def productList(user_msg):
    global selected_intent

    try:
        with open('./resources/productlists.json', 'r') as file:
            data = json.load(file)

        categories = list(data.keys())

        # Auto-detect category from user message
        detected_category = extract_category(user_msg, categories)

        if detected_category is None:
            # No category recognized
            return f"Please select a category: {', '.join(categories)}"

        # Category found
        products = data[detected_category]
        product_names = [p["name"] for p in products]

        selected_intent = None  # reset intent

        return f"Here are the available {detected_category}:\n" + "\n".join(product_names)

    except Exception as e:
        return f"Error loading products: {str(e)}"
    



        