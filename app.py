import streamlit as st
import pandas as pd
import random
import os

# --- 設定網頁樣式 (包含顏色與字體) ---
st.markdown("""
    <style>
    /* 選項大按鈕 */
    .stButton>button {
        width: 100%;
        height: 3.5em;
        font-size: 26px !important;
        margin-bottom: 15px;
        border-radius: 10px;
    }
    /* 再玩一次按鈕 (綠色) */
    div.stButton > button:first-child[kind="secondary"] {
        background-color: #28a745;
        color: white;
    }
    /* 複製成績按鈕 (藍色) */
    .copy-btn {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 32px !important;
        font-weight: bold;
        color: #2E4053;
    }
    .score-text {
        font-size: 40px;
        font-weight: bold;
        color: #E74C3C;
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
    st.session_state.quiz_data = df.sample(n=10).to_dict('records')
    st.session_state.current_idx = 0
    st.session_state.results = []

# --- 3. 測驗介面 ---
if st.session_state.current_idx < 10:
    q = st.session_state.quiz_data[st.session_state.current_idx]
    q_vals = list(q.values())
    
    st.write(f"### 第 {st.session_state.current_idx + 1} / 10 題")
    st.markdown('<p class="question-text">聽聽看，哪一個是對的？</p>', unsafe_allow_html=True)
    
    # 提示語速 (Streamlit 原生播放器可由用戶在右側三點選單手動調整速度)
    st.info("💡 小撇步：如果覺得太快，點擊音檔右邊的三個點 [⋮] 可以調整「播放速度」喔！")
    
    qid = str(q_vals[0]).zfill(3)
    audio_path = f"audio/q_{qid}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    option_texts = [q_vals[2], q_vals[3], q_vals[4]]
    option_keys = ['A', 'B', 'C']
    
    for i in range(len(option_texts)):
        if st.button(str(option_texts[i]), key=f"btn_{i}"):
            user_choice_key = option_keys[i]
            correct_key = str(q_vals[5]).strip().upper()
            is_correct = (user_choice_key == correct_key)
            
            st.session_state.results.append({
                "question_text": q_vals[1],
                "user_choice_text": option_texts[i],
                "correct_answer_key": correct_key,
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 4. 結果頁面 ---
else:
    st.balloons()
    st.header("練習結束囉！")
    
    wrong_list = []
    score_count = 0
    
    # 恢復原本的文字顯示樣式
    st.write("### 📝 答題詳情：")
    for item in st.session_state.results:
        if item['is_correct']:
            score_count += 1
            st.write(f"✅ 題目：{item['question_text']} (正確)")
        else:
            msg = f"❌ 題目：{item['question_text']}\n你的回答：{item['user_choice_text']}\n正確答案代號：{item['correct_answer_key']}"
            st.write(msg)
            wrong_list.append(msg)
            st.write("---")

    final_score = score_count * 10
    st.markdown(f'<p class="score-text">最終得分：{final_score} 分</p>', unsafe_allow_html=True)

    # 製作報表文字
    report_text = f"老師好！我的練習成績是：{final_score} 分\n"
    if wrong_list:
        report_text += "【錯題記錄】\n" + "\n".join(wrong_list)
    else:
        report_text += "全部都答對了！🌟"

    # --- 自定義「點擊即複製」按鈕 (JavaScript 實作) ---
    # 這裡做出你圖片中的樣式：綠色框、藍色字
    st.components.v1.html(f"""
        <div style="text-align:center;">
            <button id="copyBtn" style="
                background-color: white;
                color: #007bff;
                border: 3px solid #8bc34a;
                padding: 15px 30px;
                font-size: 24px;
                font-weight: bold;
                border-radius: 20px;
                cursor: pointer;
                width: 100%;
            ">
                按我複製成績給老師
            </button>
        </div>
        <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = `{report_text}`;
                navigator.clipboard.writeText(text).then(function() {{
                    document.getElementById('copyBtn').innerText = '✅ 複製成功！';
                    document.getElementById('copyBtn').style.borderColor = '#28a745';
                    setTimeout(function() {{
                        document.getElementById('copyBtn').innerText = '按我複製成績給老師';
                        document.getElementById('copyBtn').style.borderColor = '#8bc34a';
                    }}, 2000);
                }});
            }};
        </script>
    """, height=100)

    st.write("---")

    # --- 綠色再玩一次按鈕 ---
    st.markdown('<div class="green-btn">', unsafe_allow_html=True)
    if st.button("再玩一次"):
        del st.session_state.quiz_data
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
