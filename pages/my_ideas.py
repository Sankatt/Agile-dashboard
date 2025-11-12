# pages/my_ideas.py
import streamlit as st

def show():
    st.write("# My Ideas Page")
    st.write("This is a test - if you see this, the file is loading correctly!")
    
    # Check if saved_ideas exists
    if "saved_ideas" in st.session_state:
        st.write(f"You have {len(st.session_state.saved_ideas)} saved ideas")
        st.write(st.session_state.saved_ideas)
    else:
        st.write("No saved ideas in session state yet")

# This is important - some Streamlit apps need this
if __name__ == "__main__":
    show()
