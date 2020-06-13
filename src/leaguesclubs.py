
from .tools import *


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

def get_league_mean_player_value_for_season(league_url, season):
    '''
    From a league page such as :
    https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1
    retrived the mean Transfermarkt player valuation for the league in a season
    '''
    # change url to include season
    league_url = league_url + '/plus/?saison_id=' + season
    # load table as html
    league_base_page = get_souped_page(league_url)
    div = league_base_page.findAll('div', {'class':'responsive-table'})[0]
    data_table = div.find('table')
    # return dummy if values are not available
    if data_table.find('tr').findAll('th')[-1].text !='ø MV':
      return 0
    # get table body
    dt_body = data_table.find('tbody')
    # for every row, get value of the last column and translate into an integer
    results = []
    for row in dt_body.findAll('tr'):
      val = row.findAll('td')[-1].text
      if val == '-':
        val = '0'
      else:
        val = val.replace('€','').replace('m','0000').replace('Th','000').replace('.','')
      results.append(int(val))
    return np.mean(results)
