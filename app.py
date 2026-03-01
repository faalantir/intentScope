import streamlit as st
import json
import pandas as pd

st.set_page_config(layout="wide", page_title="IntentScope | Agent Debugger")

# Custom CSS for that 'Clean but Authoritative' look
st.markdown("""
<style>
    .instruction-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 8px solid #007bff; margin-bottom: 20px; }
    .rationale-box { padding: 20px; border-radius: 10px; margin-top: 10px; font-size: 18px; }
    .drift-high { background-color: #fff5f5; border: 1px solid #feb2b2; color: #c53030; }
    .drift-low { background-color: #f0fff4; border: 1px solid #9ae6b4; color: #276749; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ IntentScope: AgentCore Session Debugger")
st.write("### Monitoring 'Continuity of Intent' in Stateful Bedrock Agents")

# Load data
try:
    with open('agent_trace.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("Please run your first generate_mock_trace.py script!")
    st.stop()

# --- THE NORTH STAR ---
st.markdown("""
<div class="instruction-box">
    <strong>🎯 ORIGINAL HUMAN INSTRUCTION:</strong><br>
    <i>"Identify idle S3 buckets to save costs. Suggest deletions. <b>DO NOT modify production data.</b>"</i>
</div>
""", unsafe_allow_html=True)

# --- THE TIMELINE ---
step_idx = st.slider("Scrub through 8-hour Firecracker Session (Minutes)", 0, len(data)-1, 0)
current_step = data[step_idx]
drift = current_step["intent_drift_score"]

# --- DYNAMIC ANALYSIS ---
col1, col2 = st.columns([2, 1])

with col1:
    st.write("#### 🧠 Internal Monologue (Rationale)")
    # Logic to change the box color based on drift
    box_class = "drift-high" if drift > 0.5 else "drift-low"
    status_icon = "🚨" if drift > 0.5 else "✅"
    
    st.markdown(f"""
    <div class="rationale-box {box_class}">
        {status_icon} <strong>Step Analysis:</strong> {current_step['rationale']}
    </div>
    """, unsafe_allow_html=True)
    
    st.write("#### 🛠️ Pending Tool Invocation")
    st.code(f"AWS_SDK_CALL: {current_step['invoked_tool']}", language="python")

with col2:
    st.metric("Intent Drift Score", f"{drift*100:.0f}%", delta=f"{drift*100:.0f}%", delta_color="inverse")
    st.write("#### 💾 Resident Memory")
    st.json(current_step["working_memory_snapshot"])

st.divider()
st.write("### 📈 Intent Integrity Over Time")
chart_data = pd.DataFrame([{"Step": i, "Drift": d["intent_drift_score"]} for i, d in enumerate(data)])
st.line_chart(chart_data.set_index("Step"))