import xml.etree.ElementTree as ET
from Model import Player, Match, PlayerMatch;
from DatabaseService import add;

tree = ET.parse('DFL_02_01_matchinformation_DFL-COM-000001_DFL-MAT-J03WN1.xml')
root = tree.getroot()

# Result list
players = []
player_matchs = []

general = root.find(".//General")

match = Match(name=general.attrib.get("MatchTitle"), match_id=general.attrib.get("MatchId"))

# Traverse teams
for team in root.findall(".//Team"):
    team_name = team.attrib.get("TeamName")
    team_role = team.attrib.get("Role")

    for player in team.find("Players").findall("Player"):
        player_data = Player(
            first_name=player.attrib.get("FirstName"),
            last_name=player.attrib.get("LastName"),
            person_id=player.attrib.get("PersonId"),
            shirt_number=player.attrib.get("ShirtNumber"),
            team=team_name
        )

        player_match = PlayerMatch(player=player_data, match=match)
        players.append(player_data)
        player_matchs.append(player_match)
        add(player_data)
        add(player_match)

