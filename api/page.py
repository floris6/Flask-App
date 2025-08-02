from flask import Flask, render_template, request, render_template_string
from main import get_molecule, generate_model
from flask import send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Common name, IUPAC name, Molecule formula

compound = "H2S"
common_name, iupac_name, formula, mass, smiles, atoms_legend, cid, inchi_key = get_molecule(compound)
print(f"3. Data received and activating generate_model {cid} {mass}")
generate_model(smiles)

print(inchi_key)







print('5. Start App')

app = Flask(__name__, template_folder='../templates', static_folder='../static')

@app.route('/', methods=['GET', 'POST'])
def home():
    # Calculate button pressed? --> active function: look for part in the molecule, calculate the pH based on that (LLM) (send: inchikey)
    return render_template('index.html', common_name=common_name, atoms_legend=atoms_legend, iupac_name=iupac_name, formula=formula, mass=mass)

@app.route('/<input_compound>')
def search(input_compound):
    # Calculate button pressed? --> active function: calculate (send: inchikey)

    try:
        common_name, iupac_name, formula, mass, smiles, atoms_legend, cid, inchi_key = get_molecule(input_compound)
        generate_model(smiles)
        if not common_name or not formula or not mass:
            error_msg = f"Data incomplete for molecule: {input_compound}"
            return render_template('error.html', error_msg=error_msg)
        return render_template('search.html', common_name=common_name, atoms_legend=atoms_legend, iupac_name=iupac_name,
                               formula=formula, mass=mass)
    except Exception as e:
        error_msg = f"Error processing molecule '{input_compound}': {str(e)}"
        return render_template('error.html', error_msg=error_msg)


# This is required for Vercel to expose your app as a handler
def handler(environ, start_response):
    return app(environ, start_response)



if __name__ == '__main__':
    app.run(debug=True)