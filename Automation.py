import subprocess
import os

# Folders where simulation will be run
sim = ["Sim8"]

# Base paths of folders - Change according to projects
PROJECTS_PATH = os.path.expanduser("~/data/PROJECTS/Gepangghat/DEM")
GISDBASE = os.path.expanduser("~/data/SPATIALDATA")
LOCATION_NAME = "Gepangghat"

# Mapset location
PERMANENT_MAPSET = os.path.join(GISDBASE, LOCATION_NAME, "PERMANENT")

# Filter folders that are selected
available_dirs = [
    d for d in os.listdir(PROJECTS_PATH)
    if os.path.isdir(os.path.join(PROJECTS_PATH, d)) and d in sim
]

for i, folder in enumerate(available_dirs):
    mapset_name = f"Mapset_{folder}"
    sim_folder = os.path.join(PROJECTS_PATH, folder)
    subprocess.run([
        "grass",
        os.path.join(GISDBASE, LOCATION_NAME, "PERMANENT"),
        "--exec", "g.mapset", "-c", f"mapset={mapset_name}"
    ], check=True)
    
    shell_script = os.path.join(sim_folder, "start.sh")
    grass_cmd = f"sh {shell_script} {mapset_name}"

    subprocess.Popen([
        "gnome-terminal", "--", "bash", "-c",
        f'grass {os.path.join(GISDBASE, LOCATION_NAME, mapset_name)} --exec {grass_cmd}; exec bash'
    ], cwd=sim_folder)

print("Selected simulations submitted.")
