import libusb_package
from ticlib import TicUSB

for dev in libusb_package.find(find_all=True):
    print(dev)

tic = TicUSB()

tic.halt_and_set_position(0)
tic.energize()
tic.exit_safe_start()

positions = [200, 150, 100, 50, 0]
for position in positions:
    tic.set_target_position(position)
    while tic.get_current_position() != tic.get_target_position():
        sleep(0.1)

tic.deenergize()
tic.enter_safe_start()
