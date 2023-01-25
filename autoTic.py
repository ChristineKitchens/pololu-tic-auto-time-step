import csv
import pytic
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

    total_time_col = {'total_time': []}
    velocity_col = {'target_velocities': []}
    holding_col = {'holding_time': []}

    for record in reader:
        total_time_col['total_time'].append(record['total_time'])
        velocity_col['target_velocities'].append(record['target_velocities'])
        holding_col['holding_time'].append(record['holding_time'])


# - Set Start Time -------------------------------------------
# while True:
#     try:
#         totalTimePeriod = float(
#             input("Enter holding time for each target velocity"))
#         print(f'Holding Time: {totalTimePeriod} minutes.')
#         break
#     except ValueError:
#         print('Please enter a number.')

# while True:
#     try:
#         maxSpeed = float(
#             input("What is the desired max speed of the impellar"))
#         print(f'Max speed: {maxSpeed}')
#         break
#     except ValueError:
#         print('Please enter a number.')

# while True:
#     try:
#         startSpeed = float(
#             input("What is the desired start speed of the impellar?"))
#         print(f'Start Speed: {startSpeed}')
#         break
#     except ValueError:
#         print('Please enter a number.')


# startTime = time.time()
# endTime =

# output = open(f'sediment_experiment_{time.time()}', 'a')


# - Motion Command Sequence ----------------------------------

# Zero current motor position
tic.halt_and_set_position(0)

# Energize Motor
start()

tic.set_target_velocity(1000000)
# tic.set_target_position(100)

print(f'Target Velocity: {tic.variables.target_velocity}')
print(f'Target Position: {tic.variables.target_position}')
print(f'Current Velocity: {tic.variables.current_velocity}')
print(f'Current Position: {tic.variables.current_position}')
print(f'Planning Mode: {tic.variables.planning_mode}')

# De-energize motor and get error status
while True:
    try:
        endPrompt = input('Stop Motor? Y/N  ')
    except ValueError:
        print('Incorrect input')
    finally:
        if endPrompt == 'Y' or endPrompt == 'y':
            shutdown()
            break
        elif endPrompt == 'N' or endPrompt == 'n':
            print("Use your spiral power!")
        else:
            print('Incorrect input')
