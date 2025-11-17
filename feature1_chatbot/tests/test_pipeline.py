import os
from chatbot_engine import load_kb, predict_intent, is_urgent, find_answer, get_reply
KB_PATH = os.path.join(os.path.dirname(__file__), '..', 'dengue_kb_seed_50.jsonl')

def test_load_kb():
    n = load_kb(KB_PATH)
    assert n >= 50

def test_predict_intent():
    assert predict_intent('I have fever and was bitten by a mosquito') == 'dengue'
    assert predict_intent('How to bake a cake') == 'not-dengue'

def test_urgent():
    u, matches = is_urgent('I am vomiting blood and very weak')
    assert u is True
    u2, _ = is_urgent('I have a mild fever and headache')
    assert u2 is False

def test_retrieval():
    res = find_answer('What are early signs of dengue?')
    assert len(res) == 1
    assert 'canonical_answer' in res[0]

def test_get_reply():
    r = get_reply('What are the early signs of dengue?')
    assert 'reply' in r
