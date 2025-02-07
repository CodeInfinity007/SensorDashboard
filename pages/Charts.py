import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from sql_setup import MySQLConnection



# Define menu with option_menu
selected = option_menu(
    menu_title=None,
    options=["Charts", "Threshold Analysis", "KPI"],
    icons=["house", "graph-up", "columns"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
    
)


st.markdown("<h1 style='text-align: center;'>Charts</h1>", unsafe_allow_html=True)
st.markdown("---")

if st.session_state.df is not None:
    data = st.session_state.df


    if selected == "Charts":

            r1c1, r1c2 = st.columns(2, vertical_alignment="center")

            with r1c1:
                pass

            with r1c2:
                st.subheader("YOUR TITLE")
                st.write("Type your desired text here for more information on the type of template that's being made")

                # try:
                #     vals = data.columns.drop("abbrev")

                # finally:
                #     vals = data.columns

                vals = data.columns
                

                options = st.multiselect("Select Factors", vals, list(vals)[:4])
                
                

            r2c1, r2c2 = st.columns([0.4, 0.6],gap="large",  vertical_alignment="center")

            with r2c1:
                
                r2c2i, r2c2ii = st.columns(2, vertical_alignment="center")

                if "pie_vals" in st.session_state:
                    pie_vals = st.session_state.pie_vals
                if "pie_factor_columns" in st.session_state:
                    pie_factor_columns = st.session_state.pie_factor_columns

                with r2c2i:
                    st.subheader("Proportion of Alcohol-Related Incidents by State")
                    unique_abbrev = data[pie_factor_columns].unique()
                    options = st.multiselect("Select Factors", unique_abbrev, unique_abbrev[0:4])
                    

                with r2c2ii:
                    # selected_states = ['AL', 'CA', 'FL', 'NY', 'TX']
                    filtered_df = data[data[pie_factor_columns].isin(options)]

                    fig_alcohol = px.pie(filtered_df, values=pie_vals, names=pie_factor_columns, 
                            color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig_alcohol)

            with r2c2:
                

                if "line_x" in st.session_state and "line_y" in st.session_state:
                    line_x = st.session_state.line_x
                    line_y = st.session_state.line_y

                custom_header = f"""
                    <div style="text-align:center;">
                        <h2>{line_x if line_x != "abbrev" else "State"} VS {line_y.capitalize()}</h2>
                    </div>
                """
                st.markdown(custom_header, unsafe_allow_html=True)

                fig = px.line(data, x=line_x, y=line_y, markers=True, 
                    labels={'abbrev': 'State', "total": "Total Incidents"}, 
                    color_discrete_sequence=px.colors.qualitative.T10)
                fig.update_traces(mode='lines+markers')
                st.plotly_chart(fig)  


            

            
                # r3c1i, r3c1ii = st.columns(2,gap="large",  vertical_alignment="center")

                # with r3c1i:

    if selected == "Threshold Analysis":
        st.title("Threshold Anomaly Analysis")

        # Starting conn
        mysql_conn = MySQLConnection()
        mysql_conn.start_connection()

        mysql_conn.import_csv_to_mysql('sensor.csv', 'sensor')
        
    
        sensor_data = mysql_conn.fetch_data("SELECT * FROM sensor_data;")
        # sensor_data = pd.DataFrame(sensor_data)
        print(sensor_data)

        # if sensor_data is not None:
        st.subheader("MySQL Table Data")
        st.dataframe(sensor_data)

        def anomaly_detection(sens, lower_percentile=5, upper_percentile=95):
            results = {}
            print(sens)
            for col in sens:

                if pd.api.types.is_numeric_dtype(sens[col]):
                    lower_threshold = np.percentile(sens[col], lower_percentile)
                    upper_threshold = np.percentile(sens[col], upper_percentile)

                    anomalies_low = sens[col][sens[col] < lower_threshold]
                    anomalies_high = sens[col][sens[col] > upper_threshold]
                    print(anomalies_low)

                    results[col] = {
                        'lower_threshold': lower_threshold,
                        'upper_threshold': upper_threshold,
                        'anomalies_below_count': anomalies_low.count(),
                        'anomalies_above_count': anomalies_high.count(),
                        'anomalies_below': anomalies_low.tolist(),
                        'anomalies_above': anomalies_high.tolist()
                    }

            return results

        # Function to create anomaly DataFrame
        def create_anomaly_df(metrics):
            below_df = pd.DataFrame({
                'Type': 'Below Threshold',
                'Values': metrics['anomalies_below']
            })

            above_df = pd.DataFrame({
                'Type': 'Above Threshold',
                'Values': metrics['anomalies_above']
            })

            return pd.concat([below_df, above_df], ignore_index=True)
        

        anomaly_detection(sensor_data)
        anomaly_results = anomaly_detection(sensor_data)
        anomaly_results = {key: value for key, value in anomaly_results.items() if 'year' not in key and 'date' not in key}

        # print(anomaly_results)

        st.markdown("#")
        st.subheader('Sensor Data Anomaly Detection')

        # print(anomaly_results.items())

        # Iterate over each sensor and display anomaly metrics and details
        for col, metrics in anomaly_results.items():
            st.markdown(f"### Sensor: {col}")

            # Display thresholds and counts in metrics format
            col1, col2 = st.columns([0.4,0.6])
            with col1:
                
                st.metric('Upper Threshold: ', value=f"{metrics['upper_threshold']:.2f}", delta=f'Values Above = {metrics["anomalies_above_count"]}', delta_color='normal')
                st.metric('Lower Threshold: ', value=f"{metrics['lower_threshold']:.2f}", delta=f'Values Below = {metrics["anomalies_below_count"]}', delta_color='inverse')

            with col2:
                pass

                # Create a detailed table for anomalies
                anomaly_df = pd.DataFrame({
                    'Type': ['Below Threshold'] * len(metrics['anomalies_below']) + ['Above Threshold'] * len(metrics['anomalies_above']),
                    'Values': metrics['anomalies_below'] + metrics['anomalies_above']
                })
                with st.expander("See detailed anomalies"):
                    st.table(anomaly_df)

                # Convert 'random_date' to datetime format
                sensor_data['random_date'] = pd.to_datetime(sensor_data['random_date'])

                # Create Plotly figure
                fig = go.Figure()

                # Add scatter plot for sensor data
                fig.add_trace(go.Scatter(x=sensor_data['random_date'], y=sensor_data[col], mode='markers', name=col))

                # Add lower and upper thresholds as lines
                fig.add_trace(go.Scatter(x=[sensor_data['random_date'].min(), sensor_data['random_date'].max()], y=[metrics['lower_threshold'], metrics['lower_threshold']],
                                        mode='lines', name=f'Lower {col} Threshold', line=dict(color='blue', width=2, dash='dash')))
                fig.add_trace(go.Scatter(x=[sensor_data['random_date'].min(), sensor_data['random_date'].max()], y=[metrics['upper_threshold'], metrics['upper_threshold']],
                                        mode='lines', name=f'Upper {col} Threshold', line=dict(color='blue', width=2, dash='dash')))

                # Update layout for the figure
                fig.update_layout(title=f'{col} Data with Thresholds', xaxis_title='Date', yaxis_title=col)

                # Render the Plotly figure in Streamlit
                st.plotly_chart(fig)


            

        # Closing connection
        mysql_conn.close_connection()

    if selected == "KPI":
            
            data['random_date'] = pd.to_datetime(data['random_date'])

            st.sidebar.header('Select Time Interval')
            start_date = st.sidebar.date_input('Start date', value=pd.to_datetime('2017-01-01'))
            end_date = st.sidebar.date_input('End date', value=pd.to_datetime('2018-12-31'))
            x_axis_kpi = st.sidebar.selectbox("X Axis:", data.columns)

            data_columns = data.columns

            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            filtered_data = data[(data['random_date'] >= start_date) & (data['random_date'] <= end_date)]

            col1_kpi, col2_kpi = st.columns(2, gap="large")

            with col1_kpi:
                st.subheader("Filtered Data:")
                st.dataframe(filtered_data)

            with col2_kpi:

                def compute_metrics(data):
                    metrics = {}

                    for col in data.columns:
                        if pd.api.types.is_numeric_dtype(data[col]):
                            metrics[f'Average of {col}'] = round(data[col].mean(), 2)

                            if pd.api.types.is_integer_dtype(data[col]):
                                metrics[f'Sum of {col}'] = data[col].sum()
                        
                        elif pd.api.types.is_categorical_dtype(data[col]) or pd.api.types.is_object_dtype(data[col]):
                            metrics[f'Unique values in {col}'] = data[col].nunique()

                    return metrics


                metrics = compute_metrics(data)
                st.title('Key Performance Indicators')

                for label, value in metrics.items():
                    st.metric(label=label, value=value)


            columns = st.columns(3,gap="large",  vertical_alignment="center")
            columns2 = st.columns(3,gap="large",  vertical_alignment="center")

            for i, col in enumerate(columns, 1):
                with col:
                    fig = px.line(filtered_data, x=x_axis_kpi, y=data_columns[i])
                    st.plotly_chart(fig)

            for j, col in enumerate(columns2):
                with col:
                    fig = px.line(filtered_data, x=x_axis_kpi, y=data_columns[j])
                    st.plotly_chart(fig)

else:
    st.info("Upload a CSV file and switch back to see charts.")
