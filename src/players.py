
import pandas as pd
import re
import csv
import js2xml
import datetime
from .leaguesclubs import *
import warnings

def bio_player_pull(pageSoup, player_id):

############# ADD SECONDARY POSITION INFO #################### #TODO
    ## base info
    player_name = pageSoup.select('h1')[0].get_text().lower()

    DOB = None
    POB = None
    COB = None
    position = None
    age = None
    height = None
    foot = None
    second_citizenship = None

    for row in pageSoup.select('tr'):
        try:

            if row.select('th')[0].get_text().strip() == "Date of birth:":
                DOB = row.select('td')[0].get_text().strip()

            # COB = None
            if row.select('th')[0].get_text().strip() == "Place of birth:":
                POB = row.select('td')[0].get_text().strip()
                COB = row.select('td')[0].select('img')[0]['alt']

            if row.select('th')[0].get_text().strip() == "Position:":
                position = row.select('td')[0].get_text().strip()

            if row.select('th')[0].get_text().strip() == "Age:":
                age = int(row.select('td')[0].get_text().strip())

            if row.select('th')[0].get_text().strip() == "Height:":
                height = int(float(row.select('td')[0].get_text().strip().replace('m', '').replace(',', '.').strip())*100)

            if row.select('th')[0].get_text().strip() == "Foot:":
                foot = row.select('td')[0].get_text().strip()

        except:
            pass

    if COB == None:
        for row in pageSoup.select('tr'):
            try:
                if row.select('th')[0].get_text().strip() == "Citizenship:":
                    COB = row.select('td')[0].get_text().strip()
            except:
                pass

    for row in pageSoup.select('tr'):
        try:
            if row.select('th')[0].get_text().strip() == "Citizenship:":
                no_of_citizenships = len(row.select('td')[0].select('img'))
                if no_of_citizenships > 1:
                    second_citizenship = row.select('td')[0].select('img')[1]['alt']
                else:
                    second_citizenship = None
        except:
            pass


    if DOB != None:
        DOB = DOB.replace(" Happy Birthday", "")
        year_of_birth = int(DOB[len(DOB)-4:])
        month_of_birth = month_to_number(DOB.split(" ")[0])
        day_of_birth = int(DOB.split(" ")[1].split(",")[0])
        DOB = datetime.date(year_of_birth, month_of_birth, day_of_birth)

    else:
        year_of_birth = None
        month_of_birth = None
        day_of_birth = None

    biodict = {
        "player_id": player_id,
        "player_name": player_name,
        "day_of_birth": day_of_birth,
        "month_of_birth": month_of_birth,
        "year_of_birth": year_of_birth,
        "pob": POB,
        "cob": COB,
        "dob": DOB,
        "position": position,
        "height": height,
        "foot": foot,
        "second_citizenship": second_citizenship
    }

    return(biodict)


def current_football_bio_player_pull(pageSoup, player_id):

    if len(pageSoup.select('div.dataRibbonRIP')) > 0:
        current_club = "dead"
        current_club_country = "NA"
    else:
        current_club = pageSoup.select('div.dataZusatzImage')[0].select('img')[0].get('alt').lower()
        if current_club in ["retired", "without club", "unknown"]:
            current_club_country = "NA"
        else:
            current_club_country = pageSoup.select('div.dataZusatzDaten')[0].select('img')[0].get('alt').lower()


    if len(pageSoup.select('div.dataMarktwert')) == 0:
        market_value = 0

    else:
        market_value = pageSoup.select('div.dataMarktwert')[0].get_text().split("Last update")[0].strip()

        if "m" in market_value:
            market_value = int( float(market_value.strip().replace("â‚¬", "").replace("€","").replace("m","")) * 1000000 )
        elif "Th." in market_value:
            market_value = int(market_value.strip().replace("â‚¬", "").replace("€","").replace("Th.","")) * 1000
        elif "-":
            market_value = 0

    joined = None
    contract_expires = None
    contract_option = None
    on_loan_from = None
    on_loan_from_url = None
    on_loan_from_country = None
    loan_contract_expiry = None
    player_agent = None

    for row in pageSoup.select('tr'):
        try:

            if row.select('th')[0].get_text().strip() == "Joined:":
                joined = row.select('td')[0].get_text().strip()

            if row.select('th')[0].get_text().strip() == "Contract expires:":
                contract_expires = row.select('td')[0].get_text().strip()

            if row.select('th')[0].get_text().strip() == "Contract option:":
                contract_option = row.select('td')[0].get_text().strip()

            if row.select('th')[0].get_text().strip() == "On loan from:":
                on_loan_from = row.select('td')[0].get_text().strip().lower()
                on_loan_from_url = "https://www.transfermarkt.com" + row.select('td')[0].select('a')[0]['href']

            if row.select('th')[0].get_text().strip() == "Contract there expires:":
                loan_contract_expiry = row.select('td')[0].get_text().strip()

            if row.select('th')[0].get_text().strip() == "Player agent:":
                player_agent = row.select('td')[0].get_text().strip()
        except:
            pass

    if joined != None:
        year_joined = int(joined[len(joined)-4:])
        month_joined = month_to_number(joined.split(" ")[0])
        day_joined = int(joined.split(" ")[1].split(",")[0])
        joined = datetime.date(year_joined, month_joined, day_joined)

    if contract_expires != None:
        if contract_expires != "-":
            year_expired = int(contract_expires[len(contract_expires)-4:])
            month_expired = month_to_number(contract_expires.split(" ")[0])
            day_expired = int(contract_expires.split(" ")[1].split(",")[0])
            contract_expires = datetime.date(year_expired, month_expired, day_expired)
        else:
            contract_expires = None

    if loan_contract_expiry != None:
        if loan_contract_expiry != "-":
            year_expires = int(loan_contract_expiry[len(loan_contract_expiry)-4:])
            month_expires = month_to_number(loan_contract_expiry.split(" ")[0])
            day_expires = int(loan_contract_expiry.split(" ")[1].split(",")[0])
            loan_contract_expiry = datetime.date(year_expires, month_expires, day_expires)
        else:
            loan_contract_expiry = None

    if loan_contract_expiry != None:
        loan_contract_expiry,contract_expires = contract_expires,loan_contract_expiry

    if on_loan_from != None:
        temp_soup = get_souped_page(on_loan_from_url)
        on_loan_from_country = temp_soup.select('div.dataZusatzDaten')[0].select('img')[0]['alt'].lower()

    statusdict = {
        "player_id": player_id,
        "current_club": current_club,
        "current_club_country": current_club_country,
        "market_value": market_value,
        "joined": joined,
        "contract_expires": contract_expires,
        "contract_option": contract_option,
        "on_loan_from": on_loan_from,
        "on_loan_from_country": on_loan_from_country,
        "loan_contract_expiry": loan_contract_expiry,
        "player_agent": player_agent}

    return(statusdict)

def transfer_history_pull(pageSoup, player_id):


    transfered_from = []
    transferred_to = []
    market_values = []
    transfer_fees = []
    transfer_dates = []
    transfer_season = []
    country_from = []
    country_to = []

    market_values_value = None
#         print("player transfer history")
    not_first_row = True
    for box in pageSoup.select('div.box.transferhistorie'):
        if not_first_row:
            not_first_row = True

            for row in box.select('tr')[1:]:
                try:
                    transfered_from_value = row.select('td')[4].select('a')[0].get('href').split("/")[1].replace("-", " ")
#                 if transfered_from_value == ""
                    transfered_from.append(transfered_from_value)
                except:
                    pass

            for row in box.select('tr')[1:]:
                try:
                    transferred_to_value = row.select('td')[7].select('a')[0].get('href').split("/")[1].replace("-", " ")
                    transferred_to.append(transferred_to_value)
                except:
                    pass

            for row in box.select('tr')[1:]:
                try:
                    market_values_value = row.select('td.zelle-mw')[0].get_text()#.select('img')[0].get('alt')

                    if "m" in market_values_value:
                        market_values_value = int( float(market_values_value.replace("€","").replace("m","")) * 1000000 )
                    elif "Th." in market_values_value:
                        market_values_value = int(market_values_value.replace("€","").replace("Th.","")) * 1000
                    elif "-":
                        market_values_value = 0



                    market_values.append(market_values_value)
                except:
                    pass


        ## grab COUNTRY TO
            for row in box.select('tr')[1:]:
                try:
                    no_images = len(row.select('td')[6].select('img'))
                    if no_images > 0:
                        country_to.append(row.select('td')[6].select('img')[0].get('title').lower())
                    else:
                        country_to.append("no country")
                except:
                    pass


        ## grab COUNTRY FROM
            for row in box.select('tr')[1:]:
                try:
                    no_images = len(row.select('td')[3].select('img'))
                    if no_images > 0:
                        country_from.append(row.select('td')[3].select('img')[0].get('title').lower())
                    else:
                        country_from.append("no country")
                except:
                    pass


        ## grab TRANSFER FEE
        for row in box.select('tr')[1:]:
            try:
                transfer_fees_raw = row.select('td.zelle-abloese')[0].get_text()
                transfer_fees.append(transfer_fees_raw)
            except:
                pass


        ## grab TRANSFER DATE
        for row in box.select('tr')[1:]:
            try:
                date_raw = "" #removed if clause to get this to work. Is it still necessary?
                date_raw = row.select('td')[1].get_text().strip()#.get_text())#.select('img')[0].get('alt')
                year_of_transfer = int(date_raw[len(date_raw)-4:])
                month_of_transfer = month_to_number(date_raw.split(" ")[0])
                day_of_transfer = int(date_raw.split(" ")[1].split(",")[0])
                transfer_date = datetime.date(year_of_transfer, month_of_transfer, day_of_transfer)
                transfer_dates.append(transfer_date)
            except:
                pass

        ## grab SEASON
        for row in box.select('tr')[1:]:
            try:
                season_raw = row.select('td')[0].get_text().strip()
                if "Date" in season_raw:
                    pass
                else:
                    if "Total" in season_raw:
                        pass
                    else:
                        if "/" in season_raw:
                            transfer_season.append(season_raw.strip())
            except:
                pass
    ## edit the transfer fees / types

    transfer_types = ['loan' if "oan" in f else 'transfer' for f in transfer_fees]


    transfer_fees_new = []

    for t in range(len(transfer_fees)):

        if transfer_fees[t] == "-":
            transfer_fees_new.append(0)

        elif transfer_fees[t] == "Loan":
            transfer_fees_new.append(0)

        elif transfer_fees[t] == "End of loan":
            transfer_fees_new.append(0)

        elif transfer_fees[t] == "Free transfer":
            transfer_fees_new.append(0)

        elif "Loan fee:" in transfer_fees[t]:
            if "m" in transfer_fees[t]:
                transfer_fees_new.append( int( float( transfer_fees[t].replace("Loan fee:", "").replace("€", "").replace("m", "") ) * 1000000 ) )
            else:
                transfer_fees_new.append( int( transfer_fees[t].replace("Loan fee:", "").replace("€", "").replace("Th.", "") ) * 1000 )

        elif transfer_fees[t] == "?":
            transfer_fees_new.append(market_values[t])

        elif "m" in transfer_fees[t]:
            transfer_fees_new.append( int( float( transfer_fees[t].replace("€", "").replace("m", "") ) * 1000000 ) )

        elif "Th." in transfer_fees[t]:
            transfer_fees_new.append( int( transfer_fees[t].replace("Loan fee:", "").replace("€", "").replace("Th.", "") ) * 1000 )

        else:
            transfer_fees_new.append(transfer_fees[t])


    ## check internal

    internal_transfer = []

    for t in range(len(transfered_from)):
        if remove_youth(transfered_from[t]) == remove_youth(transferred_to[t]):
            internal_transfer.append("internal")
        else:
            internal_transfer.append("external")

    ## this seems to break this function. Is it still necessary country_from = country_from[:-1]

    DOB = None

    for row in pageSoup.select('tr'):
        try:
            if row.select('th')[0].get_text().strip() == "Date of birth:":
                DOB = row.select('td')[0].get_text().strip()
        except:
            pass

    # age at transfer
    if DOB != None:
        DOB = DOB.replace(" Happy Birthday", "")
        year_of_birth = int(DOB[len(DOB)-4:])
        month_of_birth = month_to_number(DOB.split(" ")[0])
        day_of_birth = int(DOB.split(" ")[1].split(",")[0])
        DOB = datetime.date(year_of_birth, month_of_birth, day_of_birth)

    age_at_transfer = [calculate_age_at_transfer(DOB, f) for f in transfer_dates]

    player_view = pd.DataFrame(
    {'transfered_from': transfered_from,
     'transferred_to': transferred_to,
     'market_values': market_values,
     'transfer_fees': transfer_fees_new,
     'transfer_dates': transfer_dates,
     'transfer_season': transfer_season,
     'country_to': country_to,
     'country_from': country_from,
     'transfer_types': transfer_types,
     'internal_external_transfer': internal_transfer,
     'age_at_transfer': age_at_transfer
    })

    player_view['player_id'] = player_id


    ####  ADD YOUTH CLUBS ######################################################
    youth_clubs = None
    try:
        for box in pageSoup.select('div.box'):
            if box.select('div')[0].get_text().strip() == 'Youth clubs':
                youth_clubs = box.select('div')[1].get_text().strip()
    except:
        pass

    youth_clubs_list__ = []

    if youth_clubs != None:

        youth_club = youth_clubs

        for f in youth_club.split(","):
    #             print(f.split(" (")[0].strip().lower(), remove_youth(f.split(" (")[0].strip().lower()))
            youth_clubs_list__.append(remove_youth(f.split(" (")[0].strip().lower()))

    if len(player_view[player_view['age_at_transfer'] <= 18].transfered_from) > 0:
        youth_clubs_list__ = youth_clubs_list__ + [remove_youth(ff) for ff in player_view[player_view['age_at_transfer'] <= 18].transfered_from]

    if len(youth_clubs_list__) > 0:
        player_view['all_youth_clubs'] = ','.join(map(str, list(set(youth_clubs_list__))))
    #         print(','.join(map(str, list(set(youth_clubs_list__)))) )
    else:
        player_view['all_youth_clubs'] = remove_youth(player_view.tail(1).iloc[0]['transfered_from'])

    return(player_view)


def performance_history_pull(base_url, player_id, player_dob):
    # print(base_url.replace("profil", "leistungsdatendetails") + "/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1")
    pageSoup2 = get_souped_page(base_url.replace("profil", "leistungsdatendetails") + "/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1")

    perf_table = pageSoup2.select('table.items')[0]

    ## set empty lists for collection
    season_list = []
    competition_list = []
    competition_code_list = []
    club_list = []
    in_squad_list = []
    appearances_list = []
    ppg_list = []
    goals_list = []
    assists_list = []
    subbed_on_list = []
    subbed_off_list = []
    yellow_card_list = []
    second_yellow_card_list = []
    red_card_list = []
    penalties_list = []
    mins_played_list = []
    clean_sheets_list = []
    goals_conceded_list = []

    #check position
    if len(perf_table.select('tr')[2].select('td')) == 17:
        position_profile = "GK"
    else:
        position_profile = "OUTFIELD"

    if position_profile == "OUTFIELD":
        for row in perf_table.select('tr')[2::]:
            season = row.select('td')[0].get_text()
            competition = row.select('td')[2].get_text()
            competition_code = row.select('td')[2].select('a')[0]['href'].split("/")[4]
            club = row.select('td')[3].select('img')[0]['alt']
            in_squad = int(row.select('td')[4].get_text())
            appearances = row.select('td')[5].get_text()
            ppg = row.select('td')[6].get_text()
            goals = row.select('td')[7].get_text()
            assists = row.select('td')[8].get_text()
            subbed_on = row.select('td')[10].get_text()
            subbed_off = row.select('td')[11].get_text()
            yellow_card = row.select('td')[12].get_text()
            second_yellow_card = row.select('td')[13].get_text()
            red_card = row.select('td')[14].get_text()
            penalties = row.select('td')[15].get_text()
            mins_played = row.select('td')[17].get_text()

            appearances = 0 if appearances == "-" else int(appearances)
            ppg = 0 if ppg in ["-", "0,00"] else float(ppg)
            goals = 0 if goals == "-" else int(goals)
            assists = 0 if assists == "-" else int(assists)
            subbed_on = 0 if subbed_on == "-" else int(subbed_on)
            subbed_off = 0 if subbed_off == "-" else int(subbed_off)
            yellow_card = 0 if yellow_card == "-" else int(yellow_card)
            second_yellow_card = 0 if second_yellow_card == "-" else int(second_yellow_card)
            red_card = 0 if red_card == "-" else int(red_card)
            penalties = 0 if penalties == "-" else int(penalties)

            if mins_played == "-":
                mins_played = 0
            elif "." in mins_played:
                # print(mins_played)
                mins_played = mins_played.replace("'", "").replace(".", "")
            else:
                mins_played = int(mins_played.replace("'", ""))

            goals_conceded = 0
            clean_sheets = 0

            ## append values
            season_list.append(season)
            competition_list.append(competition)
            competition_code_list.append(competition_code)
            club_list.append(club)
            in_squad_list.append(in_squad)
            appearances_list.append(appearances)
            ppg_list.append(ppg)
            goals_list.append(goals)
            assists_list.append(assists)
            subbed_on_list.append(subbed_on)
            subbed_off_list.append(subbed_off)
            yellow_card_list.append(yellow_card)
            second_yellow_card_list.append(second_yellow_card)
            red_card_list.append(red_card)
            penalties_list.append(penalties)
            mins_played_list.append(mins_played)
            clean_sheets_list.append(clean_sheets)
            goals_conceded_list.append(goals_conceded)

    else:
        for row in perf_table.select('tr')[2::]:
            season = row.select('td')[0].get_text()
            competition = row.select('td')[2].get_text()
            competition_code = row.select('td')[2].select('a')[0]['href'].split("/")[4]
            club = row.select('td')[3].select('img')[0]['alt']
            in_squad = int(row.select('td')[4].get_text())
            appearances = row.select('td')[5].get_text()
            ppg = row.select('td')[6].get_text()
            goals = row.select('td')[7].get_text()
            subbed_on = row.select('td')[9].get_text()
            subbed_off = row.select('td')[10].get_text()
            yellow_card = row.select('td')[11].get_text()
            second_yellow_card = row.select('td')[12].get_text()
            red_card = row.select('td')[13].get_text()
            goals_conceded = row.select('td')[14].get_text()
            clean_sheets = row.select('td')[15].get_text()
            mins_played = row.select('td')[16].get_text()

            appearances = 0 if appearances == "-" else int(appearances)
            ppg = 0 if ppg in ["-", "0,00"] else float(ppg)
            goals = 0 if goals == "-" else int(goals)
            subbed_on = 0 if subbed_on == "-" else int(subbed_on)
            subbed_off = 0 if subbed_off == "-" else int(subbed_off)
            yellow_card = 0 if yellow_card == "-" else int(yellow_card)
            second_yellow_card = 0 if second_yellow_card == "-" else int(second_yellow_card)
            red_card = 0 if red_card == "-" else int(red_card)
            clean_sheets = 0 if clean_sheets == "-" else int(clean_sheets)
            goals_conceded = 0 if goals_conceded == "-" else int(goals_conceded)

            if mins_played == "-":
                mins_played = 0
            elif "." in mins_played:
                # print(mins_played)
                mins_played = mins_played.replace("'", "").replace(".", "")
            else:
                mins_played = int(mins_played.replace("'", ""))

            assists = 0
            penalties = 0

            ## append values
            season_list.append(season)
            competition_list.append(competition)
            competition_code_list.append(competition_code)
            club_list.append(club)
            in_squad_list.append(in_squad)
            appearances_list.append(appearances)
            ppg_list.append(ppg)
            goals_list.append(goals)
            assists_list.append(assists)
            subbed_on_list.append(subbed_on)
            subbed_off_list.append(subbed_off)
            yellow_card_list.append(yellow_card)
            second_yellow_card_list.append(second_yellow_card)
            red_card_list.append(red_card)
            penalties_list.append(penalties)
            mins_played_list.append(mins_played)
            clean_sheets_list.append(clean_sheets)
            goals_conceded_list.append(goals_conceded)

    performance_data = pd.DataFrame(
            {'season': season_list,
            'competition': competition_list,
            'competition_code': competition_code_list,
            'club': club_list,
            'in_squad': in_squad_list,
            'appearances': appearances_list,
            'ppg': ppg_list,
            'goals': goals_list,
            'assists': assists_list,
            'subbed_on': subbed_on_list,
            'subbed_off': subbed_off_list,
            'yellow_card': yellow_card_list,
            'second_yellow_card': second_yellow_card_list,
            'red_card': red_card_list,
            'penalties': penalties_list,
            'mins_played': mins_played_list,
            'clean_sheets': clean_sheets_list,
            'goals_conceded': goals_conceded_list
            })


    performance_data['player_id'] = player_id

    age = []
    for s in performance_data.season:

        if "/" in s:
            year = int(s.split("/")[0])
            if year < 30:
                year = 2000 + year
            else:
                year = 1900 + year
            competition_start_date = datetime.date(year, 8, 1)

        else:
            year = int(s)
            competition_start_date = datetime.date(year, 4, 1)

        age.append(calculate_age(player_dob, competition_start_date))

    performance_data['age'] = age

    return(performance_data)

def market_value_historic_pull(base_url, player_id):

    mv_soup = get_souped_page(base_url.replace("profil", "marktwertverlauf"))

    if mv_soup.find("script", text=re.compile("Highcharts.Chart")) != None:

        script = mv_soup.find("script", text=re.compile("Highcharts.Chart")).text
        parsed = js2xml.parse(script)


        xpath = '//array//object//property'

        age_list = []
        club_list = []
        mv_list = []
        date_of_value_list = []

        for i in range(len(parsed.xpath(xpath))):

            age = None
            club = None
            raw_value = None
            date_of_value = None
            date_raw = None

            if parsed.xpath(xpath)[i].get('name') == 'age':
                age = int(stringify_children(parsed.xpath(xpath)[i]).split("number value=")[1].split("/")[0][1:][:-1])
                age_list.append(age)

            if parsed.xpath(xpath)[i].get('name') == 'verein':
                club = stringify_children(parsed.xpath(xpath)[i]).split("<string>")[1].split("</string>")[0].lower()
                club_list.append(club)

            if parsed.xpath(xpath)[i].get('name') == 'mw':
                raw_value = stringify_children(parsed.xpath(xpath)[i]).split("<string>")[1].split("</string>")[0].replace("€", "")

                if "m" in raw_value:
                    raw_value = int( float(raw_value.strip().replace("â‚¬", "").replace("€","").replace("m","")) * 1000000 )
                elif "Th." in raw_value:
                    raw_value = int(raw_value.strip().replace("â‚¬", "").replace("€","").replace("Th.","")) * 1000
                elif "-":
                    raw_value = 0

                mv_list.append(raw_value)

            if parsed.xpath(xpath)[i].get('name') == 'datum_mw':
                date_raw = stringify_children(parsed.xpath(xpath)[i]).split("<string>")[1].split("</string>")[0]
                if date_raw != None:
                    year_of_birth = int(date_raw[len(date_raw)-4:])
                    month_of_birth = month_to_number(date_raw.split(" ")[0])
                    day_of_birth = int(date_raw.split(" ")[1].split(",")[0])
                    date_of_value = datetime.date(year_of_birth, month_of_birth, day_of_birth)

                date_of_value_list.append(date_of_value)


        market_value_history = pd.DataFrame(
        {'club': club_list,
         'value': mv_list,
         'data_date': date_of_value_list,
         'age': age_list
        })

        market_value_history['player_id'] = player_id

        return(market_value_history)

    else:
        market_value_history = pd.DataFrame(
        {'club': [None],
         'value': [None],
         'data_date': [None],
         'age': [None]
        })

        market_value_history['player_id'] = player_id

        return(market_value_history)




def tm_pull(player_page,
            data_folder = "",
            player_bio = False,
            player_status = False,
            transfer_history = False,
            performance_data = False,
            market_value_history = False,
            output = "pandas" ):

    player_id = player_page.split("/")[-1:][0]
    raw_base_page = get_souped_page(player_page)

    bio = bio_player_pull(raw_base_page, player_id)
    output_dict = {}

    player_dob = bio['dob']

    ### if the user has selected to pull player_bio data then run
    if player_bio:

        # pandas output
        if output == "pandas":
            output_dict['player_bio'] = pd.DataFrame.from_dict(bio, orient = "index").transpose()

        # csv output
        elif output == "csv":
            with open((data_folder + player_id + '_bio.csv'),'w') as f:
                w = csv.writer(f)
                w.writerow(bio.keys())
                w.writerow(bio.values())

    ### if the user has selected to pull player_status data then run
    if player_status:

        status = current_football_bio_player_pull(raw_base_page, player_id)

        # pandas output
        if output == "pandas":
            output_dict['player_status'] = pd.DataFrame.from_dict(status, orient = "index").transpose()

        # csv output
        elif output == "csv":
            with open((data_folder + player_id + '_status.csv'),'w') as f:
                w = csv.writer(f)
                w.writerow(status.keys())
                w.writerow(status.values())

    ### if the user has selected to pull player_transfers data then run
    if transfer_history:

        transfers = transfer_history_pull(raw_base_page, player_id)

        # pandas output
        if output == "pandas":
            output_dict['transfer_history'] = transfers

        # csv output
        elif output == "csv":
            transfers.to_csv((data_folder + player_id + '_transfer_history.csv'), index = False)


    ### if the user has selected to pull market_value_history data then run
    if market_value_history:

        historic_market_value = market_value_historic_pull(player_page, player_id)

        # pandas output
        if output == "pandas":
            output_dict['market_value_history'] = historic_market_value

        # csv output
        elif output == "csv":
            historic_market_value.to_csv((data_folder + player_id + '_historic_market_value.csv'), index = False)


    ### if the user has selected to pull performance data then run
    if performance_data:

        perf_data = performance_history_pull(player_page, player_id, player_dob)

        # pandas output
        if output == "pandas":
            output_dict['performance_data'] = perf_data

        # csv output
        elif output == "csv":
            perf_data.to_csv((data_folder + player_id + '_performance_data.csv'), index = False)

    # return all pandas output
    if output == "pandas":
        return(output_dict)

def squad_number_history(base_url, squad_type = "both"):
    '''
    This method returns the squad numbers history of a player.

    Squad numbers history is returned according to the squad type. If the squad type is both,
    then the squad numbers of the players representation for both club and country is returned.

    Args:
    -----------
        base_url: transfermarkt url of the player, string
        squad_type: The type of squad. Default - both. Can be one of ["club", "country", "both], string
    
    Returns:
    -----------
        squad_df: History of squad numbers of the player, Pandas DataFrame
    
    Raises:
    -----------
        Only User Warnings are raised when the squad type doesn't match with one of the 3 options and
        if the player hasn't played for his country and the user requested for both squad numbers.
    '''

    # Check if the squad type is in one of the 3 options
    if squad_type not in ["club", "country", "both"]:
        warnings.warn("Unsupported squad type", UserWarning)
        return None
    
    #Get player id
    player_id = base_url.split("/")[-1:][0]

    # Scrape the squad number page.
    souped_page = get_souped_page(base_url.replace("profil", "rueckennummern"))
    
    #Get the tables with the data directly.
    tables = souped_page.findAll("table", {"class": "items"})

    # Get the columns and add a user defined column
    columns = [col.get_text() for col in tables[0].findAll("th") if col.get_text() != ""]
    columns.append("squad_type")

    # Checking if the player has played for his country
    if len(tables) == 1:
        isNationalAvailable = False
    else:
        isNationalAvailable = True
    values = []

    #Parsing the club squad numbers
    if squad_type in ["both", "club"]:
        for row in tables[0].findAll("tr"):
            row_elem = [val.get_text() for val in row.findAll("td") if val.get_text() != ""]
            if len(row_elem) > 0:
                row_elem.append("club")
                values.append(row_elem)

    #Parsing the coutry squad numbers
    if squad_type in ["both", "country"] and isNationalAvailable:
        for row in tables[1].findAll("tr"):
            row_elem = [val.get_text() for val in row.findAll("td") if val.get_text() != ""]
            if len(row_elem) > 0:
                row_elem.append("country")
                values.append(row_elem)
    elif isNationalAvailable!=True and squad_type in ["both", "country"]:
        warnings.warn("Player hasn't played for his country", UserWarning)
    
    # pandas dataframe output
    if len(values) == 0:
        return None
    squad_df = pd.DataFrame(values, columns=columns)
    squad_df["player_id"] = player_id
    return squad_df    
    
    
