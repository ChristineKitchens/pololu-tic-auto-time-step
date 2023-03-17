import csv
from datetime import datetime
from datetime import timedelta
# from itertools import batched
# from itertools import islice
import libusb_package
import os
import signal
import sys
import readchar
from ticlib import TicUSB
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
            holding_col['holding_time'].append(float(record['holding_time']))

    print(f'Target Velocities: {list(velocity_col.values())}')
    print(f'Holding Times (seconds): {list(holding_col.values())}.')

# Split target velocities and/or holding times into smaller batches


# def split_imported_data(x):
#     for batch in batched(list(x.values()), 10):
#         print(batch)

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
            velocity_input = input('Enter target velocities (microsteps/ 10,000 seconds): \n'

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
            holding_input = input('Holding times for target velocities (secs): \n'
                                  'Please enter a list separated by a space \n')

            holding_list = holding_input.split()

            try:
                for i in holding_list:
                    holding_col['holding_time'].append(int(i))
            except ValueError:
                print('Please use numbers.')

        finally:
            print(
                f'Holding Times (seconds): {list(holding_col.values())}.')
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

for dev in libusb_package.find(find_all=True):
    print(dev)


tic = TicUSB()


# - Configure Run Parameters ---------------------------------

while True:
    try:
        project_name = input("Enter project name: ")
    finally:
        print(f'Project: {project_name}')
        break

while True:
    try:
        core_name = input("Enter core name: ")
    finally:
        print(f'Core id: {core_name}')
        break

while True:
    try:
        replicate_id = input("Enter replicate ID: ")
    finally:
        print(f'Replicate: {replicate_id}')
        break

while True:
    try:
        material_name = input("Enter material (e.g. marine sand): ")
    finally:
        print(f'Material: {material_name}')
        break

while True:
    try:
        size_fraction = input("Enter size fraction: ")
    finally:
        print(f'Size fraction: {size_fraction}')
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

# Zero current motor position
tic.halt_and_set_position(0)

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
with open(f'{project_name}_{current_time().date().strftime("%Y%m%d")}_{material_name}_{size_fraction}_{replicate_id}.txt', 'a', newline='') as output_file:

    # Write header information to document
    output_writer = csv.writer(output_file, delimiter='\t')
    output_writer.writerow([f'Date: {current_time()}'])
    output_writer.writerow([f'User: {os.getlogin()}'])
    output_writer.writerow([f'Tic Device: TIC-T500'])
    output_writer.writerow([f'Tic Serial Number: 00387558'])

    output_writer.writerow(
        [f'Target Velocities: {list(velocity_col.values())}'])
    output_writer.writerow(
        [f'Holding Times: {list(holding_col.values())}'])
    output_writer.writerow('')
    output_writer.writerow(['<<<Begin Data Collection>>>'])
    output_writer.writerow(['time', 'current_velocity'])

    total_run_time = sum(holding_col['holding_time'])
    run_time_counter = 0
    counter = 0

    # Iterate through list of target velocities
    for key, value in velocity_col.items():
        for i in value:
            tic.set_target_velocity(i)
            holding_time = int(holding_col['holding_time'][counter])

            # Maintain current velocity for pre-determined holding time
            while tic.get_current_velocity() != tic.get_target_velocity():

                for t in range(holding_time, 0, -1):
                    time.sleep(1)
                    remaining_run_time = timedelta(
                        seconds=total_run_time-run_time_counter)
                    sys.stdout.write(
                        f'Current velocity: {i}     Current time: {current_time()}    Time to velocity change: {t} seconds  Time to run end: {remaining_run_time} \n')
                    # Clear printed line
                    sys.stdout.flush()
                    # Write current time and velocity to output file
                    output_writer.writerow(
                        [f'{current_time()}', f'{tic.get_current_velocity()}'])

                    run_time_counter += 1

            counter += 1

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
