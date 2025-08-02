import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
import py3Dmol
import os
from PIL import Image
import base64
from io import BytesIO
import pubchempy as pcp


def get_molecule(compound):
    compound_data = None

    # Try CID search if input is a number
    try:
        cid = int(compound)
        compounds = pcp.get_compounds(cid, 'cid', record_type='2d')
        if compounds:
            compound_data = compounds[0]
            print(f"1. Compound found by CID: {cid}")
    except ValueError:
        pass

    # If not found, try name/IUPAC
    if not compound_data:
        try:
            compounds = pcp.get_compounds(compound, 'name', record_type='2d')
            if compounds:
                compound_data = compounds[0]
                print(f"1. Compound found by common name/IUPAC: {compound}")
        except Exception:
            pass

    # If still not found, try formula (may return multiple)
    if not compound_data:
        try:
            compounds = pcp.get_compounds(compound, 'formula', record_type='2d')
            if compounds:
                compound_data = compounds[0]
                print(f"1. Compound found by molecular formula: {compound}")
        except Exception:
            pass

    if not compound_data:
        print('2. DATA NOT FOUND: Invalid Name/ID/Formula')
        return None

    compound_dict = compound_data.to_dict()
    cid = compound_data.cid
    inchi_key = compound_data.inchikey
    common_name = compound_data.synonyms[0]
    formula = compound_data.molecular_formula
    smiles = compound_data.canonical_smiles
    iupac_name = compound_data.iupac_name
    if len(iupac_name) > 30:
        iupac_name = iupac_name[:30] + '...'
    mass = compound_data.molecular_weight
    atoms_element = compound_dict.get("atoms", [])
    atoms_list = sorted(set(atom["element"] for atom in atoms_element))
    color_map = {
        'C': 'gray', 'H': 'white', 'O': 'red', 'N': 'blue',
        'Cl': 'green', 'F': 'cyan', 'P': 'orange', 'S': 'yellow'
    }
    atoms_legend = {}
    for atom in atoms_list:
        atom_color = color_map.get(atom, 'black')
        atoms_legend[atom] = atom_color

    # If SMILES missing, try alternative from props
    if not smiles and 'record' in compound_dict and 'props' in compound_dict['record']:
        for prop in compound_dict['record']['props']:
            urn = prop.get('urn', {})
            if urn.get('label') == 'SMILES' and urn.get('name') == 'Connectivity':
                smiles = prop.get('value', {}).get('sval')
                break

    print("2. DATA FOUND")
    return common_name, iupac_name, formula, mass, smiles, atoms_legend, cid, inchi_key


def generate_model(smiles):

    # 3D
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())  # 3D coordinates
    AllChem.UFFOptimizeMolecule(mol)

    mol_block = Chem.MolToMolBlock(mol)

    viewer = py3Dmol.view(width=400, height=400)
    viewer.addModel(mol_block, 'mol')
    viewer.setStyle({'stick': {}})
    viewer.setBackgroundColor('white')
    viewer.zoomTo()
    html_str = viewer._make_html()

    # Inject SPIN
    spin_code = "\n<script>viewer.animate({mode: 'spin', speed: 1});</script>\n"
    html_str = html_str.replace('</body>', f'{spin_code}</body>')

    with open('templates/tmp.html', 'w') as f:
        f.write(html_str)

    #2D
    mol2d = Chem.MolFromSmiles(smiles)
    AllChem.Compute2DCoords(mol2d)
    img = Draw.MolToImage(mol2d, size=(300, 300))
    img_path = 'static/tmp_2d.png'
    img.save(img_path)
    print("4. Model HTML done for tmp.html")




