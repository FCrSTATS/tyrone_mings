
import numpy as np
import pandas as pd
from .tools import *


def get_time(bgPosCols, bgPosRows, extra_mins):
    mat = np.zeros((13,10))
    for r in range (12):
        for c in range (1, 11):
            mat[r,c-1] = (r * 10) + c

    return(int(mat[int((bgPosRows / -36)) , int((bgPosCols / -36))]) + extra_mins)


def convert_time(time_raw):

    if 'PM' in time_raw:
        hour, mins = map(int, time_raw.replace(" PM", "").strip().split(":"))
        converted_time = str(hour + 12) + ":" + str(mins)
    else:
        converted_time = time_raw.replace(" AM", "").strip()

    return(converted_time)

def get_match_info(match_soup, match_url):
    match_id = match_url.rsplit('/', 1)[1]

    competition = match_soup.select("div.spielername-profil")[0].select("h2")[0].get_text().strip()
    competition_id = match_soup.select("div.spielername-profil")[0].select('a')[0]['href'].split("/")[4]


    home_team = match_soup.select("div.sb-team.sb-heim.show-for-small")[0].select('img')[0]['alt'].lower()
    home_team_id = match_soup.select("div.sb-team.sb-heim.show-for-small")[0].select('a')[0]['href'].split("/verein/")[1].split("/")[0]
    try:
        home_league_position = int(match_soup.select("div.sb-team.sb-heim.show-for-small")[0].select('p')[0].get_text().replace("Position:", "").strip())
    except:
        home_league_position = None

    away_team = match_soup.select("div.sb-team.sb-gast.show-for-small")[0].select('img')[0]['alt'].lower()
    away_team_id = match_soup.select("div.sb-team.sb-gast.show-for-small")[0].select('a')[0]['href'].split("/verein/")[1].split("/")[0]
    try:
        away_league_position = int(match_soup.select("div.sb-team.sb-gast.show-for-small")[0].select('p')[0].get_text().replace("Position:", "").strip())
    except:
        away_league_position = None

    core_info = match_soup.select("div.sb-spieldaten")[0]


    stadium = core_info.select('p.sb-zusatzinfos')[0].select('a')[0].get_text()

    # print(core_info.select('p.sb-zusatzinfos')[0].get_text())
    if "Behind Closed Doors" in core_info.select('p.sb-zusatzinfos')[0].get_text():
        attendance = 0
    else:
        attendance = int(core_info.select('p.sb-zusatzinfos')[0].select('strong')[0].get_text().replace("Attendance: ", "").strip().replace(".", ""))

    try:
        match_date_raw = core_info.select('p.sb-datum.hide-for-small')[0].select('a')[1].get_text().strip()[5:]
    except:
        match_date_raw = 'asdsad'

    try:
        match_day = int(core_info.select('p.sb-datum.hide-for-small')[0].select('a')[0].get_text().replace(". Matchday", ""))
    except:
        match_day = None

    home_goals, away_goals = map(int, core_info.select('div.ergebnis-wrap')[0].get_text().strip().split("(")[0].split(":"))

    home_ht_goals, away_ht_goals = map(int, core_info.select('div.ergebnis-wrap')[0].get_text().strip().split("(")[1].replace(")", "").split(":"))
    time_of_match = convert_time(core_info.select('p.sb-datum.hide-for-small')[0].get_text().strip().rsplit('|', 1)[1].strip())

    home_formation = match_soup.select('div.large-7.aufstellung-vereinsseite.columns.small-12.unterueberschrift.aufstellung-unterueberschrift')[0].get_text().replace('Starting Line-up: ', '').strip()
    away_formation = match_soup.select('div.large-7.aufstellung-vereinsseite.columns.small-12.unterueberschrift.aufstellung-unterueberschrift')[1].get_text().replace('Starting Line-up: ', '').strip()

    ## game bio
    match_info = dict(
            {'match_url': match_url,
            'match_id': match_id,
            'competition': competition,
            'competition_id': competition_id,
            'home_team': home_team,
            'home_team_id': home_team_id,
            'away_team': away_team,
            'away_team_id': away_team_id,
            'home_league_position': home_league_position,
            'away_league_position': away_league_position,
            'stadium': stadium,
            'attendance': attendance,
            'time_of_match': time_of_match,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'home_ht_goals': home_ht_goals,
            'away_ht_goals': away_ht_goals,
            'home_formation': home_formation,
            'away_formation': away_formation
            })

    if match_info['home_goals'] > match_info['away_goals']:
        match_info['result'] = "home_win"
    elif match_info['home_goals'] < match_info['away_goals']:
        match_info['result'] = "away_win"
    else:
        match_info['result'] = "draw"

    # match_info = pd.DataFrame.from_dict(match_info, orient = "index").transpose()
    return(match_info)

def get_match_data(match_soup, match_info, match_url):

    output_dict = {}

    ### GET Goals
    home_score_before_goal_list = []
    away_score_before_goal_list = []
    game_state_list = []
    player_id_list = []
    player_name_list = []
    scoring_team_list = []
    player_id_list = []
    player_name_list = []
    shot_type_list = []
    shot_foot_list = []
    minute_list = []
    assisting_player_name_list = []
    assisting_player_id_list = []
    assist_type_list = []

    if match_soup.find("div", {"id": "sb-tore"}) != None:
        for li in match_soup.find("div", {"id": "sb-tore"}).select('li'):

            ## name and ID
            player_id_list.append(li.select('div.sb-aktion-aktion')[0].select('a')[0]['id'])
            player_name_list.append(li.select('div.sb-aktion-aktion')[0].select('a')[0]['title'])

            ## check which is the scoring team
            scoring_team = "home" if li['class'][0] == "sb-aktion-heim" else "away"
            scoring_team_list.append(scoring_team)

            ## calculate pre-goal score and game state
            home_score, away_score = map(int, li.select("div.sb-aktion-spielstand")[0].get_text().strip().split(":"))

            if scoring_team == "home":
                home_score_before_goal = home_score - 1
                away_score_before_goal = away_score
                game_state_list.append(home_score_before_goal - away_score_before_goal)
                home_score_before_goal_list.append(home_score_before_goal)
                away_score_before_goal_list.append(away_score_before_goal)
            else:
                home_score_before_goal = home_score
                away_score_before_goal = away_score - 1
                game_state_list.append(away_score_before_goal - home_score_before_goal)
                home_score_before_goal_list.append(home_score_before_goal)
                away_score_before_goal_list.append(away_score_before_goal)

            for item in li.select('div.sb-aktion-aktion'):
                if len(item.get_text().split("Assist: ")) == 2:
                    assist_raw = item.get_text().split("Assist: ")[1].strip()
                    assisting_player_name_list.append(li.select('a.wichtig')[1]['title'])
                    assisting_player_id_list.append(li.select('a.wichtig')[1]['id'])

                    ### TODO
                    # 1. find other edge cases for shot_foot
                    # 2. deal with own goals (WC final), to better represent the assist info
                    # 3. deal with penalties (WC final), to better represent the assist info

                    if "," in assist_raw:
                        assist_type_list.append(assist_raw.split(",")[1].lower().strip())
                    elif 'Handball by' in assist_raw:
                        assist_type_list.append("handball")
                else:
                    assisting_player_name_list.append(None)
                    assisting_player_id_list.append(None)
                    assist_type_list.append(None)

            ## get minutes
            bgPosCols, bgPosRows = map(int, li.select('span.sb-sprite-uhr-klein')[0]['style'].replace("background-position: ", "").replace(";", "").replace("px", "").split(" "))
            extra_mins = 0 if li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip() == "" else int(li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip())
            minute_list.append(get_time(bgPosCols, bgPosRows, extra_mins))


            ## get shot info
            goal_text = li.select('div.sb-aktion-aktion')[0].get_text()
            if len(goal_text.split(",")) < 3:
                shot_type_list.append(None)
            else:
                shot_type = li.select('div.sb-aktion-aktion')[0].get_text().split(",")[1].strip()
                if shot_type == "Header":
                    shot_type_list.append("header")
                    shot_foot_list.append(None)
                else:
                    shot_foot_list.append(shot_type.split("-")[0].lower())
                    shot_type_list.append("foot")

    goals_data = pd.DataFrame(
            {'home_score_before_goal': home_score_before_goal_list,
            'away_score_before_goal': away_score_before_goal_list,
            'game_state': game_state_list,
            'player_id': player_id_list,
            'player_name': player_name_list,
            'scoring_team': scoring_team_list,
            'player_id': player_id_list,
            'player_name': player_name_list,
            'shot_type': shot_type_list,
            'shot_foot': shot_foot_list,
            'minute': minute_list,
            'assisting_player_name': assisting_player_name_list,
            'assisting_player_id': assisting_player_id_list,
            'assist_type': assist_type_list
            })

            # TODO add the right team and id for the scoring team
    goals_data['team_name'] = match_info['home_team']
    goals_data['team_id'] = match_info['away_team']

    goals_data['match_id'] = match_info['match_id']

    output_dict['goals_data'] = goals_data

    player_name_list = []
    player_id_list = []
    team_list = []
    sub_type_list = []
    sub_reason_list = []
    minute_list = []
    other_sub_name_list = []
    other_sub_id_list = []

    if match_soup.find("div", {"id": "sb-wechsel"}) != None:
        for li in match_soup.find("div", {"id": "sb-wechsel"}).select('li'):

            subbing_team = match_info['home_team'] if li['class'][0] == "sb-aktion-heim" else match_info['away_team']

            try:
                sub_reason = li.select('div.sb-aktion-spielstand.hide-for-small')[0].select('span')[0]['title'].lower()
            except:
                sub_reason = None

            bgPosCols, bgPosRows = map(int, li.select('span.sb-sprite-uhr-klein')[0]['style'].replace("background-position: ", "").replace(";", "").replace("px", "").split(" "))
            extra_mins = 0 if li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip() == "" else int(li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip())
            sub_min = get_time(bgPosCols, bgPosRows, extra_mins)

            player_name = li.select('div.sb-aktion-spielerbild')[0].select('img')[0]['alt'].lower()
            player_id = li.select('div.sb-aktion-spielerbild')[0].select('a')[0]['id'].lower()

            player_name_in = li.select('div.sb-aktion-spielerbild')[1].select('img')[0]['alt'].lower()
            player_id_in = li.select('div.sb-aktion-spielerbild')[1].select('a')[0]['id'].lower()

            # player on
            player_name_list.append(player_name)
            player_id_list.append(player_id)
            team_list.append(subbing_team)
            sub_type_list.append('out')
            sub_reason_list.append(sub_reason)
            minute_list.append(sub_min)
            other_sub_name_list.append(player_name_in)
            other_sub_id_list.append(player_id_in)

            # player off
            player_name_list.append(player_name_in)
            player_id_list.append(player_id_in)
            team_list.append(subbing_team)
            sub_type_list.append('in')
            sub_reason_list.append(sub_reason)
            minute_list.append(sub_min)
            other_sub_name_list.append(player_name)
            other_sub_id_list.append(player_id)

    subs_data = pd.DataFrame(
            {'player_name': player_name_list,
            'player_id': player_id_list,
            'team': team_list,
            'sub_type': sub_type_list,
            'sub_reason': sub_reason_list,
            'minute': minute_list,
            'other_sub_name': other_sub_name_list,
            'other_sub_id': other_sub_id_list
            })

    subs_data['match_id'] = match_info['match_id']

    output_dict['subs_data'] = subs_data

    player_name_list = []
    player_id_list = []
    team_list = []
    card_type_list = []
    card_reason_list = []
    minute_list = []

    if match_soup.find("div", {"id": "sb-karten"}) != None:
        for li in match_soup.find("div", {"id": "sb-karten"}).select('li'):

            team_list.append(match_info['home_team'] if li['class'][0] == "sb-aktion-heim" else match_info['away_team'])

            bgPosCols, bgPosRows = map(int, li.select('span.sb-sprite-uhr-klein')[0]['style'].replace("background-position: ", "").replace(";", "").replace("px", "").split(" "))
            extra_mins = 0 if li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip() == "" else int(li.select('span.sb-sprite-uhr-klein')[0].get_text().replace("+", "").strip())
            minute_list.append(get_time(bgPosCols, bgPosRows, extra_mins))

            player_name_list.append(li.select('div.sb-aktion-spielerbild')[0].select('img')[0]['alt'].lower())
            player_id_list.append(li.select('div.sb-aktion-spielerbild')[0].select('a')[0]['id'].lower())

            if "Yellow card" in li.select('div.sb-aktion-aktion')[0].get_text().strip():
                card_type_list.append("yellow")
            elif "Second yellow" in li.select('div.sb-aktion-aktion')[0].get_text().strip():
                card_type_list.append("second yellow")
            else:
                card_type_list.append("red card")

            if "," in li.select('div.sb-aktion-aktion')[0].get_text().strip():
                card_reason_list.append(li.select('div.sb-aktion-aktion')[0].get_text().strip().split(",")[1].strip().lower())
            else:
                card_reason_list.append(None)

    card_data = pd.DataFrame(
            {'player_name': player_name_list,
            'player_id': player_id_list,
            'team': team_list,
            'card_type': card_type_list,
            'card_reason': card_reason_list,
            'minute': minute_list
            })

    card_data['match_id'] = match_info['match_id']


    output_dict['card_data'] = card_data

    lineup_soup = get_souped_page(match_url.replace("index", "aufstellung"))

    player_name_list = []
    player_id_list = []
    squad_number_list = []
    age_list = []
    started_list = []
    team_list = []
    position_list = []

    # home team - starters
    for row in lineup_soup.select('table.items')[0].select('tr')[0::3]:
        player_name_list.append(row.select('img')[0]['alt'].lower())
        player_id_list.append(row.select('a')[0]['id'].lower())
        squad_number_list.append(row.select('div.rn_nummer')[0].get_text())
        age_list.append(int(row.get_text().strip().split("(")[1].strip().split(" years old")[0]))
        started_list.append(1)
        team_list.append(match_info['home_team'])
        position_list.append(row.get_text().strip().split(")")[1].split(",")[0].strip().lower())

    # away team - starters
    for row in lineup_soup.select('table.items')[1].select('tr')[0::3]:
        player_name_list.append(row.select('img')[0]['alt'].lower())
        player_id_list.append(row.select('a')[0]['id'].lower())
        squad_number_list.append(row.select('div.rn_nummer')[0].get_text())
        age_list.append(int(row.get_text().strip().split("(")[1].strip().split(" years old")[0]))
        started_list.append(1)
        team_list.append(match_info['away_team'])
        position_list.append(row.get_text().strip().split(")")[1].split(",")[0].strip().lower())

    # home team - subs
    for row in lineup_soup.select('table.items')[2].select('tr')[0::3]:
        player_name_list.append(row.select('img')[0]['alt'].lower())
        player_id_list.append(row.select('a')[0]['id'].lower())
        squad_number_list.append(row.select('div.rn_nummer')[0].get_text())
        age_list.append(int(row.get_text().strip().split("(")[1].strip().split(" years old")[0]))
        started_list.append(0)
        team_list.append(match_info['home_team'])
        position_list.append(row.get_text().strip().split(")")[1].split(",")[0].strip().lower())

    # away team - subs
    for row in lineup_soup.select('table.items')[3].select('tr')[0::3]:
        player_name_list.append(row.select('img')[0]['alt'].lower())
        player_id_list.append(row.select('a')[0]['id'].lower())
        squad_number_list.append(row.select('div.rn_nummer')[0].get_text())
        age_list.append(int(row.get_text().strip().split("(")[1].strip().split(" years old")[0]))
        started_list.append(0)
        team_list.append(match_info['away_team'])
        position_list.append(row.get_text().strip().split(")")[1].split(",")[0].strip().lower())


    lineup_data = pd.DataFrame(
            {'player_name': player_name_list,
            'player_id': player_id_list,
            'team': team_list,
            'squad_number': squad_number_list,
            'age': age_list,
            'started': started_list,
            'position': position_list
            })

    mins_played_list = []
    subbed_off_list = []
    subbed_on_list = []

    # find max minutes
    max_minutes = max(goals_data.minute.max(), card_data.minute.max(), subs_data.minute.max()) + 1


    for i in range(len(lineup_data)):
        row = lineup_data.iloc[i]
        if row.started == 1:
            if row.player_name in list(subs_data[subs_data['sub_type'] == "out"]['player_name']):
                mins_played_list.append(int(subs_data[subs_data['player_name'] == row.player_name]['minute']))
                subbed_off_list.append(1)
                subbed_on_list.append(0)
            else:
                mins_played_list.append(max_minutes)
                subbed_off_list.append(0)
                subbed_on_list.append(0)
        else:
            if row.player_name in list(subs_data[subs_data['sub_type'] == "in"]['player_name']):
                mins_played_list.append(max_minutes - int(subs_data[subs_data['player_name'] == row.player_name]['minute']))
                subbed_off_list.append(0)
                subbed_on_list.append(1)
                ### TODO add subbed on then off edge case
            else:
                mins_played_list.append(0)
                subbed_off_list.append(0)
                subbed_on_list.append(0)

    lineup_data['mins_played'] = mins_played_list
    lineup_data['subbed_off'] = subbed_off_list
    lineup_data['subbed_on'] = subbed_on_list
    lineup_data['match_id'] = match_url.rsplit('/', 1)[1]
    lineup_data['competition_id'] = match_info['competition_id']
    lineup_data['competition'] = match_info['competition']

    output_dict['lineup_data'] = lineup_data

    return(output_dict)

def match_pull(match_url,
               data_folder = '',
               info = False,
               lineups = False,
               goals = False,
               cards = False,
               subs = False,
               output = "pandas"):

    match_soup = get_souped_page(match_url)
    match_info = get_match_info(match_soup, match_url)
    match_data = get_match_data(match_soup, match_info, match_url)

    # print()
    final_output_dict = {}

    if lineups:
        # pandas output
        if output == "pandas":
            final_output_dict['lineup_data'] = match_data['lineup_data']
        # csv output
        elif output == "csv":
            pd.DataFrame.from_dict(match_data['lineup_data']).to_csv((data_folder + str(match_info['match_id']) + '_lineups.csv'), index = False)

    if goals:
        # pandas output
        if output == "pandas":
            final_output_dict['goals_data'] = match_data['goals_data']
        # csv output
        elif output == "csv":
            pd.DataFrame.from_dict(match_data['goals_data']).to_csv((data_folder + str(match_info['match_id']) + '_goals.csv'), index = False)

    if cards:
        # pandas output
        if output == "pandas":
            final_output_dict['card_data'] = match_data['card_data']
        # csv output
        elif output == "csv":
            pd.DataFrame.from_dict(match_data['card_data']).to_csv((data_folder + str(match_info['match_id']) + '_cards.csv'), index = False)

    if subs:
        # pandas output
        if output == "pandas":
            final_output_dict['subs_data'] = match_data['subs_data']
        # csv output
        elif output == "csv":
            pd.DataFrame.from_dict(match_data['subs_data']).to_csv((data_folder + str(match_info['match_id']) + '_subs.csv'), index = False)

    if info:
        # pandas output
        if output == "pandas":
            final_output_dict['match_data'] = match_info
        # csv output
        elif output == "csv":
            pd.DataFrame.from_dict(match_info, orient='index').transpose().to_csv((data_folder + str(match_info['match_id']) + '_info.csv'), index = False)

    return(final_output_dict)
