import pandas as pd

product_structure = {
    "product": "bicycle",
    "time_to_complete": 2,
    "components": {
        "frame": {
            "quantity": 4,
            "time_to_complete": 2,
            "production_batch_size": 20,
            "starting_quantity": 5,
        },
         "wheel": {
             "quantity": 2,
             "time_to_complete": 1,
             "production_batch_size": 40,
             "starting_quantity": 10,
             "components": {
                 "rim": {
                     "quantity": 1,
                     "time_to_complete": 2,
                     "production_batch_size": 40,
                     "starting_quantity": 19,
                 },
                 "tire": {
                     "quantity": 1,
                     "time_to_complete": 1,
                     "production_batch_size": 80,
                    "starting_quantity": 15,
                 }
             }
         }
    }
}

def extract_components(structure, parent_time=0, parent_component=None):
    components = []
    if 'components' in structure:
        for component, sub_structure in structure['components'].items():
            time_to_complete = sub_structure.get('time_to_complete', 0)
            bias = time_to_complete + parent_time
            new_component = {
                'Component': component.capitalize(),
                'quantity': sub_structure['quantity'],
                'time_to_complete': time_to_complete,
                'production_batch_size': sub_structure['production_batch_size'],
                'starting_quantity': sub_structure['starting_quantity'],
                'bias': bias,
                'parent_component': parent_component
            }
            components.append(new_component)
            if 'components' in sub_structure:
                components.extend(extract_components(sub_structure, time_to_complete, component))
    return components


def get_component_by_name(components, component_name):
    return next((x for x in components if x['Component'].lower() == component_name.lower()), None)

def calculate_mps(starting_quantity, demand_production):
    schedule = []
    current_quantity = starting_quantity

    for week, row in demand_production.iterrows():
        current_quantity = current_quantity - row['Demand'] + row['Production']
        schedule.append((week, row['Demand'], row['Production'], current_quantity))

    return pd.DataFrame(schedule, columns=['Week', 'Demand', 'Production', 'Available'])

def generate_mrp_table(component, num_weeks, mps_schedule, components, parent_mrp):
    print(component)
    mrp_table = pd.DataFrame({
        'Week': range(num_weeks),
        'Gross Requirement': [0]*num_weeks,
        'Scheduled Receipts': [0]*num_weeks,
        'Forecasted On Hand': [0]*num_weeks,
        'Net Requirement': [0]*num_weeks,
        'Planned Order Receipts': [0]*num_weeks,
        'Planned Order Releases': [0]*num_weeks
    })

    current_stock = component['starting_quantity']
    production_batch_size = component['production_batch_size']
    mrp_table.at[0, 'Forecasted On Hand'] = current_stock

    for week in range(num_weeks):
        if week + component['bias'] < num_weeks:
            if component['parent_component']:
                parent = next((x for x in components if x['Component'].lower() == component['parent_component']), None)
                if parent:
                    mrp_table.at[week, 'Gross Requirement'] = parent_mrp.at[week, 'Planned Order Receipts'] * component['quantity']
            else:
                mrp_table.at[week, 'Gross Requirement'] = mps_schedule.at[week + 1, 'Production'] * component['quantity']
        
        this_week_gross_req = mrp_table.at[week, 'Gross Requirement']
        if week != 0:
            previous_week_on_hand = mrp_table.at[week - 1, 'Forecasted On Hand']
        else:
            previous_week_on_hand = mrp_table.at[week, 'Forecasted On Hand']
        net_requirement_current = previous_week_on_hand - this_week_gross_req
        
        if net_requirement_current < 0:
            if this_week_gross_req > 0:
                if week - component['bias'] < 0:
                    mrp_table.at[week, 'Scheduled Receipts'] = net_requirement_current*-1
                else:
                    mrp_table.at[week, 'Net Requirement'] = net_requirement_current*-1
                    batches_needed = (mrp_table.at[week, 'Net Requirement'] + production_batch_size - 1) // production_batch_size
                    planned_order_quantity = batches_needed * production_batch_size
                    mrp_table.at[week, 'Planned Order Releases'] = planned_order_quantity
                    mrp_table.at[week - component['bias'], 'Planned Order Receipts'] = planned_order_quantity
        mrp_table.at[week, 'Forecasted On Hand'] = previous_week_on_hand - this_week_gross_req + mrp_table.at[week, 'Planned Order Releases'] + mrp_table.at[week, 'Scheduled Receipts']

    return mrp_table

def return_ghp_table(demand_production):
    starting_quantity_prod = 2
    return calculate_mps(starting_quantity_prod, demand_production)

def return_mrp_tables(mps_schedule, number_of_weeks):
    components = extract_components(product_structure)
    print(components)
    frame = get_component_by_name(components, 'frame')
    wheel = get_component_by_name(components, 'wheel')
    rim = get_component_by_name(components, 'rim')
    tire = get_component_by_name(components, 'tire')

    frame_mrp = generate_mrp_table(frame, number_of_weeks, mps_schedule, components, None)
    wheel_mrp = generate_mrp_table(wheel, number_of_weeks, mps_schedule, components, None)
    rim_mrp = generate_mrp_table(rim, number_of_weeks, mps_schedule, components, wheel_mrp)
    tire_mrp = generate_mrp_table(tire, number_of_weeks, mps_schedule, components, wheel_mrp)

    return [('Frame', frame_mrp), ('Wheel', wheel_mrp), ('Rim', rim_mrp), ('Tire', tire_mrp)]

def update_product_structure(batch_sizes, start_quantities):
    print("updating")
    product_structure['components']['frame']['production_batch_size'] = int(batch_sizes['frame'])
    product_structure['components']['frame']['starting_quantity'] = int(start_quantities['frame'])
    product_structure['components']['wheel']['production_batch_size'] = int(batch_sizes['wheel'])
    product_structure['components']['wheel']['starting_quantity'] = int(start_quantities['wheel'])
    product_structure['components']['wheel']['components']['rim']['production_batch_size'] = int(batch_sizes['rim'])
    product_structure['components']['wheel']['components']['rim']['starting_quantity'] = int(start_quantities['rim'])
    product_structure['components']['wheel']['components']['tire']['production_batch_size'] = int(batch_sizes['tire'])
    product_structure['components']['wheel']['components']['tire']['starting_quantity'] = int(start_quantities['tire'])