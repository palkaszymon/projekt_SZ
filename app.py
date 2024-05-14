from flask import Flask, render_template, request
import pandas as pd
from mrp import return_mrp_tables, return_ghp_table, update_product_structure

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        batch_sizes = {
            'frame': request.form['frame_batch_size'],
            'wheel': request.form['wheel_batch_size'],
            'rim': request.form['rim_batch_size'],
            'tire': request.form['tire_batch_size']
        }
        start_quantities = {
            'frame': request.form['frame_start_qty'],
            'wheel': request.form['wheel_start_qty'],
            'rim': request.form['rim_start_qty'],
            'tire': request.form['tire_start_qty']
        }
        
        update_product_structure(batch_sizes, start_quantities)
        weeks = request.form.getlist('week[]')
        demands = request.form.getlist('demand[]')
        productions = request.form.getlist('production[]')
        data = {
            'Week': [int(w) for w in weeks],
            'Demand': [int(d) for d in demands],
            'Production': [int(p) for p in productions]
        }
        df = pd.DataFrame(data)
        df.set_index('Week', inplace=True)
        df.sort_index(inplace=True)
        all_weeks = pd.DataFrame(index=range(1, 11), columns=['Demand', 'Production'])
        all_weeks = all_weeks.fillna(0)
        df = df.combine_first(all_weeks)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Week'}, inplace=True)
        mrp_tables = return_mrp_tables(df, len(df))
        
        df.set_index('Week', inplace=True)
        ghp_df = return_ghp_table(df)
        ghp_html = ghp_df.T.to_html(classes='table table-striped')
        
        # Correct handling of tuple unpacking in the list comprehension
        mrp_html = [(name, table.to_html(classes='table table-striped')) for name, table in mrp_tables]

        return render_template('results.html', ghp=ghp_html, mrp=mrp_html)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
