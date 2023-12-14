"""Client file for interfacing and sending data to a server reading internal
Pi components.
TPRG 2131 Project 2 Dustin Horne 100844416"""
import socket
import time
import PySimpleGUI as sg
import platform
import os
import json

def check_platform():
    """Checks to ensure program is only run on Pi"""
    if platform.system() != "Linux" or platform.machine() != "armv7l":
        print("This script is designed to run on a Raspberry Pi only.")
        print("Exiting .")
        sg.popup_error("This script is designed to run on a Raspberry Pi only.\nExiting.")
        exit(0)

def get_temperature():
    """Grabs the core temp from the Pi"""
    temperature_str = os.popen("vcgencmd measure_temp").readline().strip()
    # Extract numeric part and convert to float
    temperature = float(temperature_str.split("=")[1].split("'")[0])
    return temperature

def get_cpu_speed():
    """Grabs the CPU speed from the Pi"""
    return os.popen("vcgencmd measure_clock arm").readline()

def get_gpu_speed():
    """Grabs the GPU speed from the Pi"""
    return os.popen("vcgencmd measure_clock core").readline()

def get_memory_info():
    """Grabs the RAM info from the Pi"""
    mem_info = os.popen("free").readlines()
    used_memory = mem_info[1].split()[2]
    total_memory = mem_info[1].split()[1]
    return {'used_memory': used_memory, 'total_memory': total_memory}

def collate_data(iteration_count):
    """Grabs the data"""
    temperature = get_temperature()
    cpu_speed = float(get_cpu_speed().strip("frequency(48)="))
    gpu_speed = float(get_gpu_speed().strip("frequency(1000)="))
    memory_info = get_memory_info()

    # Create a dictionary with the gathered data
    data = {
        "Temperature": round(temperature, 1),
        "CPU_Speed": round(cpu_speed, 1),
        "GPU_Speed": round(gpu_speed, 1),
        "Used_Memory": memory_info['used_memory'],
        "Total_Memory": memory_info['total_memory'],
        "Iteration_Count": iteration_count,
    }

    return data

def send_data_to_server(sock, data):
    """Sends the data"""
    try:
        # Convert dictionary to JSON string
        json_data = json.dumps(data)
        # Encode the JSON string to bytes
        message = json_data.encode('utf-8')
        # Send the data to the server
        sock.sendall(message)
    except Exception as e:
        print(f"Error sending data to server: {e}")


def create_layout():
    """makes a GUI with a solid circle as an indicator"""
    layout = [
        [sg.Text('Connection Status:'), sg.Text('', size=(15, 1), key='connection_status')],
        [sg.Text('LED Status:'), sg.Text('◯', size=(2, 1), key='led_status')],
        [sg.Button('Exit')]
    ]
    return layout

def toggle_led_status(window):
    """changes the window to simulate an LED with the hollow circle"""
    window['led_status'].update('◯' if window['led_status'].get() == '\u2B24' else '\u2B24')
    window.read(timeout=0)  # Force the window to update immediately



def main():
    """GUI that displays the data"""
    host = '10.102.13.149' # Put server ip address here laptop ip 10.160.5.147 pi 10.102.13.149
    port = 5001

    window = sg.Window('Client', create_layout(), finalize=True)

    try:
        s = socket.socket()
        s.connect((host, port))

        window['connection_status'].update('Connected', text_color='green')

        for i in range(50):
            event, values = window.read(timeout=2000)  # Poll events every 2 seconds
            if event == sg.WIN_CLOSED or event == 'Exit':
                break  # Exit the loop if the window is closed or "Exit" button is clicked

            data = collate_data(i + 1)
            send_data_to_server(s, data)

            # Alternate LED status every second while there is a connection
            if i % 2 == 0:
                window['led_status'].update('◯')
            else:
                window['led_status'].update('\u2B24 ')

        window['connection_status'].update('Disconnected', text_color='red')

    except Exception as e:
        print(f"Error: {e}")
        sg.popup_error(f"Error: {e}")

    finally:
        s.close()
        window.close()

if __name__ == "__main__":
    main()