"""Run this model in Python

> pip install openai
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from difflib import get_close_matches
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

# ------------------ convert list -> category dict (unchanged) ------------------
def convert_list_to_category_dict(product_list):
    category_dict = {}
    for p in product_list:
        cat = p.get("category", "Uncategorized")
        if cat not in category_dict:
            category_dict[cat] = []
        category_dict[cat].append(p)
    return category_dict
# -----------------------------------------------------------------------------

# ------------------ BUILD PRODUCT INDEX FOR FAST SEARCH ----------------------
def build_product_index(data):
    """
    data: dict where keys are category names and values are lists of product dicts.
    This function returns an index: { lower_name_or_id: product_copy_with_category }
    """
    index = {}
    for category, products in data.items():
        for p in products:
            # create a shallow copy so we can safely add the category (do not mutate original)
            p_copy = p.copy()
            # ensure 'category' exists on product object (helps later when formatting)
            p_copy.setdefault("category", category)
            # normalize keys for index
            name_key = p_copy.get("name", "").lower()
            id_key = p_copy.get("id", "").lower()
            if name_key:
                index[name_key] = p_copy
            if id_key:
                index[id_key] = p_copy
    return index
# -----------------------------------------------------------------------------


# ----------------------- FUZZY SEARCH ---------------------------------------
def fuzzy_find_product(user_msg, index, threshold=0.55):
    user_msg = user_msg.lower()
    product_keys = list(index.keys())
    matches = get_close_matches(user_msg, product_keys, n=1, cutoff=threshold)
    if matches:
        return index[matches[0]]
    return None
# -----------------------------------------------------------------------------


# ----------------------- AI PRODUCT MATCHER ---------------------------------
def ai_guess_product(user_msg, product_names):
    prompt = f"""
You are an AI product matcher.
User said: "{user_msg}"
Here is the list of product names:
{product_names}

Return ONLY the closest product name (exactly as it appears above).
If none match, reply exactly: none
"""
    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # normalize to lower for matching against index keys
    return ai_response.choices[0].message.content.strip().lower()
# -----------------------------------------------------------------------------


# ----------------------- INTENT HANDLER (product info) -----------------------
def product_info(msg):
    try:
        # Load raw JSON
        with open('./resources/productlists.json', 'r', encoding='utf-8') as file:
            raw = json.load(file)

        # If raw is a dict (already category-grouped) use it, else convert list->dict
        if isinstance(raw, dict):
            data = raw
        else:
            data = convert_list_to_category_dict(raw)

        # Build index (adds category into product copies)
        index = build_product_index(data)

        # 1) Try exact/fuzzy match
        match = fuzzy_find_product(msg, index)

        # 2) Fallback: AI guess (if fuzzy fails)
        if match is None:
            product_names = list(index.keys())  # keys are lowercased names/ids
            guess = ai_guess_product(msg, product_names)
            if guess != "none" and guess in index:
                match = index[guess]

        # If we found a product, format the response
        if match:
            p = match
            # safe getters (some fields may be missing)
            name = p.get("name", "Unknown")
            brand = p.get("brand", "Unknown")
            category = p.get("category", "Unknown")
            subcat = p.get("subcategory", "")
            price = p.get("price", "N/A")
            rating = p.get("rating", "N/A")
            specs = p.get("specs", {})

            response_lines = [
                f"Product Found: {name}",
                f"Brand: {brand}",
                f"Category: {category}" + (f" → {subcat}" if subcat else ""),
                f"Price: Rs. {price}",
                "",
                f"⭐ Rating: {rating}",
                "",
                "Specifications:"
            ]
            for spec_key, spec_val in specs.items():
                response_lines.append(f"- {spec_key.capitalize()}: {spec_val}")

            return "\n".join(response_lines)

        return "I couldn't find that product. Please try again or give a more specific name."

    except Exception as e:
        # return the exception text for debugging; in prod, log instead
        return f"Error reading product list: {str(e)}"

def list_products(msg):
    global selected_intent
    selected_intent = "list_products"
    return "We have Laptops, Smartphones, Audio Devices, Wearables, Cameras, Gaming, Smart Home and Accessories. What category are you interested in?"


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
    global selected_intent
    if selected_intent == None:
        print(selected_intent)
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
    
    