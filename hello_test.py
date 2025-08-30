import streamlit as st

st.title("Hello World Test!")
st.write("If you can see this, Streamlit is working!")
st.write("🎉 Success!")

name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello {name}!")

if st.button("Test Button"):
    st.balloons()
    st.success("Button clicked successfully!")