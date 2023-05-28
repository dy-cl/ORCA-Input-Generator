from openbabel import openbabel as ob
import re
import datetime
import os

def select_from_menu(options):
    """
    Reusable menu function.

    Parameters:
    - options (list): List of options for the user to choose from.

    Returns:
    - choice (int): The user's choice.
    """

    print()
    max_width = max(len(option) for option in options)  #Find the maximum width of the options

    for i, option in enumerate(options, 1):
        centered_option = option.center(max_width)  #Center the option within the maximum width
        print(f"{i}. {centered_option.strip()}", end = " | ")

        if i % 6 == 0:  #Add a new line after every 6th option
            print()  

    print()

    choice = int(input("Enter your choice: "))
    print()

    if choice not in range(1, len(options) + 1):
        print("Invalid choice. Please try again.")
        return select_from_menu(options)

    return choice

#to .xyz
def to_xyz(molecule, molecule_format):
    """
    Convert molecular input to .xyz format.

    Parameters:
    - molecule (str): Molecular input string.
    - molecule_format (str): Initial format type of the molecular string.

    Returns:
    - None: If xyz coordinates could not be generated.
    - xyz_content: Otherwise.
    """
    #Create Open Babel molecule object
    mol = ob.OBMol()

    #Set the input and output formats based on the molecule format
    if molecule_format == 'SMILES':
        in_format = "smi"
    elif molecule_format == 'InChI':
        in_format = "inchi"
 
    obConversion = ob.OBConversion()
    obConversion.SetInAndOutFormats(in_format, "xyz")

    if not obConversion.ReadString(mol, molecule):
        print("Error: Failed to read the molecule.")
        return None

    #Generate 3D coordinates
    builder = ob.OBBuilder()
    if not builder.Build(mol):
        print("Error: Failed to generate 3D coordinates.")
        return None

    #Add implicit hydrogens
    mol.AddHydrogens()

    #Write to XYZ format
    xyz_content = obConversion.WriteString(mol)

    lines = xyz_content.split('\n')
    xyz_content = '\n'.join(lines[2:])
     
    return xyz_content
 
    
#Add timestamp to file name to avoid overwriting
def generate_unique_filename(file_name):
    base_name, extension = os.path.splitext(file_name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

#File generators
class Input_Generator:

    #Reusable file writer with varying parameters
    @staticmethod
    def write_input_file(file_name, method, basis_set, coordinate_type, charge, spin, xyz_content, calculation_type):
        """
        Reusable file writer.

        Parameters:
        - file_name (str): Name with which the file is saved.
        - method (str): Method.
        - basis_set (str): Basis set.
        - coordinate_type (str): Currently only xyz is supported, expanded later.
        - charge (int): Integer value for molecule charge (typically 0).
        - spin (int): Integer value for molecule spin (typically 0).
        - xyz_content (str): Cartesian coordinates.
        - calculation_type (str): Calcultion to be requested from ORCA (eg. Optimization).
        """

        spinmult = (2*spin) + 1

        unique_file_name = generate_unique_filename(file_name)

        calculation_statements = {
        'energy': '\n',
        'optimization': '! OPT\n',
        'vibration': '! FREQ\n',
        'vib + freq': '! OPT\n!FREQ\n',
        'nmr' : '! NMR TightSCF\n', #Use default SCF setting for now
        'uv' : '\n'
        }

        try:  
            with open(unique_file_name, 'w') as f:
                f.write(f'#\n'
                        f'# {file_name.replace(".inp", "")}\n' #Input title
                        f'#\n'
                        f'%maxcore 3000\n' #Memory to use
                        f'\n')
                
                if calculation_type == 'nmr':
                    f.write(f'! {method} {basis_set} AutoAux\n') #Use automatic auxilliary basis set for NMR add options later
                
                else:
                    f.write(f'! {method} {basis_set}\n')

                f.write(calculation_statements.get(calculation_type, '\n'))

                if calculation_type == 'uv':
                    f.write(f'%cis\n'  #Use default excited state method and default parameters add options later
                            f'  nroots 8\n'
                            f'  maxdim 64\n'
                            f'end\n')

                f.write(f'\n'
                        f'* {coordinate_type} {charge} {spinmult} \n'
                        f'{xyz_content}'
                        f'*')
                
                if calculation_type == 'nmr':
                    f.write(f'\n'
                            f'%eprnmr\n'
                            f'  Nuclei = all C {{ shift }}\n'
                            f'  Nuclei = all H {{ shift }}\n'
                            f'end\n')
    
        except IOError as e:
            print(f"Error writing to file: {str(e)}")

    """
    Calculation type specific functions located below here. Takes inputs obtain in main() and uses them to create
    the calculation specific parameters that are passed to write_input_file.

    Parameters:
    - method_choice (int): Numerical user input for method choice.
    - basis_choice (int): Numerical user input for basis set choice.
    - molecule (str): Molecular input string.
    - methods (list): List of all avaliable methods.
    - basis_sets (list): List of all avaliable basis sets.
    - orca_tasks (list): List of all avaliavle calculation types.
    - calculation_choice (int):  Numerical user input for calculation type.
    - name (str): User input for molecule name.
    - molecule_format (str): Formant of molecular input string.
    """
    #Energy calculation
    @staticmethod
    def energy_input(method_choice, basis_choice, molecule, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'energy'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
      
    
    #Geometry optimization
    @staticmethod
    def optimization_input(method_choice, basis_choice, molecule, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'optimization'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
        
    
    #Vibrational frequency calculation
    @staticmethod
    def vibrational_input(method_choice, basis_choice, molecule, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'vibration'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
       
   
    #Optimization and vibrational frequency calculation
    @staticmethod
    def opt_freq_input(method_choice, basis_choice, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'vib + freq'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
       
        
    #NMR calculation
    @staticmethod
    def nmr_input(method_choice, basis_choice, molecule, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'nmr'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
 
     
    #Excited states and UV-vis calculation
    @staticmethod
    def UV_input(method_choice, basis_choice, molecule, methods, basis_sets, orca_tasks, calculation_choice, name, molecule_format):
        if molecule == 'SMILES':
            molecule = molecule.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{name}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'uv'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = to_xyz(molecule, molecule_format)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
      
    
def main():
    """
    Collects the following parameters to pass to file generator functions:

    - input_types (str): The format type of the molecular input.
    - orca_tasks (str): Selection of calculation to write in the input file.
    - methods (str): Selection of method to write in the input file.
    - basis_sets (str): Selection of basis sets to write in the input file.
    - molecule (str): Molecule formatted according to the style chosen in input_types.

    """

    input_types = ["SMILES", "InChI"]
    orca_tasks = ["Molecular Energy", "Geometry Optimization", "Vibrational Frequencies", "Optimize + Vib-Freq", "NMR", "UV-vis + Excited state"]
    methods = ['B3LYP', 'HF', 'MP2', 'CCSD']
    basis_sets = ['STO-3G', '3-21G', '6-31G(d)', '6-311+G(2d,p)', 'def2-SVP', 'def2-TZVP', 'def2-TZVPP', 'def2-QZVPP']

    print("Select format of molecular input: ")
    input_selection = select_from_menu(input_types)
    molecule_format = str(input_types[input_selection - 1])

    print("Select Calculation: ")
    calculation_choice = select_from_menu(orca_tasks)

    calculation_functions = {
        1: Input_Generator.energy_input,
        2: Input_Generator.optimization_input,
        3: Input_Generator.vibrational_input,
        4: Input_Generator.opt_freq_input,
        5: Input_Generator.nmr_input,
        6: Input_Generator.UV_input
    }

    if calculation_choice in calculation_functions:
        print("Select method: ")
        method_choice = select_from_menu(methods)
        print("Select basis set: ")
        basis_choice = select_from_menu(basis_sets)
        molecule = input("Input molecule in " + str(input_types[input_selection - 1]) + " format: ")

        #Needs to be tested more
        if molecule_format == 'SMILES' and not re.match(r'^[^J][0-9BCOHNSOPrIFla@+\-\[\]\(\)\\\/%=#$,.~&!]+', molecule): 
            print("Invalid SMILES format.")
            return
        elif molecule_format == 'InChI' and not re.match(r'^InChI\=1S?\/[A-Za-z0-9\.]+(\+[0-9]+)?(\/[cnpqbtmsih][A-Za-z0-9\-\+\(\)\,\/\?\;\.]+)*$', molecule):
            print("Invalid InChI format.")
            return
        
        name = input("Enter molecule name: ")

        calculation_functions[calculation_choice](method_choice, basis_choice, molecule, methods, basis_sets, 
                                                  orca_tasks, calculation_choice, name, molecule_format)

    print('File written')

#Run main
if __name__ == '__main__':
    main()