from dotenv import load_dotenv
load_dotenv()

from app.llm import get_llm

fast = get_llm('fast')
writer = get_llm('writer')

print('fast model:', fast.model_name, 'temp:', fast.temperature)
print('writer model:', writer.model_name, 'temp:', writer.temperature)

r = fast.invoke('Say hi in exactly one word')
print('LLM response:', r.content)
