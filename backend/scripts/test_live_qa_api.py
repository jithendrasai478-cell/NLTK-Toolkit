import requests

url = "http://127.0.0.1:5001/api/v1/nlp/qa"

passage1 = "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889 as the centerpiece of the 1889 World Fair. It was designed by Gustave Eiffel."
passage2 = "NLTK was created in 2001 by Steven Bird and Edward Loper at the University of Pennsylvania."

tests = [
    (passage1, "Who designed the Eiffel Tower?"),
    (passage1, "Where is the Eiffel Tower located?"),
    (passage1, "When was it constructed?"),
    (passage1, "Who was the president of France in 1889?"),
    (passage1, "What is the speed of light?"),
    (passage2, "When was NLTK created?"),
    (passage2, "Who created NLTK?"),
    (passage2, "What is the capital of Japan?")
]

print("=== TESTING ZERO-HALLUCINATION EXTRACTIVE QA ===")
for p, q in tests:
    res = requests.post(url, json={"passage": p, "question": q}).json()
    d = res.get("data", {})
    ans = d.get("answer")
    grounded = d.get("is_grounded")
    conf = d.get("confidence")
    conf_lbl = d.get("confidence_label")
    print(f"Q: {q}")
    print(f"   Answer:   {ans}")
    print(f"   Grounded: {grounded}")
    print(f"   Conf:     {conf} ({conf_lbl})")
    print("-" * 50)
