import streamlit as st
import pandas as pd
import random
import os

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

# --- 1. 讀取資料 (包含編碼偵錯) ---
@st.cache_data
def load_data():
    file_name = "HWG1-100.csv"
    try:
        # 先嘗試 UTF-8
        df = pd.read_csv(file_name, encoding='utf-8-sig')
    except:
        # 若失敗則嘗試 Big5 (台灣 Excel 常見格式)
        df = pd.read_csv(file_name, encoding='big5')
    return df

df = load_data()

# --- 2. 初始化 Session State ---
if 'quiz_data' not in st.session_state:
    # 隨機選 10 題
    st.session_state.quiz_data = df.sample(n=10).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = [] # 儲存答題狀況

# --- 3. 測驗介面 ---
if st.session_state.current_idx < 10:
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    st.markdown(f'<p class="question-text">聽聽看，哪一個是對的？</p>', unsafe_allow_html=True)
    
    # 音檔處理：補零成 q_001.mp3 格式
    qid = str(q['id']).zfill(3)
    audio_path = f"audio/q_{qid}.mp3"
    
    # 防錯：如果音檔不存在，顯示警告而不是讓程式崩潰
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    # 準備選項
    opts = [q['option_a'], q['option_b'], q['option_c']]
    
    # 建立大按鈕供點擊
    for opt in opts:
        if st.button(opt):
            # 比對 answerkey 欄位
            # 加上 strip() 防止 Excel 裡有看不見的空白
            is_correct = (str(opt).strip() == str(q['answerkey']).strip())
            
            st.session_state.results.append({
                "question": q['question'],
                "user_choice": opt,
                "correct_answer": q['answerkey'],
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
    
    for item in st.session_state.results:
        if item['is_correct']:
            score += 1
        else:
            wrong_list.append(f"題目：{item['question']}\n你的答案：{item['user_choice']}\n正確答案：{item['correct_answer']}\n---")

    st.subheader(f"得分：{score} / 10")

    if wrong_list:
        st.write("### ❌ 錯題記錄 (可複製下方內容)")
        wrong_text = "\n".join(wrong_list)
        st.text_area("選取並複製：", value=wrong_text, height=300)
    else:
        st.success("太棒了！全部正確！")

    if st.button("再測驗一次"):
        # 清除資料重新開始
        del st.session_state.quiz_data
        st.rerun()
