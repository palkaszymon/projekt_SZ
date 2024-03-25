import pandas as pd

def calculate_mps(starting_quantity, demand_production):
    schedule = []
    current_quantity = starting_quantity

    for index, row in demand_production.iterrows():
        current_quantity = current_quantity - row['Demand'] + row['Production']
        schedule.append((row['Week'], row['Demand'], row['Production'], current_quantity))

    return pd.DataFrame(schedule, columns=['Week', 'Demand', 'Production', 'Available'])


def main():
    num_weeks = int(input("Enter the number of weeks: "))
    demand_production = pd.DataFrame(columns=['Week', 'Demand', 'Production'])
    for week in range(1, num_weeks + 1):
        demand_production = pd.concat([demand_production, pd.DataFrame({'Week': [week],
                                                                        'Demand': [int(input(f"Enter demand for week {week}: "))],
                                                                        'Production': [int(input(f"Enter production for week {week}: "))]})],
                                                                        ignore_index=True)

    starting_quantity = int(input("Enter starting quantity of goods: "))

    mps_schedule = calculate_mps(starting_quantity, demand_production)

    print("\nMaster Production Schedule:")
    print(mps_schedule.transpose())


if __name__ == "__main__":
    main()
