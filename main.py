import streamlit as st
import pandas as pd
from groq import Groq
from datetime import datetime

# --- Groq Setup ---
client = Groq(api_key="TUMHARI_GROQ_API_KEY_YAHAN_DALO")

st.set_page_config(page_title="FinTrack AI", page_icon="💰")
st.title("💰 FinTrack AI (Powered by Groq)")

# Data Storage (Session State)
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

# --- User Input Section ---
with st.container():
    user_input = st.text_input("Kahan kharch kiye? (e.g. '₹200 for Momos' or '500 ki nayi skin li')")
    
    if st.button("Add Record ➕"):
        if user_input:
            # Groq Prompt for Lllama-3.3-70b-versatile (Fast and Smart)
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Extract data from user text. Format: Amount|Category|Short_Description. Categories: Food, Games, School, Others. No prose, only format."
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model="llama-3.3-70b-versatile"
            )
            
            response = chat_completion.choices[0].message.content
            
            try:
                amt, cat, desc = response.strip().split("|")
                # Cleaning amount if it has ₹ or extra text
                amt = float(''.join(filter(str.isdigit, amt))) 
                
                new_row = {"Date": datetime.now().strftime("%d-%b"), "Description": desc, "Amount": amt, "Category": cat}
                st.session_state.expenses = pd.concat([st.session_state.expenses, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Noted: ₹{amt} for {desc} ({cat})")
            except Exception as e:
                st.error("Error: Try typing like '100 for snacks'")

# --- Dashboard Layout ---
st.divider()
if not st.session_state.expenses.empty:
    col1, col2, col3 = st.columns(3)
    
    total = st.session_state.expenses["Amount"].sum()
    waste = st.session_state.expenses[st.session_state.expenses["Category"].isin(["Games", "Others"])]["Amount"].sum()
    savings = total * 0.1  # Just an example logic

    col1.metric("Total Spends", f"₹{total}")
    col2.metric("Waste (Wants)", f"₹{waste}", delta="-High" if waste > (total/2) else "Normal")
    col3.metric("AI Advice", "Save More!" if waste > total/2 else "Good Job!")

    # Table & Chart
    st.dataframe(st.session_state.expenses, use_container_width=True)
    st.bar_chart(st.session_state.expenses.groupby("Category")["Amount"].sum())

    # Option to clear
    if st.button("Clear All Data"):
        st.session_state.expenses = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
        st.rerun()
