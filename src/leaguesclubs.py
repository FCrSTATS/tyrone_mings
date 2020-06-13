from tools import *


def get_club_urls_from_league_page(club_url):
    '''
    From a league page such as :
    https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1
    retrived the url links for all clubs
    '''

    league_base_page = get_souped_page(club_url)

    club_urls = []
    for row in league_base_page.find_all('table', 'items')[0].select('tr'):
        for item in row.find_all('td', 'hauptlink'):
            try:
                link = item.select('a')[0]['href']
                if link != None:
                    if len(link) > 0:
                        club_urls.append("https://www.transfermarkt.com" + link)
            except:
                pass

    return(list(set(club_urls)))



def get_player_urls_from_club_page(club_url):
    '''
    From a club page such as :
    https://www.transfermarkt.com/manchester-united/startseite/verein/985/saison_id/2019
    retrived the url links for all players
    '''
    club_base_page = get_souped_page(club_url)

    player_urls = []
    for row in club_base_page.find_all('table', 'items')[0].select('tr'):
        for item in row.find_all('td', 'hauptlink'):
            try:
                link = item.select('a')[0]['href']
                if link != None:
                    if len(link) > 0:
                        player_urls.append("https://www.transfermarkt.com" + link)
            except:
                pass

    return(list(set(player_urls)))



def get_player_urls_from_league_page(league_url, verbose = False):
    '''
    From a league page such as :
    https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1
    retrived the url links for all players from all clubs

    if you want to check on progress chhange verbose to True
    '''
    players = []

    clubs = get_club_urls_from_league_page(league_url)
    for c in clubs:
        players = players +  get_player_urls_from_club_page(c)
        if verbose:
            print(c.split("/")[3].replace("-", " "), "players added")
    return(players)
