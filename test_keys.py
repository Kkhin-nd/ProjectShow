import os
from openai import OpenAI
from dotenv import load_dotenv

# .env ဖိုင်ကို ချိတ်ဆက်ရန်
load_dotenv()

# .env ထဲတွင် ထည့်ထားသော API Key များကို စာရင်းပြုစုခြင်း
API_KEYS = [
    os.getenv("OPENROUTER_API_KEY_1"),
    os.getenv("OPENROUTER_API_KEY_2"),
    os.getenv("OPENROUTER_API_KEY_3"),
    os.getenv("OPENROUTER_API_KEY_4"),
    os.getenv("OPENROUTER_API_KEY_5"),
    os.getenv("OPENROUTER_API_KEY_6"),
    os.getenv("OPENROUTER_API_KEY_7"),
    os.getenv("OPENROUTER_API_KEY_8"),
    os.getenv("OPENROUTER_API_KEY_9"),
    os.getenv("OPENROUTER_API_KEY_10"),
    os.getenv("OPENROUTER_API_KEY_11"),
        os.getenv("OPENROUTER_API_KEY_12"),
        os.getenv("OPENROUTER_API_KEY_13"),
        os.getenv("OPENROUTER_API_KEY_14"),
        os.getenv("OPENROUTER_API_KEY_15"),
        os.getenv("OPENROUTER_API_KEY_16"),
        os.getenv("OPENROUTER_API_KEY_17"),
        os.getenv("OPENROUTER_API_KEY_18"),
        os.getenv("OPENROUTER_API_KEY_19"),
        os.getenv("OPENROUTER_API_KEY_20"),
]

print("=== OpenRouter API Keys Status Check ==-\n")

for i, api_key in enumerate(API_KEYS, start=1):
    if not api_key:
        print(f"⚠️ OPENROUTER_API_KEY_{i}: ထည့်ထားခြင်း မရှိပါ (Empty)")
        continue
        
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # စမ်းသပ်ရန်အတွက် မက်ဆေ့ခ်ျတိုလေး ပို့ကြည့်ခြင်း
        response = client.chat.completions.create(
            model="google/gemini-2.5-flash", 
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        print(f"✅ OPENROUTER_API_KEY_{i}: အလုပ်လုပ်ပါသည် (Valid & Active)")
        
    except Exception as e:
        print(f"❌ OPENROUTER_API_KEY_{i}: သုံးမရတော့ပါ (Error / Out of Credit)")
        print(    f"   └─ အကြောင်းရင်း: {e}\n")

print("\n=== စစ်ဆေးမှု ပြီးဆုံးပါပြီ ===")