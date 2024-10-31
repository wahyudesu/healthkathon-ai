import streamlit as st
import numpy as np

# Data dummmy
np.random.seed(42)  
import pandas as pd

data = pd.DataFrame({
    'baby_id': range(1, 101),  # 100 babies
    'category': np.random.choice(['stunting', 'at risk of stunting', 'healthy'], size=100),
    'age_months': np.random.randint(0, 24, size=100),  # Age in months
    'weight_kg': np.random.uniform(2.5, 10.0, size=100),  # Weight in kg
    'height_cm': np.random.uniform(45, 90, size=100)  # Height in cm
})

columns_list = list(data.columns)

#table
col = st.columns((1.5, 2, 2, 2, 2, 2), gap='medium')  
header = columns_list #header

for col, field in zip(col, header): 
	col.write("**" + field + "**")

for idx, row in data.iterrows():
    col = st.columns((1.5, 2, 2, 2, 2, 2), gap='medium')  
    col[0].write(str(idx))
    col[1].write(row['category'])
    col[2].write(row['age_months'])
    col[3].write(row['weight_kg'])
    col[4].write(row['height_cm'])
    
    placeholder = col[5].empty()
    show_more = placeholder.button("more", key=idx, type="primary")

    # if button pressed
    if show_more:
        # rename button
        placeholder.button("less", key=str(idx) + "_")
        
        # do stuff
        st.write("This is some more stuff with a checkbox")
        temp = st.selectbox("Select one", ["A", "B", "C"], key=f"selectbox_{idx}")
        st.write("You picked ", temp)
        st.write("---")