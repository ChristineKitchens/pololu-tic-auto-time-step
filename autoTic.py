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

# Retrieve current timestamp in %d-%m-%Y, %H:%M:%S format


def current_time():
    current_time = datetime.now()
    time_stamp = current_time.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    return date_time

# When clicking Ctrl + C, confirm command and shutdown motor


def handler(signum, frame):
    msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
    print(msg, end="", flush=True)
    res = readchar.readchar()
    if res == 'y':
        print("Shutting down motor...")
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

# - Load in Settings -----------------------------------------

variable_csv = r'run_parameters.csv'

with open(variable_csv, encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)

    velocity_col = {'target_velocities': []}
    holding_col = {'holding_time': []}

    for record in reader:
        velocity_col['target_velocities'].append(record['target_velocities'])
        holding_col['holding_time'].append(record['holding_time'])


# - Configure Run --------------------------------------------
# while True:
#     try:
#         maxSpeed = float(
#             input("Enter target velocities: "))
#         print(f'Max speed: {maxSpeed}')
#         break
#     except ValueError:
#         print('Please enter a number.')

# while True:
#     try:
#         totalTimePeriod = float(
#             input("Holding time for target velocities (secs):"))
#         print(f'Holding Time: {totalTimePeriod} seconds.')
#         break
#     except ValueError:
#         print('Please enter a number.')


# - Motion Command Sequence ----------------------------------

# Zero current motor position
tic.halt_and_set_position(0)

# Energize Motor
start()

# Show configuration
print(f'Target Velocity: {tic.variables.target_velocity}')
print(f'Target Position: {tic.variables.target_position}')
print(f'Current Velocity: {tic.variables.current_velocity}')
print(f'Current Position: {tic.variables.current_position}')
print(f'Planning Mode: {tic.variables.planning_mode}')

# Create new document to store time and velocity information
with open(f'sediment_experiment_{time.time()}', 'a', newline='') as output_file:
    # Write header information to document
    output_writer = csv.writer(output_file, delimiter='\t')
    output_writer.writerow([f'Date: {current_time()}'])
    output_writer.writerow([f'User: {os.getlogin()}'])
    output_writer.writerow([f'Tic Device: {tic.settings.product}'])
    output_writer.writerow([f'Tic Serial Number: {serialNums[0]}'])
    output_writer.writerow([f'Target Velocities: {velocity_col.values()}'])
    output_writer.writerow([f'Holding Time: {holding_col.values()}'])
    output_writer.writerow(['<<<Begin Data Collection>>>'])
    output_writer.writerow(['time', 'current_velocity'])

    # Iterate through list of target velocities
    for key, value in velocity_col.items():
        for i in value:
            print(i)
            tic.set_target_velocity(int(i))
            # Maintain current velocity for pre-determined holding time
            while tic.variables.current_velocity != tic.variables.target_velocity:
                for t in range(int(holding_col['holding_time'][0]), 0, -1):
                    time.sleep(1)
                    sys.stdout.write(f'Time to velocity change: {t} seconds')
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
                print("Shutting down motor...")
                shutdown()
                break
            elif endPrompt == 'N' or endPrompt == 'n':
                print("Use your spiral power!")
            else:
                print('Incorrect input')
