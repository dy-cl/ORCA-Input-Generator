from openbabel import openbabel as ob


#Menu wrapper function to reuse
def select_from_menu(options):
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    print('\n')
    choice = int(input("Enter choice: "))
    print('\n')

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

    lines = xyz_content.split('\n')  #Split the string into lines

    xyz_content = '\n'.join(lines[2:])  #Join the lines, excluding the first two

    return xyz_content


class Input_Generator:
    @staticmethod
    def write_input_file(file_name, method, basis_set, coordinate_type, xyz_content, is_optimization):
        with open(file_name, 'w') as f:
            f.write(f'#\n'
                    f'#{file_name}\n'
                    f'#\n'
                    f'%maxcore 3000\n'
                    f'\n'
                    f'!{method} {basis_set}\n')

            if is_optimization:
                f.write('!OPT\n')
            
            f.write(f'\n'
                    f'{coordinate_type}\n'
                    f'{xyz_content}'
                    f'*')

    @staticmethod
    def energy_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = '* xyz 0 1'
        xyz_content = smiles_to_xyz(SMILES)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], coordinate_type, xyz_content, False)
    
    @staticmethod
    def optimization_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice):
        SMILES = SMILES.replace('(', '').replace(')', '').replace('[', '').replace(']', '')  # Remove () and []
        file_name = f"{methods[method_choice - 1]}_{basis_sets[basis_choice - 1]}_{SMILES}_{orca_tasks[calculation_choice - 1]}.inp"
        coordinate_type = '* xyz 0 1'
        xyz_content = smiles_to_xyz(SMILES)
        
        Input_Generator.write_input_file(file_name, methods[method_choice - 1], basis_sets[basis_choice - 1], coordinate_type, xyz_content, True)

#Main function
def main():
    orca_tasks = ["Energy", "Geometry Optimization", "Molecular Orbital Energies", "Vibrational Frequencies", "NMR"]
    methods = ['B3LYP']
    basis_sets = ['STO-3G']

    print("Select Calculation: ")
    calculation_choice = select_from_menu(orca_tasks)

    if calculation_choice in [1, 2, 3, 4, 5]:
        print("Select method: ")
        method_choice = select_from_menu(methods)
        print("Select basis set: ")
        basis_choice = select_from_menu(basis_sets)
        SMILES = input("Input molecule in SMILES format: ")
        
        if calculation_choice == 1:
            Input_Generator.energy_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice)
        elif calculation_choice == 2:
            Input_Generator.optimization_input(method_choice, basis_choice, SMILES, methods, basis_sets, orca_tasks, calculation_choice)

    print('File written')


#Run main
if __name__ == '__main__':
    main()