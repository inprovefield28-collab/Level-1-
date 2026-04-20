import streamlit as st
import pandas as pd
import random
import os

# --- 設定網頁整體樣式 (淡粉色背景) ---
st.markdown("""
    <style>
    /* 整體背景色 */
    .stApp {
        background-color: #FFF0F5;
    }
    /* 選項大按鈕樣式 */
    .stButton>button {
        width: 100%;
        height: 3.5em;
        font-size: 26px !important;
        margin-bottom: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    /* 題目文字 */
    .question-text {
        font-size: 32px !important;
        font-weight: bold;
        color: #2E4053;
        text-align: center;
        margin-bottom: 20px;
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
    
    st.info("💡 小撇步：如果覺得太快，點擊音檔右邊的三個點 [⋮] 可以調整「播放速度」喔！")
    
    qid = str(q_vals[0]).zfill(3)
    audio_path = f"audio/q_{qid}.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning(f"⚠️ 找不到音檔：{audio_path}")

    # 假設欄位順序: 0:id, 1:question, 2:A, 3:B, 4:C, 5:answerkey
    option_texts = [q_vals[2], q_vals[3], q_vals[4]]
    option_keys = ['A', 'B', 'C']
    
    # 建立按鈕
    for i in range(len(option_texts)):
        if st.button(str(option_texts[i]), key=f"btn_{i}"):
            user_choice_key = option_keys[i]
            user_choice_text = option_texts[i]
            correct_key = str(q_vals[5]).strip().upper()
            
            # 找出正確答案的文字內容
            correct_text = ""
            if correct_key == 'A': correct_text = q_vals[2]
            elif correct_key == 'B': correct_text = q_vals[3]
            elif correct_key == 'C': correct_text = q_vals[4]

            is_correct = (user_choice_key == correct_key)
            
            # 紀錄詳細結果
            st.session_state.results.append({
                "question_text": q_vals[1],
                "user_choice_text": user_choice_text,
                "correct_text": correct_text,
                "is_correct": is_correct
            })
            st.session_state.current_idx += 1
            st.rerun()

# --- 4. 結果頁面 (模擬 image_5.png 風格) ---
else:
    st.balloons()
    
    # 計算分數
    score_count = sum(1 for item in st.session_state.results if item['is_correct'])
    final_score = score_count * 10

    # 製作報表文字 (供複製用)
    wrong_list_for_report = []
    for item in st.session_state.results:
        if not item['is_correct']:
            wrong_list_for_report.append(f"題目：{item['question_text']}\n你的回答：{item['user_choice_text']}\n正確答案：{item['correct_text']}\n---")
    
    report_text = f"老師好！我的練習成績是：{final_score} 分\n"
    if wrong_list_for_report:
        report_text += "【錯題記錄】\n" + "\n".join(wrong_list_for_report)
    else:
        report_text += "全部都答對了！🌟"

    # --- 開始 HTML/CSS 渲染 ---
    st.markdown("""
        <style>
        /* 結果頁面的中央卡片 */
        .result-container {
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            max-width: 600px;
            margin: auto;
            text-align: center;
        }
        /* 獎盃圖示和分數 */
        .trophy {
            font-size: 50px;
            margin-bottom: 10px;
        }
        .final-score {
            font-size: 80px;
            font-weight: bold;
            color: #FF69B4; /* 粉紅色分數 */
            margin: 0;
            line-height: 1;
        }
        .score-label {
            font-size: 20px;
            color: #888;
            margin-bottom: 20px;
        }
        /* 複製按鈕樣式 (綠框藍字) */
        .copy-btn-custom {
            background-color: white;
            color: #007bff;
            border: 3px solid #8bc34a;
            padding: 12px 24px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 50px; /* 橢圓形 */
            cursor: pointer;
            width: 100%;
            margin-bottom: 30px;
            transition: all 0.2s;
        }
        .copy-btn-custom:hover {
            background-color: #f0fdf4;
            transform: scale(1.02);
        }
        /* 答題細節區塊 */
        .detail-header {
            text-align: left;
            font-size: 18px;
            color: #555;
            margin-bottom: 15px;
            font-weight: bold;
        }
        /* 單條答題記錄卡片 */
        .record-card {
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            text-align: left;
            font-size: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        /* 正確的樣式 (淡綠背景) */
        .record-correct {
            background-color: #E8F5E9;
            border: 1px solid #C8E6C9;
            color: #2E7D32;
        }
        /* 錯誤的樣式 (淡紅背景) */
        .record-wrong {
            background-color: #FFEBEE;
            border: 1px solid #FFCDD2;
            color: #C62828;
        }
        .record-icon {
            font-size: 20px;
            margin-right: 10px;
        }
        .correct-ans-text {
            font-weight: bold;
            margin-top: 5px;
            display: block;
        }
        /* 再玩一次按鈕樣式 (綠色) */
        .stButton>button.green-restart-btn {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
            font-size: 20px !important;
            height: 3em !important;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 用一個大 Div 包住所有內容，模擬卡片風格
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    
    # 分數區頭部
    st.markdown('<div class="trophy">🏆</div>', unsafe_allow_html=True)
    st.markdown('<div>測驗結果</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="final-score">{final_score}</p>', unsafe_allow_html=True)
    st.markdown('<p class="score-label">總分 100</p>', unsafe_allow_html=True)

    # --- 自定義「點擊即複製」按鈕 (JavaScript) ---
    st.components.v1.html(f"""
        <button id="copyBtn" class="copy-btn-custom" style="
            background-color: white;
            color: #007bff;
            border: 3px solid #8bc34a;
            padding: 12px 24px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
        ">
            按我複製成績給老師
        </button>
        <script>
            document.getElementById('copyBtn').onclick = function() {{
                const text = `{report_text}`;
                navigator.clipboard.writeText(text).then(function() {{
                    document.getElementById('copyBtn').innerText = '✅ 複製成功！';
                    document.getElementById('copyBtn').style.backgroundColor = '#e8f5e9';
                    setTimeout(function() {{
                        document.getElementById('copyBtn').innerText = '按我複製成績給老師';
                        document.getElementById('copyBtn').style.backgroundColor = 'white';
                    }}, 2000);
                }});
            }};
        </script>
    """, height=80)

    # 答題詳情區
    st.markdown('---')
    st.markdown('<div class="detail-header">📝 答題詳情分析</div>', unsafe_allow_html=True)

    # 迴圈渲染每一題的結果卡片
    for i, item in enumerate(st.session_state.results):
        card_class = "record-correct" if item['is_correct'] else "record-wrong"
        icon = "✅" if item['is_correct'] else "❌"
        
        # 卡片內容 HTML
        card_html = f"""
            <div class="record-card {card_class}">
                <div>
                    <div><strong>Q{i+1}: {item['question_text']}</strong></div>
        """
        
        if item['is_correct']:
            card_html += f"<div>你的回答: {item['user_choice_text']}</div>"
        else:
            card_html += f"""
                    <div>你的回答: <span style="text-decoration: line-through;">{item['user_choice_text']}</span></div>
                    <div class="correct-ans-text">正確答案: {item['correct_text']}</div>
            """
            
        card_html += f"""
                </div>
                <div class="record-icon">{icon}</div>
            </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # 結束 result-container

    # --- 綠色再玩一次按鈕 ---
    st.write("") # 留白
    # 這裡借用 type="primary" 來標記，並用 CSS 強制改綠色
    if st.button("再玩一次", type="primary", key="restart_btn", use_container_width=True):
        st.markdown("""
            <style>
            button[kind="primary"] {
                background-color: #28a745 !important;
                border: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
        del st.session_state.quiz_data
        st.rerun()
