import gpxpy
import pandas as pd
from geopy.distance import geodesic

def read_gpx(file_path):
    """
    Lee un archivo GPX y devuelve un DataFrame con:
    time, lat, lon, elevation, distance_m, pace_min_km
    """

    with open(file_path, "r", encoding="utf-8") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = []
    prev_point = None
    total_distance = 0.0  # metros

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:

                if prev_point is not None:
                    dist = geodesic(
                        (prev_point.latitude, prev_point.longitude),
                        (point.latitude, point.longitude)
                    ).meters
                else:
                    dist = 0.0

                total_distance += dist

                data.append({
                    "time": point.time,
                    "lat": round(point.latitude, 4),
                    "lon": round(point.longitude, 4),
                    "elevation": round(point.elevation, 2),
                    "delta_distance_km": round(dist / 1000, 4),
                    "distance_km": round(total_distance / 1000, 4)
                })

                prev_point = point

    df = pd.DataFrame(data)

    # ---- cálculo de velocidad y pace ----
    df["speed_km_h"] = round(df["delta_distance_km"] / (df["time"].diff().dt.total_seconds() / 3600), 2)

    # pace en min/km
    df["pace_min_km"] = round(df["speed_km_h"] ** -1 * 60, 2)

    # correcciones de valores atipicos (velocidades = {4:14 min/km a 6:01 min/km})
    df.loc[df["speed_km_h"] == 0.00, "pace_min_km"] = pd.NA
    df.loc[df["pace_min_km"] > 6.01, "pace_min_km"] = pd.NA
    df.loc[df["pace_min_km"] < 4.14, "pace_min_km"] = pd.NA

    return df
