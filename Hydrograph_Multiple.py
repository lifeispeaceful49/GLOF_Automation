import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def process_lake(lake_name, area_m2, output_directory, fraction=0.8, breach_width=50):
    lake_output_path = os.path.join(output_directory, lake_name)
    os.makedirs(lake_output_path, exist_ok=True)
    print(f"\nProcessing Lake: {lake_name} (Area: {area_m2:.2f} $m^2$)")

    A = area_m2

    V=[0.035*(A**1.5),
    0.104*(A**1.42),
    0.0354*(A**1.3742),
    A*(0.087*(A**0.434)),
    A*(55*((A*1e-6)**0.25)),
    0.2933*(A**1.3324),
    0.054393*(A**1.483009),
    A*(0.1217*(A**0.4129)),
    A*0.5057*(A**0.2884),
    A*0.1746*(A**0.3725),
    A*0.3211*(A**0.324),
    A*0.1697*(A**0.3778),
    0.036*(A**1.49),
    42.95*((A*1e-6)**1.408) * (10**6)
    ]

    V_est = pd.DataFrame()
    V_est["Volume"] = V
    V_est["Volume"] *= fraction

    # Mean depth of lake
    V_est["Mean Depth"] = V_est["Volume"] / A

    # Time of Breach
    breach_depth = V_est['Mean Depth'].median()
    # breach_width is passed as an argument

    time_of_breach=[
     0.011*breach_width,
     0.015*breach_depth,
     0.02*breach_depth+0.25,
     breach_width/(4*breach_depth),
     breach_width/(4*breach_depth+61),
     0.00254*((V_est['Volume'].median())**0.53)*(breach_depth**-0.9)
    ]
    T_est = pd.DataFrame()
    T_est["Time"] = time_of_breach

    # Peak discharge of GLOF estimation using different empirical equations
    volume_release = V_est['Volume'].median()
    peak_discharge=[
    1.268*(breach_depth+0.3)**2.5,
    (8/27)*(9.8**0.5)*(breach_depth**1.5)*breach_width,
    16.6*breach_depth**1.85,
    0.54*breach_width,
    19.1*breach_depth**1.85,
    13.4*breach_depth**1.89,
    1.776*volume_release**0.47,
    1.122*volume_release**0.57,
    0.981*(volume_release*breach_depth)**0.42,
    2.634*(volume_release*breach_depth)**0.44,
    44*breach_depth**1.63,
    325*(breach_depth*volume_release*1e-6)**0.44,
    0.72*volume_release**0.53,
    1.154*(breach_depth*volume_release)**0.412,
    3.85*(breach_depth*volume_release)**0.411,
    0.607*(breach_depth**1.24*volume_release**0.295)
    ]
    Q_est = pd.DataFrame()
    Q_est['Q'] = peak_discharge

    # Plotting the model hydrograph
    t = np.arange(0, 10000, 0.1) # Time in seconds
    Q_max = Q_est['Q'].median()

    # Calculate 'a' such that the total volume matches volume_release
    a = volume_release / (Q_max * np.e)

    Q = (volume_release / a**2) * t * np.exp(-t / a) # Discharge equation

    hydrograph = pd.DataFrame()
    hydrograph['T'] = t
    hydrograph['Q'] = Q
    hydrograph['V'] = Q / (breach_width * breach_depth)
    hydrograph.loc[len(hydrograph) - 1, ("Q", "V")] = 0

    # Visualising the hydrograph
    plt.figure(figsize=(12, 6))
    plt.plot(hydrograph['T'], hydrograph['Q'])
    plt.title(f"Lake {lake_name} - Model Hydrograph (Estimated Volume: {np.int64(volume_release)}, Peak Discharge: {np.int64(Q_max)})")
    plt.xlabel("Time (in seconds)")
    plt.ylabel("Discharge (in $m^3/s$)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(lake_output_path, f"{lake_name}_hydrograph.png"))
    plt.show()
    plt.close()

    hydro_filepath = os.path.join(lake_output_path, f"{lake_name}_hydro.txt")
    hydrograph.iloc[1:].to_csv(hydro_filepath, sep="\t", index=False)
    print(f"\nHydrograph data saved to {hydro_filepath}")
    print(f"Hydrograph plot saved to {lake_output_path}/{lake_name}_hydrograph.png")


if __name__ == "__main__":
    csv_filename = "lakes.csv"  #Put your csv file path here!
    print(f"File '{csv_filename}' loaded successfully")

    output_base_directory = "hydrograph_outputs"
    os.makedirs(output_base_directory, exist_ok=True)

    lakes_df = pd.read_csv(csv_filename)
    for index, row in lakes_df.iterrows():
        lake_name = row['Lake Name']
        area = row['Area (m^2)']
        process_lake(lake_name, area, output_base_directory)

    print("\nAll lakes processed")
