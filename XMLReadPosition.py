import xml.etree.ElementTree as ET
from datetime import datetime

from Model import Player, Match,PlayerMatch, Position
from DatabaseService import add, get_session

session = get_session()
tree = ET.parse('DFL_04_03_positions_raw_observed_DFL-COM-000001_DFL-MAT-J03WN1.xml')
root = tree.getroot()

metadata = root.find(".//MetaData")
match_id = metadata.attrib.get("MatchId")
match = session.query(Match).filter_by(match_id=match_id).first()

for frameset in root.findall(".//FrameSet"):
    if frameset.attrib.get("TeamId") == "referee" or frameset.attrib.get("TeamId") == "BALL":
        continue
    person_id = frameset.attrib.get("PersonId")
    player = session.query(Player).filter_by(person_id=person_id).first()
    print(f"Processing player: {player.first_name} {player.last_name} (PersonId: {person_id})")
    player_match = session.query(PlayerMatch).filter_by(player_id=player.id, match_id=match.id).first()
    for frame in frameset.findall("Frame"):
        position = Position(
            player_match_id=player_match.id,
            x=frame.attrib.get("X"),
            y=frame.attrib.get("Y"),
            frame_number=frame.attrib.get("N"),
            timestamp=datetime.fromisoformat(frame.attrib.get("T"))
        )
        add(position)

# import xml.etree.ElementTree as ET
# from datetime import datetime
# from collections import defaultdict

# from Model import Player, Match, PlayerMatch, Position
# from DatabaseService import get_session

# session = get_session()

# tree = ET.parse('DFL_04_03_positions_raw_observed_DFL-COM-000001_DFL-MAT-J03WN1.xml')
# root = tree.getroot()

# # Cache match
# metadata = root.find(".//MetaData")
# match_id = metadata.attrib.get("MatchId")
# match = session.query(Match).filter_by(match_id=match_id).first()

# # Cache all players and player_matches in advance
# players = {p.person_id: p.id for p in session.query(Player).all()}
# player_matches = {
#     (pm.player_id, pm.match_id): pm.id
#     for pm in session.query(PlayerMatch).filter_by(match_id=match.id)
# }

# # Start collecting positions
# positions = []

# for frameset in root.findall(".//FrameSet"):
#     if frameset.attrib.get("TeamId") in ["referee", "BALL"]:
#         continue

#     person_id = frameset.attrib.get("PersonId")
#     player_id = players.get(person_id)
#     if not player_id:
#         continue

#     player_match_id = player_matches.get((player_id, match.id))
#     if not player_match_id:
#         continue

#     for frame in frameset.findall("Frame"):
#         try:
#             positions.append(Position(
#                 player_match_id=player_match_id,
#                 x=float(frame.attrib.get("X")),
#                 y=float(frame.attrib.get("Y")),
#                 frame_number=int(frame.attrib.get("N")),
#                 timestamp=datetime.fromisoformat(frame.attrib.get("T"))
#             ))
#         except Exception as e:
#             print(f"Error parsing frame: {e}")

# # Bulk insert all at once
# print(f"Inserting {len(positions)} positions...")
# session.bulk_save_objects(positions)
# session.commit()
# print("Done.")

# import xml.etree.ElementTree as ET
# from datetime import datetime
# import mysql.connector  # raw MySQL connection

# # --- DB CONFIG (replace with your values)
# conn = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='my-secret-pw',
#     database='footballplayers_analysis',
#     autocommit=False
# )
# cursor = conn.cursor()

# # --- Load and parse XML
# tree = ET.parse('DFL_04_03_positions_raw_observed_DFL-COM-000001_DFL-MAT-J03WN1.xml')
# root = tree.getroot()

# # --- Get MatchId
# metadata = root.find(".//MetaData")
# match_id = metadata.attrib.get("MatchId")
# cursor.execute("SELECT id FROM matches WHERE match_id = %s", (match_id,))
# match_row = cursor.fetchone()
# if not match_row:
#     print("Match not found!")
#     exit(1)
# match_db_id = match_row[0]

# # --- Load Players and PlayerMatches into memory
# cursor.execute("SELECT person_id, id FROM players")
# players = dict(cursor.fetchall())

# cursor.execute("SELECT id, player_id FROM player_matches WHERE match_id = %s", (match_db_id,))
# player_matches_raw = cursor.fetchall()
# player_matches = {players[p_id]: pm_id for pm_id, p_id in player_matches_raw if p_id in players}

# # --- Build batch of rows
# positions_batch = []

# for frameset in root.findall(".//FrameSet"):
#     team_id = frameset.attrib.get("TeamId")
#     if team_id in ["referee", "BALL"]:
#         continue

#     person_id = frameset.attrib.get("PersonId")
#     player_id = players.get(person_id)
#     # if not player_id:
#     #     continue

#     player_match_id = player_matches.get(player_id)
#     # if not player_match_id:
#     #     continue

#     for frame in frameset.findall("Frame"):
#         try:
#             x = float(frame.attrib["X"])
#             y = float(frame.attrib["Y"])
#             frame_number = int(frame.attrib["N"])
#             timestamp = datetime.fromisoformat(frame.attrib["T"])

#             positions_batch.append((player_match_id, x, y, frame_number, timestamp))
#         except Exception as e:
#             print(f"Frame parse error: {e}")

# # --- Bulk insert using executemany
# print(f"Inserting {len(positions_batch)} positions...")

# insert_sql = """
#     INSERT INTO positions (player_match_id, x, y, frame_number, timestamp)
#     VALUES (%s, %s, %s, %s, %s)
# """

# cursor.executemany(insert_sql, positions_batch)
# conn.commit()
# print("Done.")
# cursor.close()
# conn.close()

