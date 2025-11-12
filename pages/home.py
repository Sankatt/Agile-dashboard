# pages/home.py
import streamlit as st
import pandas as pd
from datetime import date
from data.fake_docs import make_fake_docs, STATUSES
import streamlit.components.v1 as components

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

def get_selected_id(sel):
    # Caso 1: lista de dicts (comportamiento típico de st_aggrid)
    if isinstance(sel, list):
        return sel[0]["id"] if len(sel) > 0 else None
    # Caso 2: DataFrame de pandas
    try:
        import pandas as pd
        if isinstance(sel, pd.DataFrame):
            return sel.iloc[0]["id"] if not sel.empty else None
    except Exception:
        pass
    return None

def _init_state():
    if "home_docs" not in st.session_state:
        st.session_state.home_docs = make_fake_docs(35)
    # Initialize saved ideas list for current user
    # Try to restore from query params
    if "saved_ideas" not in st.session_state:
        saved_param = st.query_params.get("saved", "")
        if saved_param:
            try:
                st.session_state.saved_ideas = [int(x) for x in saved_param.split(",") if x]
            except:
                st.session_state.saved_ideas = []
        else:
            st.session_state.saved_ideas = []

def show():
    _init_state()

    # --- base df with real datetime for filtering
    df = st.session_state.home_docs.copy()
    for c in ["From date", "To date", "Date published"]:
        df[c] = pd.to_datetime(df[c])  # ensure dtype

    st.subheader("Documents")

    # -------- Filters
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    with c1:
        status = st.multiselect("Status", STATUSES, default=["Accepted"])
    with c2:
        fd = st.date_input("From date", value=None)
    with c3:
        td = st.date_input("To date", value=None)
    with c4:
        q = st.text_input("Search (name / doc / issue)")

    m = df["Status"].isin(status)
    if fd: m &= df["From date"] >= pd.to_datetime(fd)
    if td: m &= df["To date"] <= pd.to_datetime(td)
    if q:
        ql = q.lower()
        m &= (
            df["Document name"].str.lower().str.contains(ql) |
            df["Name"].str.lower().str.contains(ql) |
            df["Issue Number"].str.lower().str.contains(ql)
        )
    df = df[m].reset_index(drop=True)

    # -------- Copy to display: format dates as strings for the grid
    grid_df = df.copy()
    for c in ["From date", "To date", "Date published"]:
        grid_df[c] = grid_df[c].dt.strftime("%Y-%m-%d")   # or "%d/%m/%Y"

    # ---- AgGrid config
    gb = GridOptionsBuilder.from_dataframe(df)

  
    # Status value
    cell_style = JsCode("""
    function(params){
    const v = params.value;
    const base = {'border-radius':'999px','padding':'2px 8px','font-weight':'600','display':'inline-block'};
    if (v === 'On Review') return {...base, 'background':'#e6f0ff','color':'#1d4ed8', 'textAlign':'center'};
    if (v === 'Accepted')  return {...base, 'background':'#e9f9ee','color':'#079455', 'textAlign':'center'};
    if (v === 'Rejected')  return {...base, 'background':'#ffeaea','color':'#ce2b2b', 'textAlign':'center'};
    return base;
    }
    """)
    gb.configure_column("Status", cellStyle=cell_style, width=140)
    gb.configure_selection(
        selection_mode='single',   # one single line
        use_checkbox=True          # checkboxes
    )

    grid_opts = gb.build()
    grid_opts["domLayout"] = "normal"
    grid_opts["pagination"] = True
    grid_opts["paginationPageSize"] = 10
    grid_opts["suppressRowClickSelection"] = True
    grid_opts["rowSelection"] = "single"
    grid_opts["quickFilterText"] = q or ""

    resp = AgGrid(
        df,
        gridOptions=grid_opts,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=520,
        theme="balham"
    )
    # ---- Action bar out of the iframe
    sel = resp.get("selected_rows", [])
    selected_id = get_selected_id(sel)

    # Check if the selected idea is already saved
    is_saved = selected_id in st.session_state.saved_ideas if selected_id else False

    c1, c2, c3, c4 = st.columns([1,1,1,1])
    with c1:
        st.button("🔎 Open", disabled=selected_id is None,
                on_click=lambda: (_ for _ in ()).throw(SystemExit))  # placeholder 
    with c2:
        # Save/Unsave button
        if is_saved:
            if st.button("💔 Unsave", disabled=selected_id is None):
                st.session_state.saved_ideas.remove(selected_id)
                # Update localStorage
                unsave_html = f"""
                <script>
                const savedIds = {st.session_state.saved_ideas};
                localStorage.setItem('saved_ideas', JSON.stringify(savedIds));
                </script>
                """
                components.html(unsave_html, height=0)
                # Update query params
                if st.session_state.saved_ideas:
                    st.query_params["saved"] = ",".join(map(str, st.session_state.saved_ideas))
                else:
                    st.query_params.pop("saved", None)
                st.success("Idea removed from your personal list!")
                st.rerun()
        else:
            if st.button("❤️ Save", disabled=selected_id is None):
                if selected_id not in st.session_state.saved_ideas:
                    st.session_state.saved_ideas.append(selected_id)
                    # Save to localStorage
                    save_html = f"""
                    <script>
                    const savedIds = {st.session_state.saved_ideas};
                    localStorage.setItem('saved_ideas', JSON.stringify(savedIds));
                    </script>
                    """
                    components.html(save_html, height=0)
                    # Persist to query params
                    st.query_params["saved"] = ",".join(map(str, st.session_state.saved_ideas))
                    st.success("✅ New idea saved to your personal list!")
                st.rerun()
    with c3:
        if st.button("✏️ Edit selected", disabled=selected_id is None):
            st.query_params["page"] = "My Ideas"
            st.query_params["edit_id"] = str(selected_id)
            st.rerun()
    with c4:
        if st.button("🗑 Delete", disabled=selected_id is None):
            st.query_params["page"] = "Home"
            st.query_params["delete_id"] = str(selected_id)
            st.rerun()
