import psycopg2
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
import os
import pandas as pd
import altair as alt
from groq import Groq

load_dotenv()

st.set_page_config(
    page_title="StunTRON",
    page_icon="❤️🧑‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Project Ai Hackaton"}
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

data = pd.read_excel("data/data_balita.xlsx")
data1 = pd.read_excel("data/data_balita.xlsx")

# Calculate the percentage of healthy babies and stunting babies
total_babies = len(data['Nama Balita'])
healthy_count = np.sum(data['Status Stunting'] == 'Sehat')
stunting_count = np.sum(data['Status Stunting'] == 'Stunting')

percentage_healthy = int(healthy_count / total_babies * 100) if total_babies > 0 else 0
percentage_stunting = int(stunting_count / total_babies * 100) if total_babies > 0 else 0

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
    # Hardcoded authentication for admin
    if email == "admin123@gmali.com" and password == "admin123":
        # Return a tuple similar to the DB result: (fullname, email, number, location, role)
        return ("Admin", "admin123@gmali.com", "08123456789", "Jakarta", "admin")
    return None

# Dashboard (Home page) 1
def dashboard_page():
    st.title("Dashboard")
    st.info(
        """
        Aplikasi ini masih beta dan beberapa fitur masih terbatas
        """,
        icon="👾",
    )

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
        grid1.metric("**Total Balita**", len(data))
        grid2.metric("**Balita Potensi Stunting**", len(data[data['Status Stunting'] == 'Potensi Stunting']))

        grid3, grid4 = st.columns((2), gap='medium')
        grid3.metric("**Balita Sehat**", len(data[data['Status Stunting'] == 'Sehat']))
        grid4.metric("**Balita Stunting**", len(data[data['Status Stunting'] == 'Stunting']))

    # Tambahan chart dan data
    st.markdown("---")
    st.subheader("Distribusi Usia Balita")

    # Bar chart status stunting per gender
    if 'Jenis Kelamin' in data.columns:
        gender_status = data.groupby(['Jenis Kelamin', 'Status Stunting']).size().unstack(fill_value=0)
        st.bar_chart(gender_status)
    else:
        st.info("Kolom 'Jenis Kelamin' tidak ditemukan di data.")

    st.subheader("5 Data Balita Terbaru")
    st.dataframe(data.tail(5))

# Data page 2
def data_page():
    st.header("Data Balita")
    col1, col2, col3, col4 = st.columns(4)
    with col3:
        lang_selection = st.selectbox("Pilih bahasa", [ "Indonesia", "Inggris"]) 
    with col4:
        model_selection = st.selectbox("Pilih model", [ "gemini", "openai", "claude", "llama"])

    tab1, tab2 = st.tabs(["Semua Data", "Riwayat"])

    with tab1:
        st.caption("Pilih satu balita atau beberapa untuk memberikan rekomendasi gizi")
        print(data1)
        riwayat = pd.DataFrame()

        if "df" not in st.session_state:
            st.session_state.df = data1

        event = st.dataframe(
            st.session_state.df,
            key="data",
            on_select="rerun",
            selection_mode=["multi-row"],
        )
        nama_balita = data1.iloc[event['selection']['rows']]['Nama Balita'].str.cat(sep=', ')
        umur_balita = data1.iloc[event['selection']['rows']]['Usia Balita (bulan)']
        status_balita =data1.iloc[event['selection']['rows']]['Status Stunting']
        if st.button(f"Rekomendasi gizi untuk {nama_balita}"):
            # data1.iloc[event['selection']['rows']][['Status Stunting']]
            client = Groq(
                api_key=os.environ.get("GROQ"),
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Berikan rekomendasi gizi untuk tiap-tiap {nama_balita}, sesuai dengan {umur_balita}, dan status stuntingnya {status_balita} dengan bahasa {lang_selection} yang singkat dan padat"
                    }
                ],  
                model="llama3-8b-8192"
            )

            chat_completion.choices[0].message.content

    with tab2:
        if riwayat.empty:
                st.info(
                    """
                    Anda belum melakukan aksi apapun sebelumnya.
                    """,
                    icon="📊",
                )
        columns_list = list(riwayat.columns)

        #table
        col = st.columns((1.5, 2, 2, 2, 2, 2,2,2,2,2,2), gap='medium')  
        header = columns_list

        for col, field in zip(col, header): 
            col.write("**" + field + "**")
    
        for idx, row in riwayat.iterrows():
            col = st.columns((1.5, 2, 2, 2, 2, 2,2,2,2,2,2), gap='medium')  
            col[0].write(row[0])
            col[1].write(row[1])
            col[2].write(row[2])
            col[3].write(row[3])
            col[4].write(row[4])
            col[5].write(row[5])
            col[6].write(row[6])
            col[7].write(row[7])
            col[8].write(row[8])
            col[9].write(row[9])
            
            placeholder = col[10].empty()
            if st.button("Hapus", key=row[0]):
                riwayat = riwayat.drop(idx)

# Settings page 3
def posyandu():
    st.title("Data Fasilitas")
    tab1, tab2 = st.tabs(["Posyandu", "Rumah sakit"])

    with tab1:
        data_posyandu = pd.read_excel("data/data_posyandu.xlsx")
        st.dataframe(data_posyandu)
    with tab2:
        st.markdown("Data rumah sakit masih belum tersedia")

# Article
def article():
    st.title('Edukasi')
    st.header('Cara Mengatasi Stunting pada Anak')
    st.markdown('''
        Baca lebih lanjut tentang cara mengatasi stunting pada anak
        ''')
    st.link_button("Read More", "https://genbest.id/articles/cara-mengatasi-stunting-pada-anak-orang-tua-wajib-tahu")
            
    st.header('Stunting dalam Sebuah Genggaman')
    st.markdown('''
        Baca lebih lanjut tentang stunting dalam sebuah genggaman
        ''')
    st.link_button("Read More", "https://www-who-int.translate.goog/news/item/19-11-2015-stunting-in-a-nutshell?_x_tr_sl=en&_x_tr_tl=id&_x_tr_hl=id&_x_tr_pto=tc")
    
    st.header('Kenali Stunting dan Pencegahannya')
    st.markdown('''
        Baca lebih lanjut tentang kenali stunting dan pencegahannya
        ''')
    st.link_button("Read More", "https://kampungkb.bkkbn.go.id/kampung/20664/intervensi/354753/kenali-stunting-dan-pencegahan-nya")
            
    st.header('Keberhasilan Pemerintah dalam Mengatasi Stunting')
    st.markdown('''
        Baca lebih lanjut tentang keberhasilan pemerintah dalam mengatasi stunting
        ''')
    st.link_button("Read More", "https://www.setneg.go.id/baca/index/buka_rakornas_stunting_wapres_ungkap_keberhasilan_pemerintah_turunkan_prevalensi_lima_tahun_terakhir")
    
    st.header('Permasalahan Stunting di Indonesia dan Penyelesaiannya')
    st.markdown('''
        Baca lebih lanjut tentang permasalahan stunting di Indonesia dan penyelesaiannya
        ''')
    st.link_button("Read More", "https://www.djkn.kemenkeu.go.id/kpknl-pontianak/baca-artikel/16261/permasalahan-stunting-di-indonesia-dan-penyelesaiannya.html")
            
    st.header('Pahami Stunting pada Anak Sejak Dini')
    st.markdown('''
        Baca lebih lanjut tentang pahami stunting pada anak sejak dini
        ''')
    st.link_button("Read More", "https://www.generasimaju.co.id/artikel/0-3-bulan/kesehatan/pahami-stunting-pada-anak-sejak-dini?utm_source=google&utm_medium=cpc&utm_campaign=sgm-sem_generic_iffodsa-aon_cosideration_traffic_Nov-2024&utm_term=dsa&utm_content=iffo&&&&&gad_source=1&gclid=Cj0KCQjwm5e5BhCWARIsANwm06iXoa3zdL2acx-b5lM7JDIAsWg1CPhG43iL_28reSgNMTVAIxB0G8caAmy9EALw_wcB&gclsrc=aw.ds")
    
    st.header('4 Cara Mencegah Stunting')
    st.markdown('''
        Baca lebih lanjut tentang 4 cara mencegah stunting
        ''')
    st.link_button("Read More", "https://upk.kemkes.go.id/new/4-cara-mencegah-stunting")
            
    st.header('Cara Mencegah Stunting dari Berbagai Pihak')
    st.markdown('''
        Baca lebih lanjut tentang cara mencegah stunting dari berbagai pihak
        ''')
    st.link_button("Read More", "https://ayosehat.kemkes.go.id/cara-mencegah-stunting-dari-berbagai-pihak")
            
    st.header('Apa itu Stunting?')
    st.markdown('''
        Baca lebih lanjut tentang apa itu stunting
        ''')
    st.link_button("Read More", "https://www.alodokter.com/stunting")
            
    st.header('Pengertian Stunting dan Pencegahannya')
    st.markdown('''
        Baca lebih lanjut tentang pengertian stunting dan pencegahannya
        ''')
    st.link_button("Read More", "https://www.siloamhospitals.com/informasi-siloam/artikel/apa-itu-stunting")

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