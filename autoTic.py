import csv
from datetime import datetime
import os
import pytic
import signal
import sys
import readchar
import time

# - Functions ------------------------------------------------

# Energize motor


def start():
    tic.energize()
    tic.exit_safe_start()
    print('Energizing motor...')

# De-energize motor and get error status


def shutdown():
    tic.enter_safe_start()
    tic.deenergize()
    print('Deenergizing motor...')
    print(tic.variables.error_status)


# Load in settings


def load_settings():

    variable_csv = r'run_parameters.csv'

    with open(variable_csv, encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        global velocity_col
        global holding_col

        velocity_col = {'target_velocities': []}
        holding_col = {'holding_time': []}

        for record in reader:
            velocity_col['target_velocities'].append(
                int(record['target_velocities']))
            holding_col['holding_time'].append(int(record['holding_time']))

    print(f'Target Velocities: {velocity_col.values()}')
    print(f'Holding Times (seconds): {holding_col.values()}.')

# Enter settings manually


def manual_settings():
    get_target_velocities()
    get_holding_times()

# Get user input for target velocities


def get_target_velocities():
    global velocity_col

    velocity_col = {'target_velocities': []}

    while True:
        try:
            velocity_input = input('Enter target velocities (pulses/ 10,000 seconds): \n '
                                   'Please enter a list separated by a space \n')

            velocity_list = velocity_input.split()

            try:
                for i in velocity_list:
                    velocity_col['target_velocities'].append(int(i))
            except ValueError:
                print('Please use numbers.')

        finally:
            print(f'Target Velocities: {list(velocity_col.values())}')
            break

# Get user input for holding times


def get_holding_times():
    global holding_col

    holding_col = {'holding_time': []}

    while True:
        try:
            holding_input = input('Holding times for target velocities (secs): \n '
                                  'Please enter a list separated by a space \n')

            holding_list = holding_input.split()

            try:
                for i in holding_list:
                    holding_col['holding_time'].append(int(i))
            except ValueError:
                print('Please use numbers.')

        finally:
            print(f'Holding Times (seconds): {list(holding_col.values())}.')
            break

# Retrieve current timestamp in %d-%m-%Y, %H:%M:%S format


def current_time():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    return date_time

# When clicking Ctrl + C, confirm command and shutdown motor


def handler(signum, frame):
    print('\n')
    msg = "Ctrl-c was pressed. Do you really want to exit? Y/N \n"
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == 'y' or res == 'Y':
        print("Shutting down motor...")
        shutdown()
        exit(1)
    else:
        print("", end="\r", flush=True)
        print(" " * len(msg), end="", flush=True)  # clear the printed line
        print("    ", end="\r", flush=True)


signal.signal(signal.SIGINT, handler)

# - Initialization -------------------------------------------

tic = pytic.PyTic()

# Connect to first available Tic Device serial number over USB
serialNums = tic.list_connected_device_serial_numbers()
tic.connect_to_serial_number(serial_number=serialNums[0])

# Load configuration file and apply settings
tic.settings.load_config("config.yml")
tic.settings.apply()

# - Configure Run Parameters ---------------------------------

while True:
    try:
        core_name = input("Enter core name: ")
    finally:
        print(f'Core id: {core_name}')
        break

while True:
    try:
        endPrompt = input(
            'Import run parameters (I) or enter manually (M)? Enter I or M. \n')
    except ValueError:
        print('Incorrect input')
    finally:
        if endPrompt == 'I' or endPrompt == 'i':
            print("Importing from run_parameters.csv")
            load_settings()
            break
        elif endPrompt == 'M' or endPrompt == 'm':
            manual_settings()
            break
        else:
            print('Incorrect input')


# - Commence Run ---------------------------------------------

# Energize Motor
start()

while True:
    try:
        endPrompt = input('Begin run? Y/N \n')
    except ValueError:
        print('Incorrect input')
    finally:
        if endPrompt == 'Y' or endPrompt == 'y':
            print("Starting run...")
            break
        elif endPrompt == 'N' or endPrompt == 'n':
            print('Take your time :)')
        else:
            print('Incorrect input')

# Create new document to store time and velocity information
with open(f'sediment experiment core {core_name} {current_time().date()}.txt', 'a', newline='') as output_file:

    # Write header information to document
    output_writer = csv.writer(output_file, delimiter='\t')
    output_writer.writerow([f'Date: {current_time()}'])
    output_writer.writerow([f'User: {os.getlogin()}'])
    output_writer.writerow([f'Tic Device: {tic.settings.product}'])
    output_writer.writerow([f'Tic Serial Number: {serialNums[0]}'])
    output_writer.writerow(
        [f'Target Velocities: {list(velocity_col.values())}'])
    output_writer.writerow([f'Holding Times: {list(holding_col.values())}'])
    output_writer.writerow('')
    output_writer.writerow(['<<<Begin Data Collection>>>'])
    output_writer.writerow(['time', 'current_velocity'])

    counter = 0

    # Iterate through list of target velocities
    for key, value in velocity_col.items():
        for i in value:
            tic.set_target_velocity(int(i))
            holding_time = int(holding_col['holding_time'][counter])
            counter += 1
            # Maintain current velocity for pre-determined holding time
            while tic.variables.current_velocity != tic.variables.target_velocity:
                for t in range(holding_time, 0, -1):
                    time.sleep(1)
                    sys.stdout.write(
                        f'Current velocity: {i}     Current time: {current_time()}    Time to velocity change: {t} seconds \n')
                    # Clear printed line
                    sys.stdout.flush()
                    # Write current time and velocity to output file
                    output_writer.writerow(
                        [f'{current_time()}', f'{tic.variables.current_velocity}'])

    # De-energize motor and get error status
    while True:
        try:
            endPrompt = input('Stop Motor? Y/N  ')
        except ValueError:
            print('Incorrect input')
        finally:
            if endPrompt == 'Y' or endPrompt == 'y':
                print('Shutting down motor...')
                shutdown()
                break
            elif endPrompt == 'N' or endPrompt == 'n':
                print('Use your spiral power!')
            else:
                print('Incorrect input')
