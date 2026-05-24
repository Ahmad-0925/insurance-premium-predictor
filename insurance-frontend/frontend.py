import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Insurance Premium Predictor", page_icon="🏥")
st.title("🏥 Insurance Premium Predictor")

if "token" not in st.session_state:
    st.session_state.token = ""

if not st.session_state.token:

    page = st.radio("", ["🔐 Login", "📝 Signup"], horizontal=True)
    st.divider()

    if page == "🔐 Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not username or not password:
                st.warning("Please enter username and password.")
            else:
                try:
                    res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
                    data = res.json()
                    if "token" in data:
                        st.session_state.token = data["token"]
                        st.rerun()
                    else:
                        st.error(data.get("detail", "Invalid credentials."))
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    elif page == "📝 Signup":
        st.subheader("Create Account")
        new_username = st.text_input("Choose Username")
        new_password = st.text_input("Choose Password", type="password")

        if st.button("Signup"):
            if not new_username or not new_password:
                st.warning("Please fill all fields.")
            else:
                try:
                    res = requests.post(f"{API_URL}/signup", json={"username": new_username, "password": new_password})
                    data = res.json()
                    if "message" in data:
                        st.success("Account created! Please login now.")
                    else:
                        st.error(data.get("detail", "Error"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")

else:
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Logout"):
            st.session_state.token = ""
            st.rerun()

    page = st.radio("", ["📋 Predict", "📂 History"], horizontal=True)
    st.divider()

    if page == "📋 Predict":
        st.subheader("Predict Insurance Premium")

        age = st.number_input("Age", min_value=1, max_value=119, value=30)
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
        height = st.number_input("Height (meters)", min_value=0.5, max_value=2.49, value=1.70, format="%.2f")
        income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=8.0)
        smoker = st.selectbox("Smoker?", [False, True], format_func=lambda x: "Yes" if x else "No")
        city = st.text_input("City", placeholder="e.g. Mumbai, Delhi")
        occupation = st.selectbox("Occupation", ['business', 'employee', 'freelancer', 'retired', 'student'])

        payload = {
            "age": age, "weight": weight, "height": height,
            "income_lpa": income_lpa, "smoker": smoker,
            "city": city, "occupation": occupation
        }

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Predict"):
                if not city.strip():
                    st.warning("Please enter your city.")
                else:
                    with st.spinner("Predicting..."):
                        try:
                            res = requests.post(
                                f"{API_URL}/secure-predict",
                                headers={"authorization": st.session_state.token},
                                json=payload
                            )
                            result = res.json()
                            category = result.get("predicted_category", "—")
                            confidence = result.get("confidence", 0)
                            probs = result.get("class_probabilities", {})
                            emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(category, "⚪")
                            st.success(f"Result: {emoji} **{category}** Premium")
                            st.metric("Confidence", f"{confidence*100:.1f}%")
                            if probs:
                                st.write("**Probability Breakdown:**")
                                for label, prob in probs.items():
                                    st.progress(prob, text=f"{label}: {prob*100:.1f}%")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with col2:
            if st.button("💾 Predict & Save"):
                if not city.strip():
                    st.warning("Please enter your city.")
                else:
                    with st.spinner("Saving..."):
                        try:
                            res = requests.post(f"{API_URL}/predict-save", json=payload)
                            result = res.json()
                            pred = result.get("prediction", {})
                            if isinstance(pred, dict):
                                category = pred.get("predicted_category", "—")
                                confidence = pred.get("confidence", 0)
                                probs = pred.get("class_probabilities", {})
                            else:
                                category = str(pred)
                                confidence = 0
                                probs = {}
                            emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(category, "⚪")
                            st.success(f"Saved! Result: {emoji} **{category}** Premium")
                            st.metric("Confidence", f"{confidence*100:.1f}%")
                            if probs:
                                st.write("**Probability Breakdown:**")
                                for label, prob in probs.items():
                                    st.progress(prob, text=f"{label}: {prob*100:.1f}%")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    elif page == "📂 History":
        st.subheader("Prediction History")

        if st.button("🔄 Load History"):
            try:
                res = requests.get(f"{API_URL}/history")
                data = res.json()
                if len(data) == 0:
                    st.info("No history found.")
                else:
                    for i, record in enumerate(reversed(data)):
                        pred = record.get("prediction", {})
                        inp = record.get("input", {})
                        if isinstance(pred, dict):
                            cat = pred.get("predicted_category", "—")
                            conf = pred.get("confidence", 0)
                        else:
                            cat = str(pred)
                            conf = 0
                        emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(cat, "⚪")
                        occ = inp.get("occupation", "—") if isinstance(inp, dict) else "—"
                        st.write(f"**Record {len(data)-i}** — {emoji} {cat} | Confidence: {conf*100:.1f}% | Occupation: {occ}")
                        st.divider()
            except Exception as e:
                st.error(f"Error: {str(e)}")