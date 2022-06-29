# TODO allow users to save and load progress
# TODO make flask app version

import warnings
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import random

off_pos = ['TE', 'QB', 'FB', 'WR', 'RB', 'K']
def_pos = ['DE', 'SS', 'DB', 'CB', 'FS', 'DT', 'OLB', 'LB', 'ILB', 'MLB', 'DL']

def get_players():
    # change the file path here to pick what csv to read for the data
    # TODO make this an input arg from the user
    player_data = pd.read_csv('data/Basic_Stats_head.csv')
    active_players = player_data.loc[player_data['Current Status'] == 'Active']

    keep_cols = ['Name', 'Current Team', 'Position', 'Age']
    all_players = active_players[keep_cols]
    all_players['elo'] = 1000


    off_players = all_players.loc[all_players['Position'].isin(off_pos)]
    def_players = all_players.loc[all_players['Position'].isin(def_pos)]

    return [all_players, off_players, def_players]

def expected(A, B):
    """
    Calculate expected score of A in a match against B
    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def elo(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player
    :param old: The previous Elo rating
    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return old + k * (score - exp)

def start_app(players_dbs):
    # TODO allow user to filter playerset by position
    print('Rank fantasy players!')
    print('1: All players')
    print('2: Offense players')
    print('3: Defense players')
    #player_selection = int(input('Which type of players would you like to rank?\n'))
    player_selection = 2

    selected_players = pd.DataFrame()
    if player_selection == 1:
        selected_players = players_dbs[0]
        print('All players selected!')
    elif player_selection == 2:
        selected_players = players_dbs[1]
        print('Offense players selected!')
    elif player_selection == 3:
        selected_players = players_dbs[2]
        print('Defense players selected!')
    else:
        pass
    selected_players['times_rated'] = 0


    user_esc = False
    round_counter = 1
    # primary loop for rating players
    while(not user_esc):
        # print(selected_players)


        # randomly select two players to pick between
        total_players_selected = selected_players['times_rated'].sum()

        player1 = ''
        player1_elo = 0
        player2 = ''
        player2_elo = 0
        if total_players_selected == 0:
            player_matchup = random.sample(selected_players['Name'].tolist(), 2)
            player1 = player_matchup[0]
            player2 = player_matchup[1]

            player1_elo = int(selected_players.loc[selected_players['Name'] == player1, 'elo'].iloc[0])
            player2_elo = int(selected_players.loc[selected_players['Name'] == player2, 'elo'].iloc[0])

        else:
            # the more times a player has been rated relative to the field, the less likely they are to be rated again
            matchup_not_found = True
            while matchup_not_found:
                algo_times_picked = selected_players['times_rated'] + 1
                total_algo_times_picked = sum(algo_times_picked)
                algo_times_picked_pct = algo_times_picked/total_algo_times_picked
                inv_sel_pct = 1/algo_times_picked_pct
                inv_sel_pct_tot = sum(inv_sel_pct)

                prob_weights = inv_sel_pct/inv_sel_pct_tot


                """print('{}'.format(pd.DataFrame({'name': selected_players['Name'],
                                                'times picked': selected_players['times_rated'],
                                                'prob weight': prob_weights})))"""


                player_matchup = random.choices(selected_players['Name'], weights = prob_weights, k=2)
                player1 = player_matchup[0]
                player2 = player_matchup[1]

                player1_elo = int(selected_players.loc[selected_players['Name'] == player1, 'elo'].iloc[0])
                player2_elo = int(selected_players.loc[selected_players['Name'] == player2, 'elo'].iloc[0])

                if player1 != player2 and abs(player1_elo - player2_elo) < 20:
                    matchup_not_found = False



        print('\n==================================================================')
        print('Round {}: Which of the following players would you rather have?'.format(round_counter))
        user_player_sel = int(input('(1) {} or (2) {}? (3) Exit\n'.format(player1, player2)))

        p1_score = 0
        p2_score = 0
        if user_player_sel == 1:
            p1_score = 1
        elif user_player_sel == 2:
            p2_score = 1
        elif user_player_sel == 3:
            break

        # calculate new player elos based on user selection
        p1_exp = expected(player1_elo, player2_elo)
        p2_exp = expected(player2_elo, player1_elo)

        p1_elo = elo(player1_elo, p1_exp, p1_score, k=32)
        p2_elo = elo(player2_elo, p2_exp, p2_score, k=32)

        # update elo rankings in main dict
        selected_players.loc[selected_players['Name'] == player1, 'elo'] = p1_elo
        selected_players.loc[selected_players['Name'] == player1, 'times_rated'] += 1

        selected_players.loc[selected_players['Name'] == player2, 'elo'] = p2_elo
        selected_players.loc[selected_players['Name'] == player2, 'times_rated'] += 1

        print('{} updated elo: {}'.format(player1, p1_elo))
        print('{} updated elo: {}'.format(player2, p2_elo))
        round_counter += 1


    print('DONE RATING!')
    print(selected_players.sort_values(by=['elo']))


if __name__ == '__main__':
    players_dbs = get_players()

    start_app(players_dbs)
    print('FantasyMash stopped')


