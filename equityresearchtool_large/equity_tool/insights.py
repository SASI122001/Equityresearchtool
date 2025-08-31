from config import OPENAI_API_KEY, OPENAI_MODEL

def generate_insights(tickers, fundamentals, risks):
    if not OPENAI_API_KEY:
        return "\n".join([f"- {t}: solid fundamentals (heuristic)." for t in tickers])
    try:
        from openai import OpenAI
        client=OpenAI(api_key=OPENAI_API_KEY)
        prompt=f"Compare {', '.join(tickers)} based on fundamentals and risks: {fundamentals}, {risks}"
        resp=client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role":"user","content":prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(Insight generation error: {e})"
