# Polulu Tic Automated Incremental Time Step
Modification of Pololu Tic Control Center that automatically incrementally increases speed based on inputs. This script builds upon scripts in the [Pololu-Tic-Software Github](https://github.com/pololu/pololu-tic-software) and [PyTic Github](https://github.com/AllenInstitute/pytic).

# Prerequisites
Requires [Tic Software and Drivers for Windows](https://www.pololu.com/file/0J1325/pololu-tic-1.8.2-win.msi) provided by Pololu to be installed. Also requires installation of [PyTic Python wrapper](https://github.com/AllenInstitute/pytic). Install the PyTic package and PyYAML dependency using the following script:

```
C:\> pip install pytic
C:\> pip install pyyaml==5.4.1
```
Make sure to install the 5.4.1 version of PyYAML specifically since newer versions require an additional argument that pytic does not account for.
# Config.yml
Use of the pytic package requires the creation of a config.yml file. To find appropriate codes for the PyYAML file, please reference the codes listed in the [pytic_protocol.py](https://github.com/AllenInstitute/pytic/blob/master/pytic/pytic_protocol.py) file

# External Resources
- [logging Library](https://docs.python.org/3/library/logging.html)
- [Pololu-Tic-Software Github](https://github.com/pololu/pololu-tic-software)
- [Pololu Tic Manual](https://www.pololu.com/docs/0J71)
- [Pololu Tic Resources](https://www.pololu.com/product/3131/resources)
- [PyTic Github](https://github.com/AllenInstitute/pytic)
- [tic.h](https://github.com/pololu/pololu-tic-software/blob/master/include/tic.h)
- [tic_protocol.h](https://github.com/pololu/pololu-tic-software/blob/a75c204a2255554e21cc5351c528d930ba5d2c38/include/tic_protocol.h)
- [Tic Software and Drivers for Windows](https://www.pololu.com/file/0J1325/pololu-tic-1.6.2-win.msi)
