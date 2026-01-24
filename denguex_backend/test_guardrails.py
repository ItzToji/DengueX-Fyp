from chatbot.guardrails import is_blocked_query

print("Test 1 (should be True):")
print(is_blocked_query("Can you diagnose dengue?"))

print("Test 2 (should be False):")
print(is_blocked_query("How does dengue spread?"))
