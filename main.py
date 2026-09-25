"""Bangalore Explorer: Streamlit entry point.

Run with:  streamlit run main.py
"""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st
from mysql.connector import Error as MySQLError

from explorer import db
from explorer.planner import CATEGORIES, TRANSPORT_RESERVE, PlannerInputError, build_trip_query, parse_budget
from explorer.security import validate_signup

MAX_LOGIN_ATTEMPTS = 5

st.set_page_config(page_title="Bangalore Explorer", page_icon="🗺️", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem; max-width: 1200px;}
      .hero h1 {margin-bottom: 0.2rem;}
      .hero p {opacity: .75; margin-top: 0;}
      .stop {padding: .75rem 1rem; border: 1px solid rgba(128,128,128,.25);
             border-radius: 8px; margin-bottom: .5rem;}
      .stop b {font-size: 1.02rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def esc(value) -> str:
    return html.escape(str(value))


# ------------------------------------------------------------------ auth ---
def auth_sidebar() -> None:
    st.sidebar.title("Account")
    if st.session_state.get("user"):
        st.sidebar.success(f"Signed in as **{st.session_state.user}**")
        if st.sidebar.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return

    login_tab, signup_tab = st.sidebar.tabs(["Sign in", "Create account"])

    with login_tab.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Sign in", use_container_width=True):
            attempts = st.session_state.get("failed_logins", 0)
            if attempts >= MAX_LOGIN_ATTEMPTS:
                st.error("Too many failed attempts. Reload the page to try again.")
            else:
                try:
                    valid = db.authenticate(username.strip(), password)
                except MySQLError:
                    st.error("Couldn't reach the database. Try again shortly.")
                    return
                if valid:
                    st.session_state.user = username.strip()
                    st.session_state.failed_logins = 0
                    st.rerun()
                st.session_state.failed_logins = attempts + 1
                st.error("Incorrect username or password.")

    with signup_tab.form("signup"):
        username = st.text_input("Username", key="su_user")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pw")
        confirm = st.text_input("Confirm password", type="password", key="su_pw2")
        if st.form_submit_button("Create account", use_container_width=True):
            errors = validate_signup(username.strip(), email.strip(), password, confirm)
            if errors:
                for e in errors:
                    st.error(e)
                return
            try:
                created = db.create_user(username.strip(), email.strip(), password)
            except MySQLError:
                st.error("Couldn't reach the database. Try again shortly.")
                return
            if created:
                st.success("Account created. You can sign in now.")
            else:
                st.error("That username or email is already registered.")


# --------------------------------------------------------------- planner ---
def planner() -> None:
    st.markdown(
        '<div class="hero"><h1>Plan a day out in Bangalore</h1>'
        "<p>Pick what you feel like doing and your budget. You'll get combinations in the same "
        "area and the buses that get you there.</p></div>",
        unsafe_allow_html=True,
    )

    with st.form("plan"):
        c1, c2, c3 = st.columns([2, 1, 1])
        location = c1.text_input("Area (optional)", placeholder="e.g. Indiranagar")
        min_budget = c2.text_input("Minimum budget (₹)", value="0")
        max_budget = c3.text_input("Maximum budget (₹)", value="1500")
        picks = st.multiselect("What do you want to do?", list(CATEGORIES), default=["Restaurants"])
        submitted = st.form_submit_button("Find plans", type="primary")

    if submitted:
        try:
            low, high = parse_budget(min_budget, max_budget)
            query = build_trip_query(picks, low, high, location)
            rows = db.run_trip_query(query)
        except PlannerInputError as exc:
            st.warning(str(exc))
            return
        except MySQLError:
            st.error("Couldn't reach the database. Check the connection settings and try again.")
            return
        st.session_state.results = pd.DataFrame(rows, columns=query.columns)
        st.session_state.picks = picks

    df = st.session_state.get("results")
    if df is None:
        return
    if df.empty:
        st.info("No plans fit that budget and area. Try widening the budget or clearing the area.")
        return

    picks = st.session_state.picks
    m1, m2, m3 = st.columns(3)
    m1.metric("Plans found", len(df))
    m2.metric("Cheapest", f"₹{int(df['Total (₹)'].min()):,}")
    m3.metric("Kept for bus fare", f"₹{TRANSPORT_RESERVE}")

    st.dataframe(df, use_container_width=True, hide_index=True)

    choice = st.selectbox(
        "Choose a plan",
        df.index,
        format_func=lambda i: " + ".join(str(df.loc[i, p]) for p in picks) + f"  (₹{int(df.loc[i, 'Total (₹)']):,})",
    )
    plan = df.loc[choice]
    area = str(plan[f"{picks[0]} area"])

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Your plan")
        for p in picks:
            st.markdown(
                f'<div class="stop"><b>{esc(plan[p])}</b><br>'
                f"{esc(p)} · {esc(plan[p + ' area'])} · ₹{int(plan[p + ' price (₹)']):,}</div>",
                unsafe_allow_html=True,
            )
    with right:
        st.subheader("Getting there")
        try:
            buses = db.buses_for(area)
        except MySQLError:
            st.error("Couldn't load bus routes right now.")
        else:
            if buses:
                st.write(f"Buses that stop near **{area}**:")
                st.write(", ".join(f"`{b}`" for b in buses))
            else:
                st.write(f"No bus routes found for {area}.")


auth_sidebar()
if st.session_state.get("user"):
    planner()
else:
    st.title("Bangalore Explorer")
    st.write("Sign in or create an account from the sidebar to start planning.")
