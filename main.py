from openbabel import openbabel as ob

#Menu wrapper function to reuse
def select_from_menu(options):

    print('\n')
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}", end="\t")
    print()  # Print a new line after the menu options

    choice = int(input("Enter choice: "))
    print()  # Print a new line after the choice

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

    #Write to XYZ format
    xyz_content = obConversion.WriteString(mol)

    lines = xyz_content.split('\n') #Split the string into lines

    xyz_content = '\n'.join(lines[2:]) #Join the lines, excluding the first two

    return xyz_content


#File generators
class Input_Generator:

    #Reusable file writer with varying parameters
    @staticmethod
    def write_input_file(file_name, method, basis_set, coordinate_type, charge, spin, xyz_content, calculation_type):

        spinmult = (2*spin) + 1

        calculation_statements = {
        'energy': '\n',
        'optimization': '!OPT\n',
        'vibration': '!FREQ\n',
        'vib + freq': '!OPT\n!FREQ\n'
        }
         
        with open(file_name, 'w') as f:
            f.write(f'#\n'
                    f'#{file_name}\n' #Input title
                    f'#\n'
                    f'%maxcore 3000\n' #Memory to use
                    f'\n'
                    f'!{method} {basis_set}\n')

            f.write(calculation_statements.get(calculation_type, '\n'))
            
            f.write(f'\n'
                    f'* {coordinate_type} {charge} {spinmult} \n'
                    f'{xyz_content}'
                    f'*')

    #Energy calculation
    @staticmethod
    def energy_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = 'xyz'
        calculation_type = 'energy'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)
    
    #Geometry optimization
    @staticmethod
    def optimization_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = 'xyz' #Coordinate type and spin, spin should be added as option
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
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = 'xyz' #Coordinate type and spin, spin should be added as option
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
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = 'xyz' #Coordinate type and spin, spin should be added as option
        calculation_type = 'vib + freq'
        charge = input("Enter the charge (This is typically 0): ") 
        spin = int(input("Enter the spin (This is typically 0): ")) 
        xyz_content = smiles_to_xyz(SMILES)

        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], 
                                         coordinate_type, charge, spin, xyz_content, calculation_type)

#Main function
def main():
    orca_tasks = ["Energy", "Geometry Optimization", "Vibrational Frequencies", "Optimize + Vib Freq"]
    methods = ['B3LYP', 'HF', 'MP2', 'CCSD']
    basis_sets = ['STO-3G', '3-21G', '6-31G(d)', 'def2-SVP']

    print("Select Calculation: ")
    calculation_choice = select_from_menu(orca_tasks)

    calculation_functions = {
        1: Input_Generator.energy_input,
        2: Input_Generator.optimization_input,
        3: Input_Generator.vibrational_input,
        4: Input_Generator.opt_freq_input
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