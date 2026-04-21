import streamlit as st
import pandas as pd
import random
import os

# --- 1. 設定網頁樣式 ---
st.set_page_config(page_title="HWG 聽力測驗", layout="centered")

st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        padding: 15px 20px !important;
        background-color: white !important;
        border: 2px solid #eee !important;
        border-radius: 15px !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold !important;
        white-space: pre-wrap !important; 
        text-align: left !important;
    }
    audio { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 讀取與合併資料 ---
@st.cache_data
def load_data():
    files_to_load = ["HWG1-100.csv", "HWG101-200.csv"]
    df_list = []
    for f in files_to_load:
        if os.path.exists(f):
            try:
                df_list.append(pd.read_csv(f, encoding='utf-8-sig'))
            except:
                df_list.append(pd.read_csv(f, encoding='big5'))
    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

df = load_data()

# --- 3. 初始化 Session ---
if 'quiz_data' not in st.session_state and not df.empty:
    # 隨機抽 10 題並轉為字典
    st.session_state.quiz_data = df.sample(n=min(len(df), 10)).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if not df.empty and st.session_state.current_idx < len(st.session_state.quiz_data):
    # 直接從字典中根據「欄位名稱」取值，避免錯位
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    q_id = str(q.get('id')).zfill(3)
    q_text = q.get('question', '無題目')
    options = {
        'A': str(q.get('A', '')),
        'B': str(q.get('B', '')),
        'C': str(q.get('C', ''))
    }
    # 正確答案標籤 (A, B, 或 C)
    correct_label = str(q.get('answer', '')).strip().upper()

    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    
    # 音檔播放
    audio_path = f"audio/q_{q_id}.mp3"
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"缺少音檔: {audio_path}")

    # 顯示選項按鈕
    for label in ['A', 'B', 'C']:
        option_text = options[label]
        if st.button(f"{label}. {option_text}", key=f"q_{st.session_state.current_idx}_{label}", use_container_width=True):
            
            # 判斷對錯：比較標籤 (A == A?)
            is_correct = (label == correct_label)
            
            # 存入結果
            st.session_state.results.append({
                "question": q_text,
                "user_choice": option_text,
                "correct_answer": options.get(correct_label, "未設定"),
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 5. 結果頁面 ---
elif not df.empty:
    st.header("🏆 練習結束")
    score = sum(1 for x in st.session_state.results if x['is_correct'])
    st.subheader(f"得分：{score * 10} 分")

    for i, res in enumerate(st.session_state.results):
        if res['is_correct']:
            st.success(f"Q{i+1}: {res['question']} \n\n 回答: {res['user_choice']} ✅")
        else:
            st.error(f"Q{i+1}: {res['question']} \n\n 回答: {res['user_choice']} ❌ \n\n 正確答案: {res['correct_answer']}")

    if st.button("再玩一次", use_container_width=True):
        del st.session_state.quiz_data
        st.rerun()
