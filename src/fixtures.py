from .tools import *

def get_to_fixure_grid(league_url, season = "2019"):
    if "saison_id" in league_url:
        league_url = league_url.replace("startseite", "kreuztabelle")
    else:
        league_url = league_url + "/saison_id/" + season
        league_url = league_url.replace("startseite", "kreuztabelle")
    return(league_url)

def get_played_fixtures_from_league(league_url):

    soup = get_souped_page(get_to_fixure_grid(league_url))

    fixture_url_list = []
    grid = soup.select('table.kreuztabelle')[0]
    for row in grid.select('tr')[1:-1]:
        for col in row.select('td')[1:-1]:
            if ":" in col.get_text().strip():
                fixture_url_list.append("https://www.transfermarkt.com" + col.select('a')[0]['href'])
    return(fixture_url_list)


def get_played_fixtures_from_gameday_overview(game_day_url):

    soup = get_souped_page(game_day_url)
    fixture_url_list = []

    for i in soup.select('span.ergebnis-box'):
        if i.get_text().strip() != "-:-":
            fixture_url_list.append("https://www.transfermarkt.com" + i.select('a')[0]['href'])

    return(fixture_url_list)
