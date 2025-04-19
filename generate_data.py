import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

# Parameters
departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
roles_per_dept = 3
months = pd.date_range(start='2024-01-01', periods=12, freq='MS')
records = []

for dept in departments:
    for role_id in range(roles_per_dept):
        role = f"{dept} Role {role_id+1}"
        for month in months:
            openings = random.randint(1, 5)
            applicants = random.randint(20, 100)
            interviews = int(applicants * random.uniform(0.3, 0.7))
            offers = int(interviews * random.uniform(0.4, 0.8))
            hires = int(offers * random.uniform(0.6, 1.0))
            avg_time_to_fill = round(random.uniform(10, 45), 1)
            offer_accept_rate = round((hires / offers), 2) if offers > 0 else 0

            records.append({
                'Department': dept,
                'Role': role,
                'Month': month.strftime('%Y-%m'),
                'Openings': openings,
                'Applicants': applicants,
                'Interviews': interviews,
                'Offers': offers,
                'Hires': hires,
                'Avg Time to Fill (days)': avg_time_to_fill,
                'Offer Acceptance Rate': offer_accept_rate
            })

# Create and export
df = pd.DataFrame(records)
df.to_csv('staffing_data.csv', index=False)
print("✅ staffing_data.csv created.")
