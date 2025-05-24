from Model import Player
from DatabaseService import get_session

import pandas as pd
import numpy as np

def compute_pressure(session, match_id: str, player_person_id: str, d_front=3.0, max_frames=100000):
    # Step 1: Get player info
    player = session.query(Player).filter_by(person_id=player_person_id).one()
    player_team = player.team

    # Step 2: Get all player positions
    player_pos_df = pd.read_sql_query(f"""
        SELECT p.frame_number, p.x as px, p.y as py
        FROM positions p
        JOIN player_matches pm ON p.player_match_id = pm.id
        WHERE pm.player_id = {player.id}
          AND pm.match_id = (SELECT id FROM matches WHERE match_id = '{match_id}')
        ORDER BY p.frame_number
        LIMIT {max_frames}
    """, session.bind)

    if player_pos_df.empty:
        return {"error": "No position data found for this player in match"}

    frame_numbers = player_pos_df['frame_number'].tolist()

    # Step 3: Get opponent positions in those frames
    opponent_pos_df = pd.read_sql_query(f"""
        SELECT p.frame_number, p.x as ox, p.y as oy
        FROM positions p
        JOIN player_matches pm ON p.player_match_id = pm.id
        JOIN players pl ON pm.player_id = pl.id
        WHERE pm.match_id = (SELECT id FROM matches WHERE match_id = '{match_id}')
          AND pl.team != '{player_team}'
          AND p.frame_number IN ({','.join(map(str, frame_numbers))})
    """, session.bind)

    # Step 4: Merge and compute distances
    merged = pd.merge(player_pos_df, opponent_pos_df, on="frame_number")

    # Calculate dx, dy, and distance
    merged['dx'] = merged['ox'] - merged['px']
    merged['dy'] = merged['oy'] - merged['py']
    merged['distance'] = np.hypot(merged['dx'], merged['dy'])

    # Step 5: Determine if opponent is in front and within d_front
    merged['is_pressure'] = (merged['dx'] >= 0) & (merged['distance'] <= d_front)

    # Step 6: For each frame, check if at least one pressure
    pressure_by_frame = merged.groupby('frame_number')['is_pressure'].any()

    # Step 7: Stats
    total_frames = len(player_pos_df)
    pressure_frames = pressure_by_frame.sum()
    pressure_percent = round((pressure_frames / total_frames) * 100, 2)

    return {
        "player": player.first_name + " " +player.last_name,
        "team": player.team,
        "total_frames": total_frames,
        "pressure_frames_count": int(pressure_frames),
        "pressure_percent": pressure_percent
    }

if __name__ == "__main__":
    session = get_session()
    match_id = "DFL-MAT-J03WN1"
    player_person_id = "DFL-OBJ-000172"  # Replace with actual person ID
    d_front = 3.0  # Distance in meters

    result = compute_pressure(session, match_id, player_person_id, d_front)
    print(result)

