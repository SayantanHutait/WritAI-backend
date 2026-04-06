from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from bson import ObjectId

import os

load_dotenv()

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri)
collection = client.journals.entries

def get_entries(user_id, limit=3):
    cursor = collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return [
        f"Prompt: {d['generated_prompt']}\nJournal: {d['user_entry']}\nAdvice: {d['ai_advice']}\nTime: {d['timestamp']}"
        for d in cursor
    ]
def save(user_id, prompt, entry, advice, metadata=None):
    if metadata is None:
        metadata = {}
        
    collection.insert_one({
        "user_id": user_id,
        "generated_prompt": prompt,
        "user_entry": entry,
        "ai_advice": advice,
        "timestamp": datetime.now(),
        "mood_score": metadata.get("mood_score"),
        "mood_label": metadata.get("mood_label"),
        "keywords": metadata.get("keywords", []),
        "topic": metadata.get("topic")
    })

def get_dashboard_data(user_id):
    cursor = collection.find({"user_id": user_id}).sort("timestamp", 1)
    
    mood_trend = []
    word_frequencies = {}
    topic_counts = {}
    
    entries_for_insights = []
    
    for d in cursor:
        entries_for_insights.append(d["user_entry"])
        
        # Mood Trend (using timestamp as date string)
        if "mood_score" in d and d["mood_score"] is not None:
            date_str = d["timestamp"].strftime("%b %d")
            mood_trend.append({"date": date_str, "score": d["mood_score"]})
            
        # Word Frequencies
        if "keywords" in d and isinstance(d["keywords"], list):
            for word in d["keywords"]:
                word = str(word).lower().strip()
                if word:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1
                    
        # Topics
        if "topic" in d and d["topic"]:
            topic = d["topic"]
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
    # Format word frequencies for react-wordcloud
    word_cloud_data = [{"text": k, "value": v} for k, v in word_frequencies.items()]
    # Optional: limit to top 30
    word_cloud_data = sorted(word_cloud_data, key=lambda x: x["value"], reverse=True)[:30]
    
    topic_distribution = [{"name": k, "count": v} for k, v in topic_counts.items()]
    
    return {
        "mood_trend": mood_trend,
        "word_cloud_data": word_cloud_data,
        "topic_distribution": topic_distribution,
        "entries_text": "\n\n".join(entries_for_insights[-10:]) # Only standardizing recent 10 to limit token size
    }

def get_hist(user_id):
    cursor = collection.find({"user_id": user_id}).sort("timestamp", -1)
    return [
        {
            "id": str(d["_id"]),
            "journal": d["user_entry"],
            "timestamp": d["timestamp"].strftime("%Y-%m-%d %H:%M")
        }
        for d in cursor
    ]

def delete_journal(user_id,journal_id):
    result = collection.delete_one({"_id": ObjectId(journal_id), "user_id": user_id})
    return result.deleted_count



if __name__ == "__main__":
    uid = "sayantan123"

    for item in get_hist(uid):
        print(item)
        print("-" * 50)

