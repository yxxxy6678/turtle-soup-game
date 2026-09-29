import streamlit as st
import json
import re
from llm import llm_call
from prompts import GENERATE_SOUP_PROMPT, HOST_PROMPT_TPL

def create_new_game():
    """生成新一局海龟汤，返回汤面、汤底，增加JSON清洗"""
    msgs = [{"role":"user", "content":GENERATE_SOUP_PROMPT}]
    resp = llm_call(msgs, temperature=0.8)
    raw = resp.choices[0].message.content
    # 清洗：移除markdown代码块标记、换行空格
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw, re.DOTALL)
    if match:
        raw = match.group(1)
    raw = raw.strip()
    data = json.loads(raw)
    return data["soup_surface"], data["soup_answer"]

def host_answer(truth:str, question:str):
    """主持人根据汤底回答玩家问题"""
    prompt = HOST_PROMPT_TPL.format(truth=truth, user_question=question)
    msgs = [{"role":"user","content":prompt}]
    resp = llm_call(msgs, temperature=0.0)
    return resp.choices[0].message.content.strip()

# ---------------- streamlit页面 ----------------
st.set_page_config(page_title="AI海龟汤小游戏｜实验五综合项目", layout="wide")
st.title("🐢 AI海龟汤推理小游戏")

# 初始化会话状态
if "game_ready" not in st.session_state:
    st.session_state["game_ready"] = False
    st.session_state["surface"] = ""
    st.session_state["answer"] = ""
    st.session_state["chat_history"] = []

with st.sidebar:
    st.header("游戏控制面板")
    if st.button("🎲开启新一局海龟汤"):
        try:
            surf, ans = create_new_game()
            st.session_state["surface"] = surf
            st.session_state["answer"] = ans
            st.session_state["chat_history"] = []
            st.session_state["game_ready"] = True
        except Exception as e:
            st.error(f"生成海龟汤失败，请重试！错误：{e}")

    if st.button("🔮揭晓汤底（看答案）"):
        if st.session_state["game_ready"]:
            st.session_state["chat_history"].append(
                {"role":"assistant", "content":f"✅【汤底真相】：{st.session_state['answer']}"}
            )

# 如果还没开局
if not st.session_state["game_ready"]:
    st.info("👈请在左侧侧边栏点击【🎲开启新一局海龟汤】开始游戏！")
else:
    # 显示汤面
    st.subheader("📜汤面（谜题）")
    st.info(st.session_state["surface"])
    st.divider()

    # 渲染历史对话
    for item in st.session_state["chat_history"]:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    user_q = st.chat_input("请输入你的推理提问，例如：死者是自杀吗？")
    if user_q:
        st.session_state["chat_history"].append({"role":"user", "content":user_q})
        with st.chat_message("user"):
            st.markdown(user_q)

        with st.chat_message("assistant"):
            with st.spinner("主持人思考中..."):
                res = host_answer(st.session_state["answer"], user_q)
                st.markdown(res)
        st.session_state["chat_history"].append({"role":"assistant", "content":res})
