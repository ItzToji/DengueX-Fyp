import pandas as pd
import matplotlib.pyplot as plt

# --------------------
# Load results
# --------------------
df = pd.read_csv("chatbot_20k_stress_test_results.csv")

# Create output directory (optional)
import os
os.makedirs("graphs", exist_ok=True)

# --------------------
# 1. Intent Distribution (Bar Chart)
# --------------------
plt.figure(figsize=(10, 6))
df["predicted_intent"].value_counts().plot(kind="bar")
plt.title("Intent Distribution (20,000 Queries)")
plt.xlabel("Intent")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("graphs/intent_distribution.png")
plt.close()

# --------------------
# 2. Dengue vs Non-Dengue (Pie Chart)
# --------------------
dengue_count = (df["predicted_intent"] != "out_of_scope").sum()
non_dengue_count = (df["predicted_intent"] == "out_of_scope").sum()

plt.figure(figsize=(6, 6))
plt.pie(
    [dengue_count, non_dengue_count],
    labels=["Dengue-related", "Non-dengue"],
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Dengue vs Non-Dengue Queries")
plt.savefig("graphs/dengue_vs_nondengue.png")
plt.close()

# --------------------
# 3. Confidence Score Distribution
# --------------------
plt.figure(figsize=(8, 6))
plt.hist(df["confidence"], bins=20)
plt.title("Confidence Score Distribution")
plt.xlabel("Confidence")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("graphs/confidence_distribution.png")
plt.close()

# --------------------
# 4. Response Time Distribution
# --------------------
plt.figure(figsize=(8, 6))
plt.hist(df["response_time_sec"], bins=20)
plt.title("Response Time Distribution")
plt.xlabel("Response Time (seconds)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("graphs/response_time_distribution.png")
plt.close()

# --------------------
# 5. Emergency vs Non-Emergency
# --------------------
df["emergency_flag"] = df["predicted_intent"].apply(
    lambda x: "Emergency" if x == "dengue_emergency" else "Non-Emergency"
)

plt.figure(figsize=(6, 6))
df["emergency_flag"].value_counts().plot(kind="bar")
plt.title("Emergency vs Non-Emergency Responses")
plt.xlabel("Category")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("graphs/emergency_vs_non_emergency.png")
plt.close()

# --------------------
# 6. Question Type vs Intent (Stacked Bar)
# --------------------
ct = pd.crosstab(df["question_type"], df["predicted_intent"])

ct.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 7)
)

plt.title("Question Type vs Predicted Intent")
plt.xlabel("Question Type")
plt.ylabel("Count")
plt.legend(title="Intent", bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig("graphs/question_type_vs_intent.png")
plt.close()

print("All graphs generated successfully and saved in the 'graphs/' folder.")
