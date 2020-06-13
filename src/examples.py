


from tools import *
from players import *
from leaguesclubs import *

if __name__ == '__main__':

    player_page = "https://www.transfermarkt.com/tyrone-mings/profil/spieler/253677"

    market_value_data = tm_pull(player_page, player_bio = True, market_value_history = True, output = 'pandas')
    print(market_value_data['player_bio'])
    print(isinstance(market_value_data, dict))
