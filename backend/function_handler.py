import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from difflib import get_close_matches
load_dotenv()


client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)

def convert_list_to_category_dict(product_list):
    category_dict = {}
    for p in product_list:
        cat = p.get("category", "Uncategorized")
        if cat not in category_dict:
            category_dict[cat] = []
        category_dict[cat].append(p)
    return category_dict

def build_product_index(data):
    
    index = {}
    for category, products in data.items():
        for p in products:
            p_copy = p.copy()
            p_copy.setdefault("category", category)
            name_key = p_copy.get("name", "").lower()
            id_key = p_copy.get("id", "").lower()
            if name_key:
                index[name_key] = p_copy
            if id_key:
                index[id_key] = p_copy
    return index

def fuzzy_find_product(user_msg, index, threshold=0.55):
    user_msg = user_msg.lower()
    product_keys = list(index.keys())
    matches = get_close_matches(user_msg, product_keys, n=1, cutoff=threshold)
    if matches:
        return index[matches[0]]
    return None

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

def find_product(msg):
    try:
        with open('./resources/productlists.json','r',encoding='utf-8') as file:
            raw_data = json.load(file)

        if isinstance(raw_data,dict):
            data = raw_data
        else:
            data = convert_list_to_category_dict(raw_data)

        index = build_product_index(data)

        match = fuzzy_find_product(msg,index)

        if match is None:
            product_names = list(index.keys())
            guess = ai_guess_product(msg, product_names)
            if guess != "none" and guess in index:
                match = index[guess]

        if match:
            return match

        return None
        
    except Exception as e:
        print(f"error finding the product {str(e)}")
        return None

def product_info(msg):

    match = find_product(msg)

    if match:
            p = match
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


def product_price(msg):

    match = find_product(msg)

    if match:
        p = match
        name = p.get("name","Unknown")
        price = p.get("price", "N/A")

        response_lines = [
            f"Product Found: {name}",
            f"Price: Rs. {price}",
        ]

        return "\n".join(response_lines)
    
    return "I couldn't find that product price."

def ai_product_recommender(msg):
    try:
        with open('./resources/productlists.json','r',encoding='utf-8') as file:
            raw_data = json.load(file)

        prompt = f"""
        You are an AI product recommender.
        User said: "{msg}"
        Here is the list of products:
        {raw_data}

        Return ONLY product name that match with user's needs.
        Only the recommended products.
        """
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # normalize to lower for matching against index keys
        return ai_response.choices[0].message.content.strip().lower()
    
    except Exception as e:
        return f"Error reading data {str(e)}"


