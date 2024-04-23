import pandas as pd

product_structure = {
    "product": "bicycle",
    "time_to_complete": 1,
    "components": {
        "frame": {
            "quantity": 1,
            "time_to_complete": 3,
        },
        # "wheel": {
        #     "quantity": 2,
        #     "time_to_complete": 1,
        #     "components": {
        #         "rim": {
        #             "quantity": 1,
        #             "time_to_complete": 1
        #         },
        #         "tire": {
        #             "quantity": 1,
        #             "time_to_complete": 1
        #         }
        #     }
        # }
    }
}

def extract_components(structure, components=[], parent_time=0):
    if 'components' in structure:
        for component, sub_structure in structure['components'].items():
            time_to_complete = sub_structure.get('time_to_complete', 0) + parent_time
            components.append({
                'Component': component.capitalize(),
                'quantity': sub_structure['quantity'],
                'time_to_complete': time_to_complete
            })
            if 'components' in sub_structure:
                components = extract_components(sub_structure, components, time_to_complete)
    return components

def calculate_mps(starting_quantity, demand_production):
    schedule = []
    current_quantity = starting_quantity

    for index, row in demand_production.iterrows():
        current_quantity = current_quantity - row['Demand'] + row['Production']
        schedule.append((row['Week'], row['Demand'], row['Production'], current_quantity))

    return pd.DataFrame(schedule, columns=['Week', 'Demand', 'Production', 'Available'])

def generate_mrp_table(component, num_weeks, production_batch_size, starting_quantity, mps_schedule, parent_time_to_complete):
    mrp_table = pd.DataFrame({
        'Week': range(num_weeks),
        'Gross Requirement': [0]*num_weeks,
        'Scheduled Receipts': [0]*num_weeks,
        'Forecasted On Hand': [0]*num_weeks,
        'Net Requirement': [0]*num_weeks,
        'Planned Order Receipts': [0]*num_weeks,
        'Planned Order Releases': [0]*num_weeks
    })

    current_stock = starting_quantity
    mrp_table.at[0, 'Forecasted On Hand'] = current_stock

    for week in range(num_weeks):
        if week + component['time_to_complete'] < num_weeks:
            mrp_table.at[week, 'Gross Requirement'] = mps_schedule.at[week + parent_time_to_complete, 'Production'] * component['quantity']

        if week > 0:
            this_week_gross_req = mrp_table.at[week, 'Gross Requirement']
            previous_week_on_hand = mrp_table.at[week - 1, 'Forecasted On Hand']

            net_requirement_current = previous_week_on_hand - this_week_gross_req
            
            if net_requirement_current < 0:
                if this_week_gross_req > 0:
                    mrp_table.at[week, 'Net Requirement'] = net_requirement_current*-1
                batches_needed = (mrp_table.at[week, 'Net Requirement'] + production_batch_size - 1) // production_batch_size
                planned_order_quantity = batches_needed * production_batch_size
                mrp_table.at[week, 'Planned Order Releases'] = planned_order_quantity
                mrp_table.at[week - component['time_to_complete'], 'Planned Order Receipts'] = planned_order_quantity
            
            mrp_table.at[week, 'Forecasted On Hand'] = previous_week_on_hand - this_week_gross_req + mrp_table.at[week, 'Planned Order Releases']

    return mrp_table

def main():
    # Initialize demand and production data from the document
    demand_production = pd.DataFrame({
        'Week': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Demand': [0, 0, 0, 0, 20, 0, 40, 0, 0, 0],
        'Production': [0, 0, 0, 0, 28, 0, 30, 0, 0, 0]
    })
    starting_quantity_prod = 2

    mps_schedule = calculate_mps(starting_quantity_prod, demand_production)

    components = extract_components(product_structure)

    print("\nMaster Production Schedule:")
    print(mps_schedule)

    # For each component, generate MRP table
    for component in components:
        print(f"\nMRP for {component['Component']}:")
        production_batch_size = 40
        starting_quantity = 22

        mrp_table = generate_mrp_table(component, len(demand_production), production_batch_size, starting_quantity, mps_schedule, 1)
        print(mrp_table)

if __name__ == "__main__":
    main()