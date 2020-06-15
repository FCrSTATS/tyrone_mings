from .tools import *


def change_transfer_url(transfers_url, season = "2019"):

    if isinstance(season, int):
        season = str(season)

    if "?saison_id" in transfers_url:
        pass
    else:
        transfers_url = transfers_url + "/plus/?saison_id=" + season + "&s_w=&leihe=1&intern=0&intern=1"

    return(transfers_url)

def get_league_transfers_summary(transfers_url, season = "2019"):

    trasfers_url = change_transfer_url(transfers_url, season)
    soup = get_souped_page(trasfers_url)
    competition_id = trasfers_url.split("wettbewerb/")[1].split("/plus")[0]

    counter = 0
    box_select = 0

    for box_index in range(len(soup.select('div.box'))):
        box = soup.select('div.box')[box_index]
        try:
            if "Transfer record" in box.select('h2')[0].get_text():
                counter += 1
                if counter == 1:
                    box_select = box_index
        except:
            pass

    transfer_box = soup.select('div.box')[box_select]

    values_raw = []

    for item in transfer_box.select('div.text')[0].select('span'):
        values_raw.append(item.get_text())

    for item in transfer_box.select('div.text')[1].select('span'):
        values_raw.append(item.get_text())

    for item in transfer_box.select('div.text')[2].select('span'):
        values_raw.append(item.get_text())

    values_raw = [int(f.replace('€','').replace(',','')) for f in values_raw]

    tranfser_overview = {}
    tranfser_overview['total_income'] = values_raw[0]
    tranfser_overview['avg_income_per_club'] = values_raw[1]
    tranfser_overview['avg_income_per_player'] = values_raw[2]
    tranfser_overview['total_spend'] = values_raw[3]
    tranfser_overview['avg_spend_per_club'] = values_raw[4]
    tranfser_overview['avg_spend_per_player'] = values_raw[5]
    tranfser_overview['total_balance'] = values_raw[6]
    tranfser_overview['avg_balance_per_club'] = values_raw[7]
    tranfser_overview['avg_balance_per_player'] = values_raw[8]
    tranfser_overview['competition'] = soup.select('h1')[0].get_text().strip().lower()
    tranfser_overview['competition_id'] = competition_id
    tranfser_overview['season'] = soup.select('div.table-header')[0].get_text().replace("Transfers ","").strip()
    tranfser_overview['country'] = soup.select('div.flagge')[0].select('img')[0]['alt'].lower()
    return(tranfser_overview)
