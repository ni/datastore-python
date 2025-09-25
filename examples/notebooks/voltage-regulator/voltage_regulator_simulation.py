import numpy as np
import plotly.graph_objects as go

def simulate_voltage_regulator(input_voltage, time_ms, target_voltage=5.0):
    """
    Simulates the output voltage of a voltage regulator over time.
    """
    output = np.zeros_like(time_ms, dtype=float)
    startup_delay = 50  # ms
    ramp_duration = 200  # ms
    overshoot = 0.2 if input_voltage >= target_voltage else 0.0
    max_output = min(input_voltage, target_voltage + overshoot)

    for i, t in enumerate(time_ms):
        if t < startup_delay:
            output[i] = 0
        elif t < startup_delay + ramp_duration:
            ramp_progress = (t - startup_delay) / ramp_duration
            output[i] = ramp_progress * max_output
        else:
            # Simulate regulation behavior
            if input_voltage < target_voltage:
                output[i] = input_voltage
            elif input_voltage <= 8:
                output[i] = target_voltage + overshoot * np.exp(-(t - startup_delay - ramp_duration)/300)
            elif input_voltage <= 10:
                output[i] = target_voltage + 0.5 + 0.2 * np.sin(0.01 * t)
            else:
                output[i] = target_voltage + 1.0 + 0.5 * np.sin(0.01 * t)
    return output

def main():
    # Time in milliseconds
    time_ms = np.linspace(0, 1000, 500)

    # Input voltages to simulate
    input_voltages = [4.5, 7, 9, 12]
    colors = ['blue', 'green', 'orange', 'red']

    # Create Plotly figure
    fig = go.Figure()

    # Add target voltage dashed line
    fig.add_trace(go.Scatter(
        x=time_ms,
        y=[5.0]*len(time_ms),
        mode='lines',
        name='Target Voltage (5V)',
        line=dict(color='black', dash='dash')
    ))

    # Simulate and plot each input voltage
    for vin, color in zip(input_voltages, colors):
        vout = simulate_voltage_regulator(vin, time_ms)
        fig.add_trace(go.Scatter(
            x=time_ms,
            y=vout,
            mode='lines',
            name=f'Input {vin}V',
            line=dict(color=color)
        ))

    # Update layout
    fig.update_layout(
        title='Voltage Regulator Output Simulation',
        xaxis_title='Time (ms)',
        yaxis_title='Output Voltage (V)',
        legend_title='Input Voltage',
        template='plotly_white'
    )

    fig.show()

if __name__ == "__main__":
    main()
