# --- START OF FILE: chat_feature.py ---
# (v3.1 - Professional with Holistic & Ayurvedic Suggestions)

import re
import traceback
import google.generativeai as genai

# --- Core RAG and Chat Processing ---

def process_chat_query(query: str, vector_db: object, chat_model: object, chunks: list, chat_session: dict) -> str:
    """
    Processes a user query using the RAG model.
    This is the main entry point for a chat interaction.
    """
    if not all([query, vector_db, chat_model, chunks]):
        missing = [name for name, val in {'query': query, 'vector_db': vector_db, 'chat_model': chat_model, 'chunks': chunks}.items() if not val]
        print(f"Chat Error: Missing required components: {', '.join(missing)}")
        return "Error: A system component is unavailable. Please try again later."

    print(f"\n--- Processing Chat Query: '{query}' ---")
    
    try:
        distances, indices = vector_db.search(query, k=4)
        if indices is not None and len(indices) > 0:
            relevant_chunks = [chunks[i] for i in indices[0] if 0 <= i < len(chunks)]
            report_context = "\n---\n".join(relevant_chunks) if relevant_chunks else "No specific information found in the report for this query."
            print(f"Found {len(relevant_chunks)} relevant chunks.")
        else:
            report_context = "No specific information found in the report for this query."
    except Exception as e:
        print(f"Error during vector_db search: {e}")
        traceback.print_exc()
        report_context = "An error occurred while searching the report."

    response_text = generate_response_with_gemini(query, report_context, chat_model, chat_session)
    update_chat_session(chat_session, query, response_text)
    return response_text

def generate_response_with_gemini(query: str, report_context: str, chat_model: object, chat_session: dict) -> str:
    """
    Generates a response using the Gemini API with a prompt that encourages holistic suggestions.
    """
    history = chat_session.get("history", [])
    conversation_history = "\n".join([f"User: {turn['user']}\nAssistant: {turn['bot']}" for turn in history[-3:]])

    # ======================================================================
    # --- THE NEW PROMPT (v3.1) - WITH HOLISTIC/AYURVEDIC INSTRUCTIONS ---
    # ======================================================================
    prompt = f"""
    You are a professional medical report assistant with a holistic perspective. Your tone is clear, supportive, and informative. Your goal is to integrate data from the medical report with general wellness advice, including conventional, natural, and Ayurvedic remedies.

    *Conversation History:*
    {conversation_history}

    *Relevant Information from Medical Report:*
    ```
    {report_context}
    ```

    *User's Current Question:* "{query}"

    *RESPONSE INSTRUCTIONS:*

    1.  *Direct Answer:* Always start by directly addressing the user's question.
    2.  *Integrate Report Data:* Weave in relevant data from the report naturally. Example: "Regarding your question about hemoglobin, the report shows a value of [X]."
    3.  *Holistic Suggestions (CRITICAL):*
        *   If the user asks how to improve their health, a specific biomarker, or for remedies, you **must** provide a structured list of suggestions.
        *   **Structure the list into two parts:**
            *   **General & Lifestyle Suggestions:** Include common advice related to diet (e.g., "iron-rich foods"), exercise, and lifestyle changes.
            *   **Ayurvedic & Natural Remedies:** Include well-known, safe, and relevant Ayurvedic herbs or natural remedies (e.g., "Ashwagandha for stress," "Amla for Vitamin C," "Turmeric for inflammation").
        *   **Example for low hemoglobin:**
            *   **General & Lifestyle Suggestions:**
                *   Diet: Increase intake of iron-rich foods like spinach, lentils, and lean meats.
                *   Vitamin C: Pair iron sources with Vitamin C (e.g., citrus fruits) to boost absorption.
            *   **Ayurvedic & Natural Remedies:**
                *   Herbs: Herbs like Ashwagandha may support overall vitality, while Punarnava is traditionally used for blood health.
                *   Dietary: Incorporating dates and beetroot juice is a common natural practice.
    4.  *Maintain Safety:*
        *   You are not a doctor. Never give a definitive diagnosis.
        *   Frame all suggestions as "general information" or "commonly used remedies" that should be discussed with a healthcare professional.
    5.  *Mandatory Disclaimer:* End **every** response with this exact disclaimer, separated by a newline.
    6.  Don't include star's(*) for highlight instead use numbering or dot for points.

    ---
    *Disclaimer:* This information is for educational purposes only and does not constitute medical advice. The suggestions, including Ayurvedic remedies, may not be suitable for everyone and could interact with medications. Always consult your doctor or a qualified health provider before making any changes to your health regimen.
    """

    try:
        response = chat_model.generate_content(prompt)
        response_text = ''.join(part.text for part in response.parts) if hasattr(response, 'parts') and response.parts else getattr(response, 'text', '')

        if not response_text:
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                return f"My response was blocked due to safety filters ({response.prompt_feedback.block_reason}). Please rephrase your question."
            return "Apologies, I could not generate a response."
        
        return response_text.strip()

    except Exception as e:
        print(f"!!! ERROR during Gemini API call: {type(e).__name__}: {str(e)} !!!")
        traceback.print_exc()
        return "Sorry, I encountered an error while processing your request. Please try again."

# --- Session and State Management (Unchanged) ---

def initialize_chat() -> dict:
    """Initializes a new, empty chat session state."""
    return {"history": []}

def update_chat_session(chat_session: dict, user_query: str, bot_response: str):
    """Updates the chat session history after a successful turn."""
    if "history" not in chat_session or not isinstance(chat_session["history"], list):
        chat_session["history"] = []
    
    chat_session["history"].append({"user": user_query, "bot": bot_response})
    chat_session["history"] = chat_session["history"][-10:]

# --- END OF FILE: chat_feature.py ---