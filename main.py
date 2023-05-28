from openbabel import openbabel as ob
import datetime
import os

#Menu wrapper function to reuse
def select_from_menu(options):

    print()
    max_width = max(len(option) for option in options)  # Find the maximum width of the options

    for i, option in enumerate(options, 1):
        centered_option = option.center(max_width)  # Center the option within the maximum width
        print(f"{i}. {centered_option.strip()}", end=" | ")

        if i % 6 == 0:  #Add a new line after every 6th option
            print()  

    print()

    choice = int(input("Enter your choice: "))
    print()

    if choice not in range(1, len(options) + 1):
        print("Invalid choice. Please try again.")
        return select_from_menu(options)

    return choice

#SMILES to .xyz
def smiles_to_xyz(smiles):
    #Create Open Babel molecule object from SMILES
    mol = ob.OBMol()
    obConversion = ob.OBConversion()
    obConversion.SetInAndOutFormats("smi", "xyz")
    obConversion.ReadString(mol, smiles)

    #Generate 3D coordinates
    builder = ob.OBBuilder()
    builder.Build(mol)

    #Add implicit hydrogens
    mol.AddHydrogens()

    #Write to XYZ format
    xyz_content = obConversion.WriteString(mol)

    lines = xyz_content.split('\n') #Split the string into lines

    xyz_content = '\n'.join(lines[2:]) #Join the lines, excluding the first two

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

    #Energy calculation
    @staticmethod
    def energy_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type
        calculation_type = 'energy'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
    
    #Geometry optimization
    @staticmethod
    def optimization_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  #Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type 
        calculation_type = 'optimization'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)

    #Vibrational frequency calculation
    @staticmethod
    def vibrational_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type 
        calculation_type = 'vibration'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): "))   
        xyz_content = smiles_to_xyz(SMILES)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)

    #Optimization and vibrational frequency calculation
    @staticmethod
    def opt_freq_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type 
        calculation_type = 'vib + freq'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
        
    #NMR calculation
    @staticmethod
    def nmr_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type 
        calculation_type = 'nmr'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
        
    #Excited states and UV-vis calculation
    @staticmethod
    def UV_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = (f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_"
                     f"{SMILES}_{orca_tasks[calculation_choice - 1].replace(' ', '-')}.inp") #Remove blank space from file name (prevents opening error)
        coordinate_type = 'xyz' #Coordinate type 
        calculation_type = 'uv'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)

#Main function
def main():
    orca_tasks = ["Molecular Energy", "Geometry Optimization", "Vibrational Frequencies", "Optimize + Vib-Freq", "NMR", "UV-vis + Excited state"]
    methods = ['B3LYP', 'HF', 'MP2', 'CCSD']
    basis_sets = ['STO-3G', '3-21G', '6-31G(d)', '6-311+G(2d,p)', 'def2-SVP', 'def2-TZVP', 'def2-TZVPP', 'def2-QZVPP']

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
        SMILES = input("Input molecule in SMILES format: ")

        calculation_functions[calculation_choice](method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice)

    print('File written')

#Run main
if __name__ == '__main__':
    main()