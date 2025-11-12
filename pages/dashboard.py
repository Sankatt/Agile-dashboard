import streamlit as st
from styles import dashboard as dashboard_styles
from pages.header import show_header
from pages import home as home_page
from pages import _my_ideas as my_ideas_page

def _qp_get(name, default=None):
    v = st.query_params.get(name, default)
    # Normalize list -> first element
    if isinstance(v, (list, tuple)):
        return v[0] if v else default
    return v

def show():
    """Display the dashboard page with header and content"""
    
    st.set_page_config(layout="wide")
    # Load dashboard-specific CSS
    dashboard_styles.load_css()
   
    # Render header and get active tab from URL
    show_header()

    # --- read and normalize QPs
    active_qp = _qp_get("page")
    active_ss = st.session_state.get("active_tab")
    active = active_qp or active_ss or "Home"

    edit_id_qp = _qp_get("edit_id")
    if edit_id_qp is not None:
        try:
            st.session_state["edit_id"] = int(edit_id_qp)
        except Exception:
            st.session_state["edit_id"] = str(edit_id_qp)


    # Save active tab to session state
    st.session_state["active_tab"] = active
   

    # ===== Content based on active tab =====
    st.markdown('<div class="dashboard-content">', unsafe_allow_html=True)
    
    if active == "Home":
        home_page.show()
    elif active == "My Ideas":
         if "edit_id" in st.session_state:
            st.write(f"✏️ Editing idea ID: {st.session_state['edit_id']}")
            #TODO: EDIT PAGE
         else:
            # Show My Ideas page
            my_ideas_page.show()
    elif active == "Ideas":
          if "edit_id" in st.session_state:
            st.write(f"✏️ Editing idea ID: {st.session_state['edit_id']}")
          else:
            st.write("🧠 Ideas page.")
    else:
        st.write("🏠 Home content here.")
    
    st.markdown('</div>', unsafe_allow_html=True)
