import streamlit as st
import pandas as pd
import random
import os

# --- 1. 設定網頁樣式 (Grid 強制置左版) ---
st.set_page_config(page_title="HWG 聽力測驗", layout="centered")

st.markdown("""
    <style>
    /* 強制按鈕樣式 */
    div.stButton > button {
        width: 100% !important;
        height: auto !important;
        padding: 15px 20px !important;
        background-color: white !important;
        border: 2px solid #eee !important;
        border-radius: 15px !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        border-color: #8bc34a !important;
        background-color: #f9fff0 !important;
    }

    /* 強制按鈕內的文字標籤 */
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold !important;
        text-align: left !important;
        white-space: pre-wrap !important; 
        margin: 0 !important;
        width: 100% !important;
    }
    
    .question-header {
        font-size: 18px;
        color: #666;
        margin-bottom: 10px;
    }
    
    audio { width: 100% !important; height: 50px !important; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 讀取並合併資料 (1-100 & 101-200) ---
@st.cache_data
def load_data():
    files_to_load = ["HWG1-100.csv", "HWG101-200.csv"]
    df_list = []
    
    for file_name in files_to_load:
        if os.path.exists(file_name):
            try:
                temp_df = pd.read_csv(file_name, encoding='utf-8-sig')
            except Exception:
                temp_df = pd.read_csv(file_name, encoding='big5')
            
            # 重要：統一欄位名稱為小寫並去除空白，避免 Answerkey vs answerkey 的問題
            temp_df.columns = [c.strip().lower() for c in temp_df.columns]
            df_list.append(temp_df)
    
    if not df_list:
        return pd.DataFrame()
    
    return pd.concat(df_list, ignore_index=True)

df = load_data()

# --- 3. 初始化 Session State ---
if df.empty:
    st.error("❌ 找不到 CSV 檔案，請確認 HWG1-100.csv 或 HWG101-200.csv 是否在目錄中。")
    st.stop()

if 'quiz_data' not in st.session_state:
    sample_size = min(len(df), 10)
    st.session_state.quiz_data = df.sample(n=sample_size).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if st.session_state.current_idx < len(st.session_state.quiz_data):
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    # 因為前面統一轉了小寫，這裡用小寫 key 抓取
    q_id_val = q.get('id', 0)
    q_text = q.get('question', '')
    
    # 建立選項映射
    opts_map = {
        'A': str(q.get('a', '')),
        'B': str(q.get('b', '')),
        'C': str(q.get('c', ''))
    }
    
    # 針對你的 Answerkey 欄位進行對位 (已轉小寫)
    correct_key = str(q.get('answerkey', q.get('answer', ''))).strip().upper()

    st.markdown(f'<p class="question-header">第 {st.session_state.current_idx + 1} / 10 題</p>', unsafe_allow_html=True)
    st.write("## 聽聽看，哪一個是對的？")
    
    qid_str = str(q_id_val).zfill(3)
    audio_path = f"audio/q_{qid_str}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    # 選項按鈕
    option_keys = ['A', 'B', 'C']
    for i, key in enumerate(option_keys):
        option_text = opts_map[key]
        if st.button(f"{key}. {option_text}", key=f"btn_{st.session_state.current_idx}_{i}", use_container_width=True):
            
            # 正確答案的文字
            correct_text = opts_map.get(correct_key, "答案設定錯誤")
            is_correct = (key == correct_key)
            
            st.session_state.results.append({
                "question": q_text,
                "user_choice": option_text,
                "correct_answer": correct_text,
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 5. 結果頁面 ---
else:
    st.balloons()
    st.header("🏆 練習結束囉！")
    
    score_count = sum(1 for item in st.session_state.results if item['is_correct'])
    total_q = len(st.session_state.results)
    final_score = int((score_count / total_q) * 100)
    st.subheader(f"得分：{final_score} 分 (答對 {score_count} 題)")

    # 製作複製報告
    wrong_details = []
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_details.append(f"Q{i+1}: {item['question']}\n   ❌ 你的回答: {item['user_choice']}\n   ✅ 正確答案: {item['correct_answer']}")
    
    report_text = f"我的英文測驗成績：{final_score} 分\n" + "\n".join(wrong_details)

    st.components.v1.html(f"""
        <button id="copyBtn" style="background-color:white; color:#007bff; border:3px solid #8bc3
