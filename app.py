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
        height: auto !important;
        padding: 15px 20px !important;
        background-color: white !important;
        border: 2px solid #eee !important;
        border-radius: 15px !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
    }
    div.stButton > button p {
        font-size: 22px !important;
        font-weight: bold !important;
        text-align: left !important;
        white-space: pre-wrap !important; 
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
            except:
                temp_df = pd.read_csv(file_name, encoding='big5')
            
            # 統一欄位名稱為小寫並去空格，確保 Answerkey 與 answer 能對應
            temp_df.columns = [c.strip().lower() for c in temp_df.columns]
            df_list.append(temp_df)
    
    return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()

df = load_data()

# --- 3. 初始化 Session ---
if df.empty:
    st.error("❌ 找不到 CSV 檔案，請確認檔案已上傳。")
    st.stop()

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = df.sample(n=min(len(df), 10)).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if st.session_state.current_idx < len(st.session_state.quiz_data):
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    # 讀取欄位 (已轉小寫)
    q_id = str(q.get('id', 0)).zfill(3)
    q_text = q.get('question', '')
    
    opts_map = {
        'A': str(q.get('a', '')),
        'B': str(q.get('b', '')),
        'C': str(q.get('c', ''))
    }
    
    # 支援 answerkey 或 answer 欄位
    correct_key = str(q.get('answerkey', q.get('answer', ''))).strip().upper()

    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    
    audio_path = f"audio/q_{q_id}.mp3"
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"找不到音檔: {audio_path}")

    for key in ['A', 'B', 'C']:
        if st.button(f"{key}. {opts_map[key]}", key=f"btn_{st.session_state.current_idx}_{key}", use_container_width=True):
            is_correct = (key == correct_key)
            st.session_state.results.append({
                "question": q_text,
                "user_choice": opts_map[key],
                "correct_answer": opts_map.get(correct_key, "答案設定錯誤"),
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 5. 結果頁面 ---
else:
    st.header("🏆 練習結束囉！")
    score = sum(1 for item in st.session_state.results if item['is_correct'])
    final_score = score * 10
    st.subheader(f"得分：{final_score} 分")

    # 製作報告文字
    wrong_txt = ""
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_txt += f"Q{i+1}: {item['question']}\\n❌回答: {item['user_choice']}\\n✅正確: {item['correct_answer']}\\n\\n"
    
    report_text = f"我的英文測驗成績：{final_score} 分\\n{wrong_txt}"

    # 修改後的複製按鈕，避免 f-string 引號衝突
    html_code = f"""
        <button id="copyBtn" style="background-color:white; color:#007bff; border:3px solid #8bc34a; padding:15px; font-size:22px; font-weight:bold; border-radius:20px; width:100%; cursor:pointer;">
            按我複製成績給老師
        </button>
        <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = "{report_text}";
                navigator.clipboard.writeText(text.replace(/\\\\n/g, '\\n')).then(function() {{
                    document.getElementById('copyBtn').innerText = '✅ 複製成功！';
                    setTimeout(function() {{ document.getElementById('copyBtn').innerText = '按我複製成績給老師'; }}, 2000);
                }});
            }};
        </script>
    """
    st.components.v1.html(html_code, height=100)

    st.write("---")
    for i, item in enumerate(st.session_state.results):
        if item['is_correct']:
            st.success(f"**Q{i+1}: {item['question']}** \n\n 你的回答: {item['user_choice']} ✅")
        else:
            st.error(f"**Q{i+1}: {item['question']}** \n\n 你的回答: {item['user_choice']} ❌ \n\n 正確答案: {item['correct_answer']}")

    if st.button("再玩一次", use_container_width=True):
        del st.session_state.quiz_data
        st.rerun()
