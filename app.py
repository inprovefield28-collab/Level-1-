import streamlit as st
import pandas as pd
import random
import os

# --- 1. 網頁樣式 ---
st.set_page_config(page_title="HWG 聽力測驗", layout="centered")
st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        padding: 15px 20px !important;
        background-color: white !important;
        border: 2px solid #eee !important;
        border-radius: 15px !important;
    }
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold !important;
        text-align: left !important;
    }
    audio { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 讀取資料 ---
@st.cache_data
def load_data():
    files = ["HWG1-100.csv", "HWG101-200.csv"]
    all_dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                temp_df = pd.read_csv(f, encoding='utf-8-sig')
                # 強制將欄位名稱清理：去空白、轉小寫
                temp_df.columns = [c.strip().lower() for c in temp_df.columns]
                all_dfs.append(temp_df)
            except:
                temp_df = pd.read_csv(f, encoding='big5')
                temp_df.columns = [c.strip().lower() for c in temp_df.columns]
                all_dfs.append(temp_df)
    if not all_dfs: return pd.DataFrame()
    return pd.concat(all_dfs, ignore_index=True)

df = load_data()

# --- 3. 初始化測驗 ---
if 'quiz_data' not in st.session_state and not df.empty:
    # 從合併後的資料中隨機抽 10 題
    st.session_state.quiz_data = df.sample(n=min(len(df), 10)).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if not df.empty and st.session_state.current_idx < len(st.session_state.quiz_data):
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    # 根據清理後的標頭（小寫）抓取
    q_id = str(q.get('id', '0')).zfill(3)
    q_text = q.get('question', '無題目')
    
    # 選項對照表
    opts = {
        'A': str(q.get('a', '')),
        'B': str(q.get('b', '')),
        'C': str(q.get('c', ''))
    }
    
    # 關鍵修正：對應你的欄位 Answerkey (已在讀取時轉為小寫 answerkey)
    ans_label = str(q.get('answerkey', '')).strip().upper()

    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    
    audio_path = f"audio/q_{q_id}.mp3"
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"找不到音檔: {audio_path}")

    # 顯示 A, B, C 選項按鈕
    for label in ['A', 'B', 'C']:
        if st.button(f"{label}. {opts[label]}", key=f"btn_{st.session_state.current_idx}_{label}", use_container_width=True):
            is_correct = (label == ans_label)
            
            st.session_state.results.append({
                "
