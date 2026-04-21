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
                # 優先嘗試 utf-8-sig (處理 Excel 產生的 CSV BOM)
                temp_df = pd.read_csv(file_name, encoding='utf-8-sig')
                df_list.append(temp_df)
            except Exception:
                try:
                    temp_df = pd.read_csv(file_name, encoding='big5')
                    df_list.append(temp_df)
                except Exception as e:
                    st.error(f"讀取 {file_name} 時出錯: {e}")
    
    if not df_list:
        return pd.DataFrame()
    
    # 合併多個 CSV
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

df = load_data()

# --- 3. 初始化 Session State ---
if df.empty:
    st.error("❌ 找不到 CSV 檔案，請確認 HWG1-100.csv 或 HWG101-200.csv 是否在目錄中。")
    st.stop()

if 'quiz_data' not in st.session_state:
    # 從 1-200 題中隨機抽 10 題
    sample_size = min(len(df), 10)
    st.session_state.quiz_data = df.sample(n=sample_size).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if st.session_state.current_idx < len(st.session_state.quiz_data):
    q = st.session_state.quiz_data[st.session_state.current_idx]
    
    # 取得各欄位資料 (假設欄位順序: 0:id, 1:question, 2:A, 3:B, 4:C, 5:answer)
    # 使用 .get() 確保 key 不存在時不會報錯
    q_id_val = q.get('id', 0)
    q_text = q.get('question', '')
    options = [q.get('A', ''), q.get('B', ''), q.get('C', '')]
    correct_key = str(q.get('answer', '')).strip().upper()

    st.markdown(f'<p class="question-header">第 {st.session_state.current_idx + 1} / 10 題</p>', unsafe_allow_html=True)
    st.write("## 聽聽看，哪一個是對的？")
    
    st.info("💡 如果覺得太快，點擊音檔右邊的三個點 [⋮] 可以調整速度喔！")
    
    # 處理音檔路徑 (自動補零至三位數)
    qid_str = str(q_id_val).zfill(3)
    audio_path = f"audio/q_{qid_str}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path} (請確認 audio 資料夾內是否有此檔案)")

    # 選項按鈕
    option_keys = ['A', 'B', 'C']
    for i in range(len(options)):
        if st.button(f"{option_keys[i]}. {options[i]}", key=f"btn_{st.session_state.current_idx}_{i}", use_container_width=True):
            user_choice_key = option_keys[i]
            
            # 找出正確答案的文字內容
            correct_index = option_keys.index(correct_key) if correct_key in option_keys else 0
            correct_text = options[correct_index]

            is_correct = (user_choice_key == correct_key)
            
            st.session_state.results.append({
                "question": q_text,
                "user_choice": options[i],
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

    # 製作複製用的字串
    wrong_details = []
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_details.append(f"Q{i+1}: {item['question']}\n   ❌ 你的回答: {item['user_choice']}\n   ✅ 正確答案: {item['correct_answer']}")
    
    report_text = f"我的英文測驗成績：{final_score} 分\n" + "\n".join(wrong_details)

    # 複製按鈕組件
    st.components.v1.html(f"""
        <button id="copyBtn" style="background-color:white; color:#007bff; border:3px solid #8bc34a; padding:15px; font-size:22px; font-weight:bold; border-radius:20px; width:100%; cursor:pointer;">
            按我複製成績給老師
        </button>
        <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = `{report_text}`;
                navigator.clipboard.writeText(text).then(function() {{
                    document.getElementById('copyBtn').innerText = '✅ 複製成功！';
                    setTimeout(function() {{ document.getElementById('copyBtn').innerText = '按我複製成績給老師'; }}, 2000);
                }});
            }};
        </script>
    """, height=100)

    st.write("---")
    st.write("### 📝 答題詳情分析")

    for i, item in enumerate(st.session_state.results):
        if item['is_correct']:
            st.success(f"**Q{i+1}: {item['question']}** \n\n 你的回答: {item['user_choice']} ✅")
        else:
            st.error(f"**Q{i+1}: {item['question']}** \n\n 你的回答: {item['user_choice']} ❌ \n\n 正確答案: {item['correct_answer']}")

    if st.button("再玩一次", use_container_width=True):
        if 'quiz_data' in st.session_state:
            del st.session_state.quiz_data
        st.rerun()
