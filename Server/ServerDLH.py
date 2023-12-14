"""Server file for interfacing and receiving data from the client reading internal
Pi components.
TPRG 2131 Project 2 Dustin Horne 100844416"""
import signal
import sys
import socket
import os
import json
import PySimpleGUI as sg

def grace_exit(sig, frame):
    """exits when closing the gui"""
    print("Closing the server.")
    s.close()
    sys.exit(0)

signal.signal(signal.SIGINT, grace_exit)

s = socket.socket()
host = '10.102.13.149'  # Put Ip address here 10.102.13.149 pi 10.160.5.147 laptop
port = 5001
s.bind((host, port))
s.listen(5)

def get_temperature(data):
    """Get the temperature from the received data."""
    try:
        temperature = data.get('Temperature', 'N/A')
        return temperature
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return "N/A"

def get_cpu_speed(data):
    """Get the CPU speed from the received data."""
    try:
        cpu_speed = data.get('CPU_Speed', 'N/A')
        return cpu_speed
    except Exception as e:
        print(f"Error getting CPU speed: {e}")
        return "N/A"

def get_gpu_speed(data):
    """Get the GPU speed from the received data."""
    try:
        gpu_speed = data.get('GPU_Speed', 'N/A')
        return gpu_speed
    except Exception as e:
        print(f"Error getting GPU speed: {e}")
        return "N/A"

def get_memory_info(data):
    """Get memory information from the received data."""
    try:
        used_memory = data.get('Used_Memory', 'N/A')
        total_memory = data.get('Total_Memory', 'N/A')
        return {'used_memory': used_memory, 'total_memory': total_memory}
    except Exception as e:
        print(f"Error getting memory information: {e}")
        return {'used_memory': 'N/A', 'total_memory': 'N/A'}


def create_layout():
    """Makes a GUI to show status LED and seven values."""
    layout = [
        [sg.Text('Connection Status:'), sg.Text('', size=(15, 1), key='connection_status')],
        [sg.Text('LED Status:'), sg.Text('◯', size=(2, 1), key='led_status')],
        [sg.Text('', size=(30, 1), key='temperature')],
        [sg.Text('', size=(30, 1), key='cpu_speed')],
        [sg.Text('', size=(30, 1), key='gpu_speed')],
        [sg.Text('', size=(30, 1), key='used_memory')],
        [sg.Text('', size=(30, 1), key='total_memory')],
        [sg.Text('', size=(30, 1), key='iteration_count')],
        [sg.Button('Exit', key='EXIT')]
    ]
    return layout

def toggle_led_status(window):
    """Toggles status LED between ◯ and \u2B24"""
    current_symbol = window['led_status'].get()
    new_symbol = '\u2B24' if current_symbol == '◯' else '◯'
    window['led_status'].update(new_symbol)

def update_gui(window, data, iteration):
    """Updates the GUI with the received data."""
    window['connection_status'].update('Connected', text_color='green')
    
    # Toggle LED symbol based on the iteration
    led_symbol = '◯' if iteration % 2 == 0 else '\u2B24'
    window['led_status'].update(led_symbol)

    # Display the seven values on the GUI
    window['temperature'].update(f"Temperature: {data['Temperature']}")
    window['cpu_speed'].update(f"CPU Speed: {data['CPU_Speed']}")
    window['gpu_speed'].update(f"GPU Speed: {data['GPU_Speed']}")
    window['used_memory'].update(f"Used Memory: {data['Used_Memory']}")
    window['total_memory'].update(f"Total Memory: {data['Total_Memory']}")
    window['iteration_count'].update(f"Iteration Count: {data['Iteration_Count']}")
    
    window.refresh()


layout = create_layout()
window = sg.Window('System Monitor', layout, finalize=True)

try:
    iteration = 0
    while True:
        event, values = window.read(timeout=100)  # Added a timeout to allow for event checking

        if event == sg.WIN_CLOSED:
            break  # Exit the loop if the window is closed

        if event == 'Exit':
            break  # Exit the loop if the "Exit" button is pressed

        c, addr = s.accept()
        print('Got connection from', addr)

        # Receive data until the client indicates that it has finished sending
        while True:
            data_received = c.recv(1024)
            if not data_received:
                break  # No more data from the client

            try:
                # Assuming data_received is a JSON-encoded string
                data = json.loads(data_received.decode('utf-8'))

                temperature = get_temperature(data)
                cpu_speed = get_cpu_speed(data)
                gpu_speed = get_gpu_speed(data)
                memory_info = get_memory_info(data)

                data = {
                    "Temperature": temperature,
                    "CPU_Speed": cpu_speed,
                    "GPU_Speed": gpu_speed,
                    "Used_Memory": memory_info['used_memory'],
                    "Total_Memory": memory_info['total_memory'],
                    "Iteration_Count": iteration
                }

                update_gui(window, data, iteration)
                iteration += 1

            except json.JSONDecodeError as json_err:
                print(f"Error decoding JSON: {json_err}")
            except Exception as e:
                print(f"Error processing received data: {e}")

except Exception as e:
    print(f"Error: {e}")
finally:
    window.close()
