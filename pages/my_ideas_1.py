# pages/my_ideas.py
import streamlit as st

def show():
    st.write("# My Ideas - Debug Version")
    
    # Debug: Show what's in session state
    st.write("## Debug Info:")
    st.write(f"Session state keys: {list(st.session_state.keys())}")
    
    if "saved_ideas" in st.session_state:
        st.write(f"✅ saved_ideas exists")
        st.write(f"Number of saved ideas: {len(st.session_state.saved_ideas)}")
        st.write(f"Saved IDs: {st.session_state.saved_ideas}")
    else:
        st.write("❌ saved_ideas does NOT exist in session state")
    
    if "home_docs" in st.session_state:
        st.write(f"✅ home_docs exists")
        st.write(f"Total documents: {len(st.session_state.home_docs)}")
    else:
        st.write("❌ home_docs does NOT exist")
    
    # Try to show saved ideas
    st.write("---")
    st.write("## Attempting to show saved ideas:")
    
    try:
        if "saved_ideas" in st.session_state and st.session_state.saved_ideas:
            import pandas as pd
            all_docs = st.session_state.home_docs.copy()
            saved_df = all_docs[all_docs["id"].isin(st.session_state.saved_ideas)]
            
            st.write(f"Found {len(saved_df)} saved ideas in dataframe")
            st.dataframe(saved_df)
        else:
            st.info("No saved ideas yet")
    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    show()
