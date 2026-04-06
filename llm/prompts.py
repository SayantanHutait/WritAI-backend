from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GOOGLE_API_KEY")

)

def gen_prompt(entries):
    template = PromptTemplate.from_template("""
    Past Journals:
    {entries}
                                            
    Read the past journals and try to understand the user's current situation and mood. 
    Your task is to generate a thought-provoking QUESTION or a specific TOPIC for them to journal about today. 
    Do NOT give advice. Do NOT give affirmations. ONLY ask an engaging question to spark their writing.
    Keep it strictly to 1 or 2 sentences. No formatting, no "Prompt:" heading, just plain text.
    Example: 'You mentioned feeling stressed about work lately. What is one small thing you can do today to regain a sense of control?'
    """)
    try:
        return llm.invoke(template.invoke({"entries": "\n".join(entries)})).content
    except Exception as e:
        print("Failed to generate prompt:", e)
        return "What's on your mind today? Write down whatever comes to you."

def gen_advice(entry):
    template = PromptTemplate.from_template("""
    Journal: "{entry}"

    Read the journal carefully. Based on the tone and content, offer a short, empathetic, and motivational piece of advice with 2 to 3 actionable steps in bullet points (no "Generated Advice" heading. Just plane text with easy to understand English). Your goal is to uplift the user's mood and encourage mindful reflection.
    """)
    try:
        return llm.invoke(template.invoke({"entry": entry})).content
    except Exception as e:
        print("Failed to generate advice:", e)
        return "Thank you for sharing your thoughts today. Keep reflecting and stay positive!"

def analyze_journal(entry):
    template = PromptTemplate.from_template("""
    Journal: "{entry}"
    
    You are an expert psychotherapist and data analyst. Read the journal entry and extract the following:
    1. mood_score: An integer from 1 to 10 representing the sentiment/mood, where 1 is extremely negative/depressed, 5 is neutral, and 10 is extremely positive/joyful.
    2. mood_label: A single word or short phrase describing the primary emotion (e.g., "Joyful", "Anxious", "Calm", "Frustrated").
    3. keywords: A list of 3-5 important words or short themes mentioned in the journal.
    4. topic: The primary category of the journal (e.g., "Career", "Relationships", "Health", "Growth", "Daily Life").
    
    Return ONLY a valid JSON object. No markdown formatting, no code blocks, just the JSON string itself.
    Example output:
    {{
        "mood_score": 8,
        "mood_label": "Optimistic",
        "keywords": ["project", "friends", "dinner"],
        "topic": "Daily Life"
    }}
    """)
    try:
        response = llm.invoke(template.invoke({"entry": entry})).content
        response = response.strip()
        if response.startswith("```json"):
            response = response.replace("```json", "", 1).strip()
            if response.endswith("```"):
                response = response[:-3].strip()
        elif response.startswith("```"):
            response = response.replace("```", "", 1).strip()
            if response.endswith("```"):
                response = response[:-3].strip()
        data = json.loads(response)
        return dict(
            mood_score=int(data.get("mood_score", 5)),
            mood_label=str(data.get("mood_label", "Neutral")),
            keywords=list(data.get("keywords", [])),
            topic=str(data.get("topic", "General"))
        )
    except Exception as e:
        print("Failed to parse JSON for analyze_journal:", e)
        return {
            "mood_score": 5,
            "mood_label": "Neutral",
            "keywords": [],
            "topic": "General"
        }

def generate_insights(entries_text):
    if not entries_text or len(entries_text.strip()) == 0:
        return "Not enough data yet to find patterns. Keep journaling!"
    template = PromptTemplate.from_template("""
    Past Journals:
    {entries}
    
    Read the past journal entries and analyze the user's emotional trends and topics.
    Provide 2-3 specific, actionable insights or detected patterns.
    Examples formatting:
    - "You tend to feel lower energy towards the end of the week. Try adding a small restful routine on Thursdays."
    - "Your mood spikes when you mention 'friends'. These social interactions are highly beneficial for you."
    
    Do not use any introductory conversational text. Just output the bullet points directly.
    """)
    try:
        return llm.invoke(template.invoke({"entries": entries_text})).content
    except Exception as e:
        print("Failed to generate insights:", e)
        return "AI insights are currently unavailable due to API limits. Keep journaling and check back later!"


if __name__ == "__main__":
    sample_entries = [
        "Prompt: What inspired you?\nJournal: I finally took time to reflect.\nAdvice: Small steps lead to big changes.\nTime: 2025-07-02",
        "Prompt: What held you back today?\nJournal: I felt anxious about deadlines.\nAdvice: Breathe. You're doing your best.\nTime: 2025-07-03"
    ]
    #print(os.getenv("GOOGLE_API_KEY"))
    print("Generated Prompt:\n", gen_prompt(sample_entries))

    test_entry = "Today I felt overwhelmed but managed to push through."
    print("\nGenerated Advice:\n", gen_advice(test_entry))
