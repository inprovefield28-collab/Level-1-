import streamlit as st
import random

st.set_page_config(page_title="English Quiz", layout="centered")
st.title("🧒 English Quiz")

# ====== 20 題題庫（加上 audio） ======
QUESTIONS = [
    {"q": "Elephant", "choices": [("A","Egg"),("B","Elephant"),("C","Eat")], "answer": "B", "audio": "audio/Q01.mp3"},
    {"q": "What color is the sky?", "choices": [("A","Green"),("B","Blue"),("C","Red")], "answer": "B", "audio": "audio/Q02.mp3"},
    {"q": "I am hungry. I want to", "choices": [("A","Eat"),("B","Sleep"),("C","Play")], "answer": "A", "audio": "audio/Q03.mp3"},
    {"q": "Sunday", "choices": [("A","Monday"),("B","Sunday"),("C","Saturday")], "answer": "B", "audio": "audio/Q04.mp3"},
    {"q": "How are you?", "choices": [("A","I am seven"),("B","I am a boy"),("C","I am fine")], "answer": "C", "audio": "audio/Q05.mp3"},
    {"q": "Library", "choices": [("A","You can swim here"),("B","You can read books here"),("C","You can buy food here")], "answer": "B", "audio": "audio/Q06.mp3"},
    {"q": "Which one is a fruit?", "choices": [("A","An apple"),("B","A dog"),("C","A bus")], "answer": "A", "audio": "audio/Q07.mp3"},
    {"q": "Touch your nose", "choices": [("A","Eye"),("B","Nose"),("C","Mouth")], "answer": "B", "audio": "audio/Q08.mp3"},
    {"q": "What do you say in the morning?", "choices": [("A","Good night"),("B","Good afternoon"),("C","Good morning")], "answer": "C", "audio": "audio/Q09.mp3"},
    {"q": "One plus two is", "choices": [("A","Two"),("B","Three"),("C","Four")], "answer": "B", "audio": "audio/Q10.mp3"},
    {"q": "It is raining. Take your", "choices": [("A","Umbrella"),("B","Hat"),("C","Shoes")], "answer": "A", "audio": "audio/Q11.mp3"},
    {"q": "Where is the cat?", "choices": [("A","Under the table"),("B","In the sky"),("C","On the moon")], "answer": "A", "audio": "audio/Q12.mp3"},
    {"q": "A doctor works in a", "choices": [("A","School"),("B","Hospital"),("C","Park")], "answer": "B", "audio": "audio/Q13.mp3"},
    {"q": "Can you swim?", "choices": [("A","Yes I can"),("B","Yes I am"),("C","No I do not")], "answer": "A", "audio": "audio/Q14.mp3"},
    {"q": "Which animal can fly?", "choices": [("A","A bird"),("B","A fish"),("C","A pig")], "answer": "A", "audio": "audio/Q15.mp3"},
    {"q": "Today is Monday. Tomorrow is", "choices": [("A","Wednesday"),("B","Tuesday"),("C","Sunday")], "answer": "B", "audio": "audio/Q16.mp3"},
    {"q": "Close the", "choices": [("A","Window"),("B","Water"),("C","Milk")], "answer": "A", "audio": "audio/Q17.mp3"},
    {"q": "My father's brother is my", "choices": [("A","Aunt"),("B","Uncle"),("C","Brother")], "answer": "B", "audio": "audio/Q18.mp3"},
    {"q": "Wake up", "choices": [("A","It is time for bed"),("B","It is time to get up"),("C","It is time to eat lunch")], "answer": "B", "audio": "audio/Q19.mp3"},
    {"q": "How is the weather?", "choices": [("A","It is sunny"),("B","It is a pen"),("C","It is five o'clock")], "answer": "A", "audio": "audio/Q20.mp3"},
]

# ====== 初始化（只做一次） ======
if "quiz" not in st.session_state:
    st.session_state.quiz = random.sample(QUESTIONS, 5)
    st.session_state.answers = {}
    st.session_state.submitted = False

# ====== 題目顯示（含音檔） ======
for i, q in enumerate(st.session_state.quiz, 1):
    st.audio(q["audio"])
    st.write(f"### {i}. {q['q']}")
    st.session_state.answers[i] = st.radio(
        "選答案",
        q["choices"],
        format_func=lambda x: f"{x[0]}. {x[1]}",
        key=f"q{i}"
    )[0]

# ====== 交卷 ======
if st.button("✅ Finish"):
    st.session_state.submitted = True

# ====== 批改 ======
if st.session_state.submitted:
    score = 0
    wrong = []

    for i, q in enumerate(st.session_state.quiz, 1):
        if st.session_state.answers[i] == q["answer"]:
            score += 20
        else:
            wrong.append(q["q"])

    st.success(f"🎯 Score: {score} / 100")

    if wrong:
        st.error("❌ Wrong questions")
        for w in wrong:
            st.write("- " + w)
