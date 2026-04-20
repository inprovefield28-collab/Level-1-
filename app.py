import streamlit as st
import pandas as pd
import random
import os

# --- 設定網頁樣式 (字體加大) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3.5em;
        font-size: 26px !important;
        margin-bottom: 15px;
        border-radius: 10px;
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
    file_name = "HWG1-100.csv"
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig')
    except:
        df = pd.read_csv(file_name, encoding='big5')
    return df

df = load_data()

# --- 2. 初始化 Session State ---
if 'quiz_data' not in st.session_state:
    # 隨機挑 10 題
    st.session_state.quiz_data = df.sample(n=10).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 3. 測驗介面 ---
if st.session_state.current_idx < 10:
    # 取得當前題目
    q = st.session_state.quiz_data[st.session_state.current_idx]
    # 將資料轉為 list 方便用位置索引 (防標題亂碼)
    q_vals = list(q.values())
    
    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    st.markdown('<p class="question-text">聽聽看，哪一個是對的？</p>', unsafe_allow_html=True)
    
    # 音檔路徑 (假設第0欄是id)
    qid = str(q_vals[0]).zfill(3)
    audio_path = f"audio/q_{qid}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    # 定義選項文字 (假設第2,3,4欄分別是 A, B, C 的選項文字)
    # 定義對應代號
    option_texts = [q_vals[2], q_vals[3], q_vals[4]]
    option_keys = ['A', 'B', 'C']
    
    # 顯示按鈕
    for i in range(len(option_texts)):
        if st.button(str(option_texts[i]), key=f"btn_{i}"):
            # 學生點的代號 (A, B 或 C)
            user_choice_key = option_keys[i]
            # 正確答案代號 (從第5欄抓取並去空格)
            correct_key = str(q_vals[5]).strip().upper()
            
            is_correct = (user_choice_key == correct_key)
            
            # 紀錄結果
            st.session_state.results.append({
                "question_text": q_vals[1], # 第1欄是問句文字
                "user_choice_text": option_texts[i],
                "correct_answer_key": correct_key,
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 4. 結果頁面與錯題複製 ---
else:
    st.balloons()
    st.header("練習結束囉！")
    
    wrong_list = []
    score = 0
    
    for item in st.session_state.results:
        if item['is_correct']:
            score += 1
        else:
            wrong_list.append(f"題目：{item['question_text']}\n你的回答：{item['user_choice_text']}\n正確答案代號：{item['correct_answer_key']}\n---")

    st.subheader(f"得分：{score} / 10")

    if wrong_list:
        st.write("### ❌ 錯題記錄")
        summary_text = "\n".join(wrong_list)
        st.text_area("選取下方文字即可複製：", value=summary_text, height=300)
    else:
        st.success("超級厲害！全部都答對了！")

    if st.button("再玩一次"):
        del st.session_state.quiz_data
        st.rerun()
