import streamlit as st
import plotly.graph_objects as go
import numpy as np
from avs_calculation import calculate_avs_metrics  # Ensure this module is accessible

# Sidebar menu for navigation
st.sidebar.title("Underwater AVS Simulator")
menu_options = ["Simulator Control", "AVS-1 Signal", "AVS-2 Signal", "DOA & Target Analysis", "Estimated Position Plot"]
selection = st.sidebar.radio("Select a feature", menu_options)

def plot_signals_in_columns(time, signal_data, sampling_frequency, signal_name):
    # Create columns for time and frequency domain plots
    col1, col2 = st.columns(2)

    # Time Domain Plot in the first column
    with col1:
        st.subheader(f"{signal_name} - Time Domain")
        fig = go.Figure(data=[go.Scatter(x=time, y=signal_data, mode='lines', name=signal_name)])
        fig.update_layout(title=f"{signal_name} in Time Domain", xaxis_title="Time (s)", yaxis_title="Amplitude")
        st.plotly_chart(fig)

    # Frequency Domain Plot in the second column
    with col2:
        st.subheader(f"{signal_name} - Frequency Domain")
        amplitude_spectrum = np.abs(np.fft.fft(signal_data))
        frequency = np.fft.fftfreq(len(signal_data), d=1/sampling_frequency)
        fig = go.Figure(data=[go.Scatter(x=frequency[:len(frequency)//2], y=amplitude_spectrum[:len(amplitude_spectrum)//2], mode='lines', name=f"{signal_name} Frequency Spectrum")])
        fig.update_layout(title=f"Frequency Plot of {signal_name}", xaxis_title="Frequency (Hz)", yaxis_title="Amplitude")
        st.plotly_chart(fig)

# Initialize session state for results if not already present
if 'results' not in st.session_state:
    st.session_state['results'] = None

# Layout based on menu selection
if selection == "Simulator Control":
    st.title("Simulator Control")
    
    # Two columns for input fields
    col1, col2 = st.columns(2)

    # Input fields divided into two columns
    with col1:
        target_strength = st.number_input("Target Strength (dBRef1V/micro Pa)", value=150)
        noise_frequency = st.number_input("Frequency of Noise Source (Hz)", value=1500)
        signal_duration = st.number_input("Duration of Signal (Seconds)", value=1)
        seastate = st.number_input("Seastate (0, 1, 3, 6)", value=0)
        sampling_frequency = st.number_input("Sampling Frequency (Hz)", value=1000)

    with col2:
        avs1_x = st.number_input("AVS-1 X (m)", value=0)
        avs1_y = st.number_input("AVS-1 Y (m)", value=20)
        avs2_x = st.number_input("AVS-2 X (m)", value=0)
        avs2_y = st.number_input("AVS-2 Y (m)", value=40)
        target_x = st.number_input("Target X (m)", value=800)
        target_y = st.number_input("Target Y (m)", value=0)

    # Button to perform calculations
    if st.button("Calculate"):
        # Call the calculation function and store the results in session state
        st.session_state['results'] = calculate_avs_metrics(
            TS=target_strength,
            fs=sampling_frequency,
            seastate=seastate,
            duration=signal_duration,
            f=noise_frequency,
            SX1=avs1_x,
            SY1=avs1_y,
            SX2=avs2_x,
            SY2=avs2_y,
            TPX1=target_x,
            TPY1=target_y
        )

        if st.session_state['results'] is None:
            st.error("Calculation failed to generate results.")
        else:
            st.success("Calculation successful!")

    # Plot AVS and Target Positions
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[avs1_x], y=[avs1_y], mode='markers+text', name='AVS-1', text=['AVS-1'], marker=dict(symbol='star', color='blue')))
    fig.add_trace(go.Scatter(x=[avs2_x], y=[avs2_y], mode='markers+text', name='AVS-2', text=['AVS-2'], marker=dict(symbol='star', color='green')))
    fig.add_trace(go.Scatter(x=[target_x], y=[target_y], mode='markers+text', name='Target Position', text=['Target Position'], marker=dict(symbol='diamond', color='red')))
    fig.update_layout(title="AVS and Target Position", xaxis_title="X (m)", yaxis_title="Y (m)", xaxis=dict(range=[-2000, 2000]), yaxis=dict(range=[-2000, 2000]))
    st.plotly_chart(fig, use_container_width=True)

# Helper function to plot signals in two columns


# AVS-1 Signal Tab
elif selection == "AVS-1 Signal":
    st.title("AVS-1 Signal")

    if st.session_state['results'] is not None:
        results = st.session_state['results']
        time = results["t"]
        sampling_frequency = results["samplingRate"]

        # Define signals to plot for AVS-1
        signals = [
            ("Transmitted Signal", results["Tx"]),
            ("Hydrophone Signal", results["p1"]),
            ("Particle Velocity X Component", results["vx1"]),
            ("Particle Velocity Y Component", results["vy1"]),
        ]

        # Plot each signal in two columns: time domain and frequency domain
        for signal_name, signal_data in signals:
            plot_signals_in_columns(time, signal_data, sampling_frequency, signal_name)
    else:
        st.error("Please run calculations in 'Simulator Control' first to populate the results.")

# AVS-2 Signal Tab
elif selection == "AVS-2 Signal":
    st.title("AVS-2 Signal")

    if st.session_state['results'] is not None:
        results = st.session_state['results']
        time = results["t"]
        sampling_frequency = results["samplingRate"]

        # Define signals to plot for AVS-2
        signals = [
            ("Hydrophone Signal", results["p2"]),
            ("Particle Velocity X Component", results["vx2"]),
            ("Particle Velocity Y Component", results["vy2"]),
        ]

        # Plot each signal in two columns: time domain and frequency domain
        for signal_name, signal_data in signals:
            plot_signals_in_columns(time, signal_data, sampling_frequency, signal_name)
    else:
        st.error("Please run calculations in 'Simulator Control' first to populate the results.")

# DOA & Target Analysis (Static Example)
elif selection == "DOA & Target Analysis":
    st.title("DOA & Target Analysis")

    if st.session_state['results'] is not None:
        results = st.session_state['results']

        # Display values in two columns for AVS-1 and AVS-2
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("AVS-1")
            st.write(f"**Range (m):** {results['rangeArr'][0]:.2f}")
            st.write(f"**RNL (dB):** {results['RNL1']:.2f}")
            st.write(f"**SNR (dB):** {results['SNR1']:.2f}")
            st.write(f"**Actual DoA (deg):** {results['actualDoaArr'][0]:.2f}")
            st.write(f"**Estimated DoA (deg):** {results['estimatedDoa1']:.2f}")
            st.write(f"**DoA Error (deg):** {results['doaError1']:.5f}")

        with col2:
            st.subheader("AVS-2")
            st.write(f"**Range (m):** {results['rangeArr'][1]:.2f}")
            st.write(f"**RNL (dB):** {results['RNL2']:.2f}")  # Assuming RNL2 is similar; replace if separate
            st.write(f"**SNR (dB):** {results['SNR2']:.2f}")  # Assuming SNR2 is similar; replace if separate
            st.write(f"**Actual DoA (deg):** {results['actualDoaArr'][1]:.2f}")
            st.write(f"**Estimated DoA (deg):** {results['estimatedDoa2']:.2f}")
            st.write(f"**DoA Error (deg):** {results['doaError2']:.5f}")

        # Estimated Target Position and Range Error
        st.subheader("Estimated Target Position")
        st.write(f"**Estimated Target X (m):** {results['estimatedTargetX']:.2f}")
        st.write(f"**Estimated Target Y (m):** {results['estimatedTargetY']:.2f}")
        st.write(f"**Range Error (m):** {results['rangeError']:.5f}")
    else:
        st.error("Please run calculations in 'Simulator Control' first to populate the results.")

# Estimated Position Plot (Static Example)
elif selection == "Estimated Position Plot":
    st.title("Estimated Position Plot")

    if st.session_state['results'] is not None:
        results = st.session_state['results']

        # Display Target Actual Coordinates, Estimated Coordinates, and Range Error
        st.write("### Target Coordinates")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Target Actual Coordinates**")
            st.write(f"X (m): {results['targetX']}")
            st.write(f"Y (m): {results['targetY']}")
        
        with col2:
            st.write("**Target Estimated Coordinates**")
            st.write(f"X (m): {results['estimatedTargetX']:.2f}")
            st.write(f"Y (m): {results['estimatedTargetY']:.2f}")

        st.write("### Range Error")
        st.write(f"Range Error (m): {results['rangeError']:.2f}")

        # Plot AVS and Target Positions
        fig = go.Figure()

        # Plot AVS-1 and AVS-2
        fig.add_trace(go.Scatter(x=[results['avs1X']], y=[results['avs1Y']], mode='markers+text', 
                                 name='AVS-1', text=['AVS-1'], marker=dict(symbol='star', color='blue')))
        fig.add_trace(go.Scatter(x=[results['avs2X']], y=[results['avs2Y']], mode='markers+text', 
                                 name='AVS-2', text=['AVS-2'], marker=dict(symbol='star', color='green')))
        
        # Plot Actual Target Position
        fig.add_trace(go.Scatter(x=[results['targetX']], y=[results['targetY']], mode='markers+text', 
                                 name='Actual Target Position', text=['Actual Position'], marker=dict(symbol='circle', color='red')))

        # Plot Estimated Target Position
        fig.add_trace(go.Scatter(x=[results['estimatedTargetX']], y=[results['estimatedTargetY']], mode='markers+text', 
                                 name='Estimated Target Position', text=['Estimated Position'], marker=dict(symbol='diamond', color='purple')))
        
        # Update layout
        fig.update_layout(
            title="Estimated and Actual Target Position",
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            xaxis=dict(range=[-2000, 2000]),
            yaxis=dict(range=[-2000, 2000]),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Please run calculations in 'Simulator Control' first to populate the results.")

else:
    st.write("Please run calculations in 'Simulator Control' first to display results in this tab.")