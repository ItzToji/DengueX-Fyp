# Simple interactive demo for the chatbot engine
from chatbot_engine import load_kb, get_reply
import os

KB_PATH = os.path.join(os.path.dirname(__file__), 'dengue_kb_seed_50.jsonl')
print('Loading KB...')
n = load_kb(KB_PATH)
print(f'Loaded {n} KB entries. Type "exit" to quit.')
while True:
    q = input('\\nYou: ').strip()
    if not q or q.lower() in ('exit','quit'):
        break
    r = get_reply(q)
    print('\\nBot: ' + r['reply'])
    print('\\nMeta:', {k:v for k,v in r.items() if k!='reply'}) 
