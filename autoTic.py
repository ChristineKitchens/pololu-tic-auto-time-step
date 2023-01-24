from ticlib import TicUSB

tic = TicUSB(product='TIC_500')

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
