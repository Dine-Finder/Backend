import numpy as np
import pandas as pd

manhattan_bbox = {
    'min_lat': 40.700292,
    'max_lat': 40.882214,
    'min_lon': -74.019442,
    'max_lon': -73.907004
}

lat_degree_in_meters = 111320
lon_degree_in_meters = 40075000 * np.cos(np.radians(40.7831)) / 360

cell_size_meters = 500

num_cells_lat = int((manhattan_bbox['max_lat'] - manhattan_bbox['min_lat']) * lat_degree_in_meters / cell_size_meters)
num_cells_lon = int((manhattan_bbox['max_lon'] - manhattan_bbox['min_lon']) * lon_degree_in_meters / cell_size_meters)

lat_centers = np.linspace(manhattan_bbox['min_lat'], manhattan_bbox['max_lat'], num_cells_lat)
lon_centers = np.linspace(manhattan_bbox['min_lon'], manhattan_bbox['max_lon'], num_cells_lon)

coordinates = []

for lat in lat_centers:
    for lon in lon_centers:
        coordinates.append({
            'latitude': lat,
            'longitude': lon
        })
coordinates_df = pd.DataFrame(coordinates)

csv_file_path = 'manhattan_grid_coordinates.csv'
coordinates_df.to_csv(csv_file_path, index=False)

print(f"Grid coordinates have been successfully saved to {csv_file_path}")
