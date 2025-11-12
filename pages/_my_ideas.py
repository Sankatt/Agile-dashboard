# pages/my_ideas.py
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

def _init_state():
    # Initialize home_docs if it doesn't exist
    if "home_docs" not in st.session_state:
        from data.fake_docs import make_fake_docs
        st.session_state.home_docs = make_fake_docs(35)
    
    # Initialize saved_ideas if it doesn't exist
    # Try to restore from query params if available
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

    st.subheader("My Saved Ideas")
    
    # DEBUG INFO - Remove this later
    with st.expander("🔍 Debug Info", expanded=False):
        st.write(f"Query params: {dict(st.query_params)}")
        st.write(f"Saved ideas in session: {st.session_state.saved_ideas}")
        st.write(f"Number saved: {len(st.session_state.saved_ideas)}")
    
    # Check if user has saved any ideas
    if not st.session_state.saved_ideas:
        st.info("💡 You haven't saved any ideas yet. Go to the Home page to browse and save ideas you like!")
        st.write("")
        st.write("**How to save ideas:**")
        st.write("1. Go to the **Home** page")
        st.write("2. Select an idea by clicking the checkbox")
        st.write("3. Click the **❤️ Save** button below the table")
        st.write("4. Come back here to see your saved ideas!")
        return
    
    # Filter dataframe to show only saved ideas
    all_docs = st.session_state.home_docs.copy()
    saved_df = all_docs[all_docs["id"].isin(st.session_state.saved_ideas)].copy()
    
    if saved_df.empty:
        st.warning("⚠️ Your saved ideas are not available. They may have been deleted.")
        if st.button("Clear saved ideas list"):
            st.session_state.saved_ideas = []
            st.rerun()
        return
    
    # Format dates for display
    for c in ["From date", "To date", "Date published"]:
        if c in saved_df.columns:
            saved_df[c] = pd.to_datetime(saved_df[c], errors='coerce').dt.strftime("%Y-%m-%d")
    
    st.write(f"**You have {len(saved_df)} saved idea(s)** 💝")
    st.write("")
    
    # ---- AgGrid config
    gb = GridOptionsBuilder.from_dataframe(saved_df)
    
    # Status styling
    cell_style = JsCode("""
    function(params){
    const v = params.value;
    const base = {'border-radius':'999px','padding':'2px 8px','font-weight':'600','display':'inline-block'};
    if (v === 'On Review') return {...base, 'background':'#e6f0ff','color':'#1d4ed8', 'textAlign':'center'};
    if (v === 'Accepted')  return {...base, 'background':'#e9f9ee','color':'#079455', 'textAlign':'center'};
    if (v === 'Rejected')  return {...base, 'background':'#ffeaea','color':'#ce2b2b', 'textAlign':'center'};
    if (v === 'Draft')     return {...base, 'background':'#fff4e6','color':'#f59e0b', 'textAlign':'center'};
    return base;
    }
    """)
    gb.configure_column("Status", cellStyle=cell_style, width=140)
    gb.configure_selection(
        selection_mode='single',
        use_checkbox=True
    )
    
    grid_opts = gb.build()
    grid_opts["domLayout"] = "normal"
    grid_opts["pagination"] = True
    grid_opts["paginationPageSize"] = 10
    grid_opts["suppressRowClickSelection"] = True
    grid_opts["rowSelection"] = "single"
    
    resp = AgGrid(
        saved_df,
        gridOptions=grid_opts,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=400,
        theme="balham"
    )
    
    # Action buttons
    sel = resp.get("selected_rows", [])
    
    def get_selected_id(sel):
        if isinstance(sel, list):
            return sel[0]["id"] if len(sel) > 0 else None
        try:
            if isinstance(sel, pd.DataFrame):
                return sel.iloc[0]["id"] if not sel.empty else None
        except Exception:
            pass
        return None
    
    selected_id = get_selected_id(sel)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        st.button("🔎 Open", disabled=selected_id is None)
    
    with c2:
        if st.button("✏️ Edit", disabled=selected_id is None):
            # Navigate to edit page with the idea ID
            st.query_params["page"] = "edit_idea"
            st.query_params["edit_id"] = str(selected_id)
            st.rerun()
    
    with c3:
        if st.button("💔 Remove from Saved", disabled=selected_id is None):
            if selected_id in st.session_state.saved_ideas:
                st.session_state.saved_ideas.remove(selected_id)
                st.success("✅ Idea removed from your saved list!")
                st.rerun()
    
    # Show detailed view if an idea is selected
    if selected_id:
        st.divider()
        idea_row = saved_df[saved_df["id"] == selected_id].iloc[0]
        
        with st.expander("📄 Full Idea Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**ID:** {idea_row['id']}")
                st.write(f"**Name:** {idea_row['Name']}")
                st.write(f"**Category:** {idea_row['Category']}")
                st.write(f"**Status:** {idea_row['Status']}")
            
            with col2:
                if 'Issue Number' in idea_row:
                    st.write(f"**Issue Number:** {idea_row['Issue Number']}")
                if 'Document name' in idea_row:
                    st.write(f"**Document:** {idea_row['Document name']}")
                if 'Date published' in idea_row:
                    st.write(f"**Date Published:** {idea_row['Date published']}")
            
            if 'Description' in idea_row and str(idea_row['Description']) != 'nan':
                st.write(f"**Short Description:**")
                st.write(idea_row['Description'])
            
            if 'Detailed Description' in idea_row and str(idea_row['Detailed Description']) != 'nan':
                st.write(f"**Detailed Description:**")
                st.write(idea_row['Detailed Description'])
            
            if 'Estimated Impact / Target Audience' in idea_row and str(idea_row['Estimated Impact / Target Audience']) != 'nan':
                st.write(f"**Estimated Impact / Target Audience:**")
                st.write(idea_row['Estimated Impact / Target Audience'])

if __name__ == "__main__":
    show()
