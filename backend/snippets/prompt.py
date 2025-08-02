from flask import jsonify

def build_prompt(user_input : str, language : str = 'en') -> jsonify:
    # prompt = f"""You are Kisan-G , a farmer-friendly agenic AI model who 
    # gives responses to their queries in simple, effecive and practical way.
    # Your language of communication : {language}. Make sure it is well-researched and in long-term 
    # build user-accountability.
    # Farmer Query: {user_input}.
    # Your Suggestion: """
    
    jsonified_prompt = {
        "role": "system",
        "language": language,
        "user_input": user_input,
        "tone": "farmer-friendly, simple, effecive and practical",
        "accountability": "well-researched and in long-term build user-accountability",
    }
    
    return jsonified_prompt
    