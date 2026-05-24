import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- PAGE CONFIG & THEME ---
st.set_page_config(
    page_title="Spar Factory Dashboard",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for an industrial dark mode premium aesthetic
st.markdown("""
    <style>
    .main { background-color: #111625; color: #FFFFFF; }
    div[data-testid="stMetricValue"] { color: #4DB6AC !important; font-size: 28px; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #AEB7C2 !important; }
    .stButton>button { background-color: #4DB6AC; color: white; border-radius: 6px; width: 100%; }
    .stButton>button:hover { background-color: #3ca096; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Timestamp', 'Temperature'])
if 'running' not in st.session_state:
    st.session_state.running = False

# --- HEADER ---
st.title("🌡️ Spar Factory Analytics Dashboard")
st.markdown("Real-time temperature monitoring and predictive analytics engine.")
st.write("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛️ Control Panel")
    
    # Start / Stop Engine Button
    if st.session_state.running:
        if st.button("🛑 STOP ENGINE", key="toggle"):
            st.session_state.running = False
            st.rerun()
    else:
        if st.button("🚀 START ENGINE", key="toggle"):
            st.session_state.running = True
            st.rerun()
            
    st.markdown("---")
    st.header("🕒 Filter & Timeframe")
    timeframe = st.selectbox(
        "Select Duration:",
        options=["All Data", "Last 30 Minutes", "Last 1 Hour"]
    )
    
    st.markdown("---")
    st.header("📥 Export Reports")
    export_range = st.date_input("Select Date Range for Export:", [datetime.now().date(), datetime.now().date()])

# --- LIVE REFRESH LAYOUT SLOTS ---
metrics_slot = st.empty()
chart_slot = st.empty()
insights_slot = st.empty()
log_table_slot = st.empty()

# --- REAL-TIME ENGINE LOOP ---
if st.session_state.running:
    # 1. Generate real-time telemetry data point with full precision timestamp
    new_temp = round(np.random.uniform(20.0, 85.0), 2)
    new_row = pd.DataFrame({'Timestamp': [datetime.now()], 'Temperature': [new_temp]})
    st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True).tail(5000)

    # 2. Filter historical frames based on selection
    df = st.session_state.db.copy()
    if timeframe == "Last 30 Minutes":
        df = df[df['Timestamp'] >= (datetime.now() - timedelta(minutes=30))]
    elif timeframe == "Last 1 Hour":
        df = df[df['Timestamp'] >= (datetime.now() - timedelta(hours=1))]

    # 3. Update the dynamic UI slots instantly
    if not df.empty:
        with metrics_slot.container():
            val_min = round(df['Temperature'].min(), 2)
            val_max = round(df['Temperature'].max(), 2)
            val_avg = round(df['Temperature'].mean(), 2)
            col1, col2, col3 = st.columns(3)
            col1.metric(label="MINIMUM TEMPERATURE", value=f"{val_min} °C")
            col2.metric(label="MAXIMUM TEMPERATURE", value=f"{val_max} °C")
            col3.metric(label="AVERAGE TEMPERATURE", value=f"{val_avg} °C")
            st.write("---")

        with chart_slot.container():
            st.subheader("📈 Live Temperature Trend")
            # Create a localized display copy with strings for Native Streamlit plotting clarity
            plot_df = df.copy()
            plot_df['Seconds Timeline'] = plot_df['Timestamp'].dt.strftime('%H:%M:%S')
            st.line_chart(data=plot_df, x='Seconds Timeline', y='Temperature', color="#4DB6AC")
            st.write("---")

        with insights_slot.container():
            st.subheader("🔍 Peak Drill-Down Insights")
            peak_row = df.loc[df['Temperature'].idxmax()]
            col_ins, col_act = st.columns([3, 1])
            with col_ins:
                st.info(f"💡 **Highest Spike Detected:** A peak value of **{peak_row['Temperature']}°C** occurred exactly at **{peak_row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**.")
            with col_act:
                if st.button("Inspect Peak Event"):
                    st.toast(f"Drilling deep into timestamp: {peak_row['Timestamp'].strftime('%H:%M:%S')}", icon="🧐")
            st.write("---")

        with log_table_slot.container():
            st.subheader("📋 Live Running Log Records")
            display_df = df.copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(display_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

    time.sleep(10)
    st.rerun()

# --- STATIONARY/IDLE ENGINE STATE ---
else:
    df = st.session_state.db.copy()
    if timeframe == "Last 30 Minutes":
        df = df[df['Timestamp'] >= (datetime.now() - timedelta(minutes=30))]
    elif timeframe == "Last 1 Hour":
        df = df[df['Timestamp'] >= (datetime.now() - timedelta(hours=1))]

    if not df.empty:
        with metrics_slot.container():
            val_min = round(df['Temperature'].min(), 2)
            val_max = round(df['Temperature'].max(), 2)
            val_avg = round(df['Temperature'].mean(), 2)
            col1, col2, col3 = st.columns(3)
            col1.metric(label="MINIMUM TEMPERATURE", value=f"{val_min} °C")
            col2.metric(label="MAXIMUM TEMPERATURE", value=f"{val_max} °C")
            col3.metric(label="AVERAGE TEMPERATURE", value=f"{val_avg} °C")
            st.write("---")

        with chart_slot.container():
            st.subheader("📈 Historical Temperature Trend")
            plot_df = df.copy()
            plot_df['Seconds Timeline'] = plot_df['Timestamp'].dt.strftime('%H:%M:%S')
            st.line_chart(data=plot_df, x='Seconds Timeline', y='Temperature', color="#4DB6AC")
            st.write("---")

        with insights_slot.container():
            st.subheader("🔍 Peak Drill-Down Insights")
            peak_row = df.loc[df['Temperature'].idxmax()]
            col_ins, col_act = st.columns([3, 1])
            with col_ins:
                st.info(f"💡 **Highest Spike Detected:** A peak value of **{peak_row['Temperature']}°C** occurred exactly at **{peak_row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}**.")
            with col_act:
                if st.button("Inspect Peak Event"):
                    st.toast(f"Drilling deep into timestamp: {peak_row['Timestamp'].strftime('%H:%M:%S')}", icon="🧐")
            st.write("---")

        with log_table_slot.container():
            st.subheader("📋 Static Log Records")
            display_df = df.copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(display_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    else:
        st.warning(" Engine is idle. Click 'START ENGINE' in the sidebar to stream live factory floor metrics.")


# --- EXPORT REPORT GENERATION (Isolated Performance Fragment) ---
@st.fragment
def render_download_buttons():
    if st.session_state.db.empty:
        return

    st.markdown("### Download Links")
    export_df = st.session_state.db.copy()
    
    # 1. Excel Exporter
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        export_df.to_excel(writer, index=False, sheet_name='TemperatureData')
    
    st.download_button(
        label=" Download Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name=f"spar_factory_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_download_excel"
    )
    
    # 2. PDF Exporter with Crisp Seconds Graph Integration
    def generate_pdf():
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#111625'), spaceAfter=15)
        meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'), spaceAfter=15)
        section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], fontSize=14, leading=18, spaceBefore=10, spaceAfter=10)

        elements = [
            Paragraph("Spar Factory Analytics - Official Performance Report", title_style),
            Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style),
            Spacer(1, 10)
        ]
        
        # High Resolution Matplotlib Engine Configuration
        fig, ax = plt.subplots(figsize=(7.5, 3.5))
        ax.plot(export_df['Timestamp'], export_df['Temperature'], color='#4DB6AC', linewidth=1.5, marker='.', markersize=4)
        ax.set_title("High-Resolution Temperature Profile", fontsize=11, fontweight='bold', pad=10)
        ax.set_ylabel("Temperature (°C)", fontsize=9)
        ax.set_xlabel("Timeline (Seconds)", fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # Format the export document's X-Axis to read clearly with seconds
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
        fig.autofmt_xdate(rotation=25, ha='right')
        plt.yticks(fontsize=8)
        plt.xticks(fontsize=8)
        plt.tight_layout()
        
        fig_buffer = io.BytesIO()
        fig.savefig(fig_buffer, format='png', dpi=250)  # High resolution DPI adjustment
        fig_buffer.seek(0)
        plt.close(fig)
        
        elements.append(Paragraph(" Temperature Trend Chart", section_style))
        elements.append(Image(fig_buffer, width=7*inch, height=3.2*inch))
        elements.append(Spacer(1, 15))
        
        # Construct and attach data table logs
        elements.append(Paragraph(" Complete Dataset History", section_style))
        pdf_table_data = [["Timestamp (Seconds)", "Temperature (°C)"]]
        
        subset_df = export_df.tail(100).copy()
        subset_df['Timestamp'] = subset_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        pdf_table_data.extend(subset_df.values.tolist())
        
        t = Table(pdf_table_data, colWidths=[3.5*inch, 3.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#111625')),
            ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FBFD')])
        ]))
        elements.append(t)
        
        doc.build(elements)
        return pdf_buffer.getvalue()

    st.download_button(
        label="Download PDF Report",
        data=generate_pdf(),
        file_name=f"spar_factory_report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        key="btn_download_pdf"
    )

with st.sidebar:
    render_download_buttons()