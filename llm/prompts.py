from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")

)

def gen_prompt(entries):
    template = PromptTemplate.from_template("""
    Past Journals:
    {entries}
                                            
    Read the past journals and try to understand user's situation and mood. Then Create a personalised Prompt (2-3 sentences with no "Generated Prompt" heading. Just plane text with easy to understand English) to foster self-awareness, encourage positive thinking, and support users in building
    a consistent mindfulness practice.""")
    return llm.invoke(template.invoke({"entries": "\n".join(entries)})).content

def gen_advice(entry):
    template = PromptTemplate.from_template("""
    Journal: "{entry}"

    Read the journal carefully. Based on the tone and content, offer a short, empathetic, and motivational piece of advice with 2 to 3 actionable steps in bullet points (no "Generated Advice" heading. Just plane text with easy to understand English). Your goal is to uplift the user's mood and encourage mindful reflection.
    """)
    return llm.invoke(template.invoke({"entry": entry})).content


if __name__ == "__main__":
    sample_entries = [
        "Prompt: What inspired you?\nJournal: I finally took time to reflect.\nAdvice: Small steps lead to big changes.\nTime: 2025-07-02",
        "Prompt: What held you back today?\nJournal: I felt anxious about deadlines.\nAdvice: Breathe. You're doing your best.\nTime: 2025-07-03"
    ]
    #print(os.getenv("GOOGLE_API_KEY"))
    print("Generated Prompt:\n", gen_prompt(sample_entries))

    test_entry = "Today I felt overwhelmed but managed to push through."
    print("\nGenerated Advice:\n", gen_advice(test_entry))
