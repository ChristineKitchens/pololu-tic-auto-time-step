import pytic
import time

# - Initialization -------------------------------------------

tic = pytic.PyTic()

# Connect to first available Tic Device serial number over USB
serialNums = tic.list_connected_device_serial_numbers()
print(serialNums[0])
tic.connect_to_serial_number(serial_number=serialNums[0])

# Load configuration file and apply settings
tic.settings.load_config("config.yml")
tic.settings.apply()

# - Set Start Time -------------------------------------------
while True:
    try:
        totalTimePeriod = float(
            input("What total time interval (in minutes) is the impellar running for?"))
        break
    except ValueError:
        print('Please enter a number.')

while True:
    try:
        maxSpeed = float(
            input("What is the desired max speed of the impellar"))
        break
    except ValueError:
        print('Please enter a number.')

while True:
    try:
        startSpeed = float(
            input("What is the desired start speed of the impellar?"))
        break
    except ValueError:
        print('Please enter a number.')

print(totalTimePeriod)
startTime = time.time()


while True:
    print(time.time())
    time.sleep(60.0 - ((time.time() - startTime) % 60.0))

# - Motion Command Sequence ----------------------------------

# Zero current motor position
tic.halt_and_set_position(0)

# Energize Motor
tic.energize()
tic.exit_safe_start()

# Move to listed positions
positions = [1000, 2000, 3000, 0]
for p in positions:
    tic.set_target_position(p)
    while tic.variables.current_position != tic.variables.target_position:
        time.sleep(0.1)

# De-energize motor and get error status
tic.enter_safe_start()
tic.deenergize()
print(tic.variables.error_status)
