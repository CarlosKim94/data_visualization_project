import streamlit as st
import plotly_express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(layout="wide")

header = st.container()
dataset = st.container()

with header:
    st.title('Emergency Admission for Respiratory Related Diseases')
    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

    introduction = """
    The data on emergency admissions for respiratory diseases is collected daily as part of the AKTIN registration and published by the Robert Koch Institute (RKI). The dataset includes the date of the admission report, the amount of emergency departments that reported on that day, the average of the admissions per emergency department, the patient's age group and the diagnoses coded according to the [International Classification of Diseases (ICD-10)](https://www.dimdi.de/static/de/klassifikationen/icd/icd-10-gm/kode-suche/htmlgm2019/).
    """
    st.markdown(introduction, unsafe_allow_html=True)

with dataset:
    df = pd.read_csv('download/Notaufnahmesurveillance_cleaned.csv')

    # Desired order for the age groups
    age_group_order = ['0-4', '5-9', '10-14', '15-19', '20-39', '40-59', '60-79', '80+','00+']

    # Ensure the age group filter options are sorted according to the predefined order
    age_group_options = [age for age in age_group_order if age in df['age_group'].unique()]

    st.sidebar.header("Filter: ")

    # Filter for syndrome
    syndrome = st.sidebar.multiselect("Syndrome", df['syndrome'].unique())
    if not syndrome:
        df2 = df.copy()
    else:
        df2 = df[df['syndrome'].isin(syndrome)]

    # Filter for age group
    age_group = st.sidebar.multiselect("Age Group", options=age_group_options)
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

    # Predefined syndrome order
    syndrome_order = ['SARI', 'ARI', 'ILI']

    # Define custom line colors for each syndrome
    line_colors = {'SARI': 'darksalmon', 'ARI': 'steelblue', 'ILI': 'seagreen'}

    # Define the description for each syndrome
    syndrome_descriptions = {
    'SARI': 'SARI: Severe Acute Respiratory Infection',
    'ARI': 'ARI: Acute Respiratory Illness',
    'ILI': 'ILI: Influenza-Like Illness'
    }

    # Create a line graph
    date_syndrome_df = filtered_df.groupby(by = ["date", "syndrome"], as_index = False)[["relative_cases"]].sum()
    fig = go.Figure()
    config = {'displayModeBar': False}

    # Add a line trace with descriptions in the legend
    for syndrome_key in syndrome_order:
        if syndrome_key in date_syndrome_df['syndrome'].unique():
            syndrome_data = date_syndrome_df[date_syndrome_df['syndrome'] == syndrome_key]
            fig.add_trace(go.Scatter(
                x=syndrome_data['date'], 
                y=syndrome_data['relative_cases'],
                mode='lines', 
                name=syndrome_descriptions[syndrome_key], # Use the description as the legend name
                line=dict(color=line_colors[syndrome_key])
            ))
    
    # Update layout
    fig.update_layout(title='Emergency Admissions over time',
                      yaxis_title='Admissions per Emergency Deparment',
                      showlegend=True,
                      legend=dict(x=0.5, y=-0.2, xanchor='center', yanchor='top', orientation='h'),
                      height=600
                      )
    st.plotly_chart(fig, use_container_width=True, config=config)

    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

    mid_text = """
    For better understanding and identification of peaks over time, the expected value of admissions and an associated 80% prediction interval can be visualized below.
    """
    st.markdown(mid_text)

    # Create a line graph with expected values
    date_syndrome_exp_df = filtered_df.groupby(by = ["date", "syndrome"], as_index = False)[["relative_cases", "expected_lowerbound","expected_upperbound"]].sum()
    fig = go.Figure()

    # Add a line trace
    for syndrome_key in syndrome_order:
        if syndrome_key in date_syndrome_exp_df['syndrome'].unique():
            syndrome_data = date_syndrome_exp_df[date_syndrome_exp_df['syndrome'] == syndrome_key]
            fig.add_trace(go.Scatter(
                x=syndrome_data['date'], 
                y=syndrome_data['relative_cases'],
                mode='lines', 
                name=syndrome_descriptions[syndrome_key],
                line=dict(color=line_colors[syndrome_key])
            ))

            # Add shaded area between expected_lowerbound and expected_upperbound
            fig.add_trace(go.Scatter(
                x=syndrome_data['date'], 
                y=syndrome_data['expected_lowerbound'],
                fill='tonexty',
                mode='lines',
                showlegend=False,
                line=dict(color=line_colors[syndrome_key], width=0)
            ))
            
            fig.add_trace(go.Scatter(
                x=syndrome_data['date'], 
                y=syndrome_data['expected_upperbound'],
                fill='tonexty',
                mode='lines',
                showlegend=False,
                line=dict(color=line_colors[syndrome_key], width=0)
            ))

    # Update layout
    fig.update_layout(title='Emergency Admissions over time with Expected Values',
                      yaxis_title='Admissions per Emergency Deparment',
                      showlegend=True,
                      legend=dict(x=0.5, y=-0.2, xanchor='center', yanchor='top', orientation='h'),
                      height=600
                    )
    st.plotly_chart(fig, use_container_width=True, config=config)


    # Pie charts

    age_syndrome_df = filtered_df.groupby(by = ["age_group", "syndrome"], as_index = False)["relative_cases"].sum()

    age_syndrome_df['age_group'] = pd.Categorical(age_syndrome_df['age_group'], categories=age_group_order, ordered=True)
    age_syndrome_df = age_syndrome_df.sort_values('age_group')

    # Filter data for each syndrome
    sari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "SARI"]
    ari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ARI"]
    ili_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ILI"]

    # Filter data for each syndrome (assuming 'SARI', 'ARI', 'ILI' are all the syndromes you have)
    sari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "SARI"]
    ari_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ARI"]
    ili_data = age_syndrome_df[age_syndrome_df["syndrome"] == "ILI"]

    # Create subplots for each syndrome's pie chart
    fig = make_subplots(rows=1, cols=3, subplot_titles=['SARI', 'ARI', 'ILI'], specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]])

    # Add pie charts to subplots without sorting as data is already sorted
    fig.add_trace(go.Pie(labels=sari_data['age_group'], values=sari_data['relative_cases'], name="SARI",
                        sort=False, hovertemplate = "Age Group: %{label} <br>% Total Admissions: %{percent}"), 1, 1)
    fig.add_trace(go.Pie(labels=ari_data['age_group'], values=ari_data['relative_cases'], name="ARI",
                        sort=False, hovertemplate = "Age Group: %{label} <br>% Total Admissions: %{percent}"), 1, 2)
    fig.add_trace(go.Pie(labels=ili_data['age_group'], values=ili_data['relative_cases'], name="ILI",
                        sort=False, hovertemplate = "Age Group: %{label} <br>% Total Admissions: %{percent}"), 1, 3)
    
    # Set subplot titles
    fig.update_xaxes(title_text='SARI: Severe Acute Respiratory Infection', row=1, col=1)
    fig.update_xaxes(title_text='ARI: Acute Respiratory Illness', row=1, col=2)
    fig.update_xaxes(title_text='ILI: Influenza-Like Illness', row=1, col=3)

    # Update layout
    fig.update_layout(title='Syndrome Types by Age Group')

    st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

    mid_text_pie = """
    To show which age groups are most affected by different types of respiratory problems, we have created the pie charts below. These charts are arranged from the most to the least serious conditions.
    """
    st.markdown(mid_text_pie)

    st.plotly_chart(fig, use_container_width=True, config=config)


    # Data source
    st.markdown("*Data Source:* https://github.com/robert-koch-institut/Daten_der_Notaufnahmesurveillance")