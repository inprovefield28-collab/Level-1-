import streamlit as st
import pandas as pd
import random

# --- 設定網頁樣式 (字體加大) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 24px !important;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 32px !important;
        font-weight: bold;
        color: #2E4053;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. 讀取資料 ---
@st.cache_data
def load_data():
    # 讀取你的 100 題 CSV
    df = pd.read_csv("HWG1-100.csv")
    return df

df = load_data()

# --- 2. 初始化 Session State (確保重新整理不會亂掉) ---
if 'quiz_data' not in st.session_state:
    # 從 100 題中隨機選 10 題
    st.session_state.quiz_data = df.sample(n=10).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.answerkeys = [] # 格式: (題目, 選錯的項, 正確答案, 是否正確)

# --- 3. 測驗介面 ---
if st.session_state.current_idx < 10:
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    st.markdown(f'<p class="question-text">聽聽看，哪一個是對的？</p>', unsafe_allow_html=True)
    
    # 播放音檔 (檔名需對應: q_001.mp3)
    qid = str(q['id']).zfill(3)
    st.audio(f"audio/q_{qid}.mp3")

    # 答案按鈕 (字體已透過 CSS 加大)
    # 假設你的 CSV 欄位是 option_a, option_b, option_c
    opts = [q['option_a'], q['option_b'], q['option_c']]
    
    for opt in opts:
        if st.button(opt):
            # 判斷正誤 (假設 answerkey 欄位存的是內容文字，或是 A/B/C)
            # 這裡示範比對文字內容
            is_correct = (opt == q['answerkey'])
            st.session_state.answerkeys.append({
                "question": q['question'],
                "user_choice": opt,
                "correct_answerkey": q['answerkey'],
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 4. 結果頁面與錯題複製 ---
else:
    st.balloons()
    st.header("完成練習！")
    
    wrong_list = []
    score = 0
    
    for item in st.session_state.answerkeys:
        if item['is_correct']:
            score += 1
        else:
            # 格式化錯題字串
            wrong_list.append(f"題目：{item['question']}\n你的答案：{item['user_choice']}\n正確答案：{item['correct_answerkey']}\n---")

    st.subheader(f"得分：{score} / 10")

    if wrong_list:
        st.write("### ❌ 錯題記錄")
        wrong_text = "\n".join(wrong_list)
        st.text_area("可以手動選取複製以下錯題內容：", value=wrong_text, height=300)
    else:
        st.success("太棒了！全部正確！")

    if st.button("再測驗一次"):
        del st.session_state.quiz_data
        st.rerun()
