import streamlit as st
import pandas as pd
import random
import os

# --- 1. 設定網頁樣式 (Grid 強制置左版) ---
st.markdown("""
    <style>
    /* 強制按鈕樣式 */
    div.stButton > button {
        width: 100% !important;
        height: auto !important;
        padding: 10px 20px !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        border-radius: 15px !important;
        
        /* 確保內容從左邊開始 */
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
    }

    /* 強制按鈕內的文字標籤 */
    div.stButton > button p {
        font-size: 60px !important;
        font-weight: bold !important;
        text-align: left !important;
        /* 關鍵：保留空格 */
        white-space: pre !important; 
        margin: 0 !important;
        width: 100% !important;
    }
    
    audio { width: 100% !important; height: 80px !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 讀取資料 ---
@st.cache_data
def load_data():
    file_name = "HWG1-100.csv"
    try:
        df = pd.read_csv(file_name, encoding='utf-8-sig')
    except:
        df = pd.read_csv(file_name, encoding='big5')
    return df

df = load_data()

# --- 3. 初始化 Session State ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = df.sample(n=10).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 4. 測驗介面 ---
if st.session_state.current_idx < 10:
    q = st.session_state.quiz_data[st.session_state.current_idx]
    q_vals = list(q.values())
    
    st.markdown(f'<p class="question-header">第 {st.session_state.current_idx + 1} / 10 題</p>', unsafe_allow_html=True)
    st.write("## 聽聽看，哪一個是對的？")
    
    # 提示語速
    st.info("💡 如果覺得太快，點擊音檔右邊的三個點 [⋮] 可以調整速度喔！")
    
    qid = str(q_vals[0]).zfill(3)
    audio_path = f"audio/q_{qid}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    # 選項
    option_texts = [q_vals[2], q_vals[3], q_vals[4]]
    option_keys = ['A', 'B', 'C']
    
    for i in range(len(option_texts)):
        # 使用 use_container_width 確保滿版
        if st.button(f"{option_keys[i]}. {option_texts[i]}", key=f"btn_{i}", use_container_width=True):
            user_choice_key = option_keys[i]
            correct_key = str(q_vals[5]).strip().upper()
            
            correct_text = ""
            if correct_key == 'A': correct_text = q_vals[2]
            elif correct_key == 'B': correct_text = q_vals[3]
            elif correct_key == 'C': correct_text = q_vals[4]

            is_correct = (user_choice_key == correct_key)
            
            st.session_state.results.append({
                "question": q_vals[1],
                "user_choice": option_texts[i],
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
    final_score = score_count * 10
    st.subheader(f"得分：{final_score} 分")

    wrong_details = []
    for i, item in enumerate(st.session_state.results):
        if not item['is_correct']:
            wrong_details.append(f"Q{i+1}: {item['question']}\n回答: {item['user_choice']}\n正確: {item['correct_answer']}\n")
    
    report_text = f"我的成績：{final_score} 分\n" + "\n".join(wrong_details)

    # 複製按鈕
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
            st.success(f"Q{i+1}: {item['question']} \n\n 你的回答: {item['user_choice']} ✅")
        else:
            st.error(f"Q{i+1}: {item['question']} \n\n 你的回答: {item['user_choice']} ❌ \n\n 正確答案: {item['correct_answer']}")

    if st.button("再玩一次", use_container_width=True):
        del st.session_state.quiz_data
        st.rerun()
