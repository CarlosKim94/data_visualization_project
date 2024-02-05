import streamlit as st
import plotly_express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

header = st.container()
dataset = st.container()

with header:
    st.title('Emergency Admission Surveillance Data')
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
    introduction = """
    The data from emergency department documentation is routinely gathered as part of the 
    AKTIN emergency admission register. The data include information on the presenting ED, 
    age groups, reason for admission classified according to the Canadian Emergency 
    Department Information System - Presenting Complaint List (CEDIS-PCL3.0), 
    diagnoses coded according to the International Classification of Diseases (ICD-10), 
    and information on inpatient admission following the ED visit.
    """
    st.text(introduction)

with dataset:
    df = pd.read_csv('download/Notaufnahmesurveillance_cleaned.csv')

    st.sidebar.header("Filter: ")

    # Filter for syndrome
    syndrome = st.sidebar.multiselect("Syndrome", df['syndrome'].unique())
    if not syndrome:
        df2 = df.copy()
    else:
        df2 = df[df['syndrome'].isin(syndrome)]

    # Filter for age group
    age_group = st.sidebar.multiselect("Age Group", df2['age_group'].unique())
    if not age_group:
        df3 = df2.copy()
    else:
        df3 = df2[df2['age_group'].isin(age_group)]

    # Filter the data based on syndrome and age group
    if not syndrome and not age_group:
        filtered_df = df
    elif not age_group:
        filtered_df = df[df["syndrome"].isin(syndrome)]
    elif not syndrome:
        filtered_df = df[df["age_group"].isin(age_group)]
    elif syndrome and age_group:
        filtered_df = df3[df["syndrome"].isin(syndrome) & df["age_group"].isin(age_group)]
    elif syndrome:
        filtered_df = df3[df3["syndrome"].isin(syndrome)]
    else:
        filtered_df = df3[df3["age_group"].isin(age_group)]

    # Define custom line colors for each syndrome
    line_colors = {'SARI': 'darksalmon', 'ARI': 'steelblue', 'ILI': 'seagreen'}

    # Create a line graph
    date_syndrome_df = filtered_df.groupby(by = ["date", "syndrome"], as_index = False)[["relative_cases"]].sum()
    fig = go.Figure()
    config = {'displayModeBar': False}

    # Add a line trace
    for syndrome in date_syndrome_df['syndrome'].unique():
        syndrome_data = date_syndrome_df[date_syndrome_df['syndrome'] == syndrome]
        fig.add_trace(go.Scatter(x=syndrome_data['date'], y=syndrome_data['relative_cases'],
                                mode='lines', name=syndrome, line=dict(color=line_colors[syndrome])))

    # Add annotation
    extra_annotation_text = "ARI: Acute Respiratory Illness <br> SARI: Severe Acute Respiratory Infection <br> ILI: Influenza-Like Illness"

    fig.add_annotation(
    text=extra_annotation_text,
    align='center',
    x=0.5,
    y=-0.2,
    xref='paper',
    yref='paper',
    showarrow=False,
    font=dict(size=12)
    )
    
    # Update layout
    fig.update_layout(title='Emergency Admissions for Respiratory Diseases',
                      yaxis_title='Average number of admissions per emergency department',
                      showlegend=True,
                      legend=dict(x=0.93, y=0.95, xanchor='left', yanchor='top'),
                      height=600)
    st.plotly_chart(fig, use_container_width=True, config=config)


    mid_text = """
    For better understanding and identification of disease peaks over time, the expected value of 
    admissions and an associated 80% prediction interval are calculated and can be visualized below.
    """
    st.text(mid_text)

    # Create a line graph with expected values
    date_syndrome_exp_df = filtered_df.groupby(by = ["date", "syndrome"], as_index = False)[["relative_cases", "expected_lowerbound","expected_upperbound"]].sum()
    fig = go.Figure()

    # Add a line trace
    for syndrome in date_syndrome_exp_df['syndrome'].unique():

        syndrome_data = date_syndrome_exp_df[date_syndrome_exp_df['syndrome'] == syndrome]
        fig.add_trace(go.Scatter(x=syndrome_data['date'], y=syndrome_data['relative_cases'],
                                mode='lines', name=syndrome, line=dict(color=line_colors[syndrome])))
        
        # Add shaded area between expected_lowerbound and expected_upperbound
        fig.add_trace(go.Scatter(x=syndrome_data['date'], y=syndrome_data['expected_lowerbound'],
                                fill='tonexty', mode='lines',
                                showlegend=False, line=dict(color=line_colors[syndrome], width=0)
                                ))
        
        fig.add_trace(go.Scatter(x=syndrome_data['date'], y=syndrome_data['expected_upperbound'],
                                fill='tonexty', mode='lines',
                                showlegend=False, line=dict(color=line_colors[syndrome], width=0)
                                ))
    
    # Add annotation
    extra_annotation_text = "ARI: Acute Respiratory Illness <br> SARI: Severe Acute Respiratory Infection <br> ILI: Influenza-Like Illness"

    fig.add_annotation(
    text=extra_annotation_text,
    align='center',
    x=0.5,
    y=-0.2,
    xref='paper',
    yref='paper',
    showarrow=False,
    font=dict(size=12)
    )

    # Update layout
    fig.update_layout(title='Emergency Admissions for Respiratory Diseases with Expected Values',
                      yaxis_title='Average number of admissions per emergency department',
                      showlegend=True,
                      legend=dict(x=0.93, y=0.95, xanchor='left', yanchor='top'),
                      height=600)
    st.plotly_chart(fig, use_container_width=True, config=config)


    # Pie charts

    age_syndrome_df = filtered_df.groupby(by = ["age_group", "syndrome"], as_index = False)["relative_cases"].sum()

    # Filter data for each syndrome
    sari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "SARI"]
    ari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ARI"]
    ili_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ILI"]

    # # Define the desired order for the age groups
    age_group_order = ['00+', '0-4', '5-9', '10-14', '15-19', '20-39', '40-59', '60-79', '80+']
    age_group_order_ILI = ['00+', '0-4', '5-9', '10-14', '15-19', '20-39', '40-59', '60-79']

    # # Sort the DataFrame by the desired order
    sari_data_sorted = sari_data.set_index('age_group').loc[age_group_order].reset_index()
    ari_data_sorted = ari_data.set_index('age_group').loc[age_group_order].reset_index()
    ili_data_sorted = ili_data.set_index('age_group').loc[age_group_order_ILI].reset_index()

    # Create subplots
    fig = make_subplots(rows=1, cols=3, subplot_titles=['SARI', 'ARI', 'ILI'], specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])

    # Add pie charts to subplots
    fig.add_trace(go.Pie(labels=sari_data_sorted['age_group'], values=sari_data_sorted['relative_cases'], name="", sort=False,
                         hovertemplate = "Age Group:                               %{label} <br>% of Total Relative Cases: %{percent}"), 1, 1)
    fig.add_trace(go.Pie(labels=ari_data_sorted['age_group'], values=ari_data_sorted['relative_cases'], name="",
                         hovertemplate = "Age Group:                               %{label} <br>% of Total Relative Cases: %{percent}"), 1, 2)
    fig.add_trace(go.Pie(labels=ili_data_sorted['age_group'], values=ili_data_sorted['relative_cases'], name="",
                         hovertemplate = "Age Group:                               %{label} <br>% of Total Relative Cases: %{percent}"), 1, 3)

    # Set subplot titles
    fig.update_xaxes(title_text='SARI', row=1, col=1)
    fig.update_xaxes(title_text='ARI', row=1, col=2)
    fig.update_xaxes(title_text='ILI', row=1, col=3)

    # Update layout
    fig.update_layout(title='Syndrome Types sorted from most to least severe by age')

    st.plotly_chart(fig, use_container_width=True, config=config)


    # Data source
    st.markdown("*Data Source:* https://github.com/robert-koch-institut/Daten_der_Notaufnahmesurveillance")