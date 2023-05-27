This is a python script to generate ORCA .inp files for a variety of calculation types. Currently creation of inputs for molecular energy, geometry optimization, vibrational frequencies, opt + vib freq, and NMR calculations are supported, a few different methods and basis sets are avaliable.

The script takes molecular input in the SMILES format and converts it into a .xyz format to use in the input file. The generated input file is placed in the same location as the script itself. Additionally, the generated file is named according to the SMILES input, calculation type, method and basis set, and a timestamp to prevent overwriting.

Future additions: 
-Allow for different molecular inputs other than SMILES
-Support for more calculation types (UV-vis, Transistion state optimization, Coordinate scans)
-Add more methods and basis sets
-More in-depth options for calculations such as auxilliary basis sets


