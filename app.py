import psycopg2
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
import altair as alt
import plost

load_dotenv()

st.set_page_config(
    page_title="StunTRON",
    page_icon="❤️🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Kutakbisa membuatmu jatuh cinta kepadaku meski kau tak cinta kepadaku beri sedikit waktu"}
)

# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #7da0fa;
    text-align: center;
    padding: 15px 0;
    border-radius: 5px;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            database=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD")
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

np.random.seed(42)  # Set seed for reproducibility
data = {
    'baby_id': range(1, 101),  # 100 babies
    'category': np.random.choice(['stunting', 'at risk of stunting', 'healthy'], size=100),
    'age_months': np.random.randint(0, 24, size=100),  # Age in months
    'weight_kg': np.random.uniform(2.5, 10.0, size=100),  # Weight in kg
    'height_cm': np.random.uniform(45, 90, size=100)  # Height in cm
}

# Calculate the percentage of healthy babies and stunting babies
total_babies = len(data['baby_id'])
healthy_count = np.sum(data['category'] == 'healthy')
stunting_count = np.sum(data['category'] == 'stunting')

percentage_healthy = (healthy_count / total_babies * 100) if total_babies > 0 else 0
percentage_stunting = (stunting_count / total_babies * 100) if total_babies > 0 else 0

# Main function app
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Login form
    if not st.session_state.logged_in:
        st.title("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = authenticate_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.name = user[0]
                st.session_state.email = user[1]
                st.session_state.number = user[2]
                st.session_state.location = user[3]
                st.session_state.role = user[4]
                st.success("Login successful!")
                st.rerun()  # Refresh to load the dashboard immediately
            else:
                st.error("Invalid email or password")

    # Display sidebar menu and pages if logged in
    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        menu_selection = st.sidebar.radio("Menu", ["Dashboard", "Data","Posyandu", "Article", "Account"])
        
        if menu_selection == "Dashboard":
            dashboard_page()
        elif menu_selection == "Data":
            data_page()
        elif menu_selection == "Posyandu":
            posyandu()
        elif menu_selection == "Article":
            article()
        elif menu_selection == "Account":
            account_page()
        

# Login function to authenticate user and fetch details
def authenticate_user(email, password):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fullname, email, number, location, role FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Exception as e:
            st.error(f"Error querying the database: {e}")
            return None
        finally:
            conn.close()
    return None

# Dashboard (Home page) 1
def dashboard_page():
    st.title("Simple Login Dashboard")

    st.sidebar.title("Options")
    st.sidebar.write("Select an option from the sidebar.")

    col = st.columns((4,5), gap='medium')

    with col[0]:
        colcol = st.columns((1.6,2), gap='medium')
        
        def make_donut(healthy_percentage, label_text, color_scheme):
            if color_scheme == 'blue':
                chart_color = ['#29b5e8', '#155F7A']
            elif color_scheme == 'green':
                chart_color = ['#27AE60', '#12783D']
            elif color_scheme == 'orange':
                chart_color = ['#F39C12', '#875A12']
            elif color_scheme == 'red':
                chart_color = ['#E74C3C', '#781F16']
            
            # Data for the donut chart
            source = pd.DataFrame({
                "Category": ['Unhealthy', label_text],
                "Percentage": [100 - healthy_percentage, healthy_percentage]
            })
            source_bg = pd.DataFrame({
                "Category": ['Unhealthy', label_text],
                "Percentage": [100, 0]
            })
            
            # Create the donut chart
            plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
                theta="Percentage",
                color=alt.Color("Category:N",
                                scale=alt.Scale(
                                    domain=[label_text, 'Unhealthy'],
                                    range=chart_color),
                                legend=None),
            ).properties(width=130, height=130)
            
            # Add text to the chart
            text = plot.mark_text(align='center', color=chart_color[0], font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(
                text=alt.value(f'{healthy_percentage} %')
            )
            
            # Background plot
            plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
                theta="Percentage",
                color=alt.Color("Category:N",
                                scale=alt.Scale(
                                    domain=[label_text, 'Unhealthy'],
                                    range=chart_color),
                                legend=None),
            ).properties(width=130, height=130)
            
            return plot_bg + plot + text

        with colcol[0]:
            st.subheader('Bayi sehat')
            st.altair_chart(make_donut(healthy_percentage=percentage_healthy, label_text='Healthy Babies', color_scheme='green'))
        with colcol[1]:
            st.subheader('Bayi stunting')
            st.altair_chart(make_donut(healthy_percentage=percentage_stunting, label_text='Healthy Babies', color_scheme='red'))

    with col[1]:
        # Create a 2x2 grid layout
        grid1, grid2 = st.columns((2), gap='medium')
        grid1.metric("**Total Balita**", 2)
        grid2.metric("**Balita Potensi Stunting**", 3)
        
        grid3, grid4 = st.columns((2), gap='medium')
        grid3.metric("**Balita Sehat**", 20)
        grid4.metric("**Balita Stunting**", 31)
        
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Create a plot
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label='Sine Wave')
    plt.title('Sample Graph')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    st.pyplot(plt)

# Data page 2
def data_page():
    st.header("Data Pasien")
    tab1, tab2 = st.tabs(["Semua Data", "Riwayat"])

    with tab1:
        st.header("Data Balita")
        st.caption("This is a string that explains something above. This is a string that explains something above. This is a string that explains something above. This is a string that explains something above. This is a string that explains something above. This is a string that explains something above.")
        np.random.seed(42)  

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
    with tab2:
        st.header("Content for Tab 2")
        st.write("This is the content of the second tab.")

# Settings page 3
def posyandu():
    st.title("Data posyandu")
    tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

    with tab1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    with tab2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
    with tab3:
        st.header("An owl")
        st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

# Article
def article():
    
    st.title('Research article')

    st.header('Writing an interactive research article using Streamlit')
    if st.button("Read More", key="read_more_1"):
        st.markdown('''
        This is additional information that provides more context and details about the topic discussed in the article. 
        It can include insights, data, or any other relevant information that enhances the reader's understanding.
        ''')
        if st.button("Back", key="back_1"):
            st.empty()
            
    st.header('Writing an interactive research article using Streamlit2')
    if st.button("Read More", key="read_more_2"):
        st.markdown('''
        This is additional information that provides more context and details about the topic d.
        ''')
        if st.button("Back", key="back_2"):
            st.empty()
    
    st.header('Writing an interactive research article using Streamlit3')
    if st.button("Read More", key="read_more_3"):
        st.markdown('''
        This is additional information and details about the topic discussed in the article. 
        It can include insights, data, or any other relevant information that enhances the reader's understanding.
        ''')
        if st.button("Back", key="back_3"):
            st.empty()
            
# Settings page 4
def account_page():
    st.title("Account Information")

    about = "Data Scientist with a passion for AI and ML."

    # Display user profile information
    if os.path.exists("avatar.png"):
        st.image("avatar.png", width=150, caption="Avatar")
    else:
        st.write("No avatar available.")

    st.write(f"**Nama:** {st.session_state.name}")
    st.write(f"**About:** {about}")
    st.write(f"**Email:** {st.session_state.email}")
    st.write(f"**Number:** {st.session_state.number}")
    st.write(f"**Role:** {st.session_state.role}")

    # Option to log out
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()  # Refresh to go back to the login page

# Run the app
if __name__ == "__main__":
    main()