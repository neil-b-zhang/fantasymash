import math 
import pandas as pd  
import sys
import random

def get_inputs():
    input_dict = {}
    
    # get user input on which positions to rank
    while True:
        temp_pos_in = input('Which position(s) do you want to rank?\n'+
                            '    Options: All, QB, RB, WR, TE, K\n').lower()
        if temp_pos_in == 'quit':
            sys.exit('Exiting with quit command')
        elif temp_pos_in not in ['all', 'qb', 'rb', 'wr', 'te', 'k']:
            print('\nIncorrect input detected\n')
            pass
        else:
            input_dict['pos'] = temp_pos_in
            break
        
    while True:
        try:
            num_players = int(input('How many players do you want to rank?\n'))
        except ValueError:
            print("Not an integer! Try again.")
            continue
        else:
            input_dict['num_players'] = num_players 
            break 
            
    return input_dict

# function for reading in ff data from csv
def read_data(inputs):
    data = pd.read_csv('ffdata_2019.csv')
    
    # clean up data from profootballref
    data.columns = map(str.lower, data.columns)
    data=data.fillna(0)
    data = data.applymap(lambda s:s.lower() if type(s) == str else s)
    data['player'] = data['player'].map(lambda x: x.rstrip('*+'))
    
    # check for desired position
    if inputs['pos'] != 'all':
        data = data[data['fantpos']==inputs['pos']]
    
    # get num players based on input    
    data = data.head(inputs['num_players'])

    return data
    
    
# function to calculate the Probability 
def prob(rating1, rating2):   
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400)) 
    
def elorating(p1, r1, p2, r2, k=32): 
   
    # To calculate the Winning 
    # Probability of Player 2 
    pb2 = prob(r1, r2) 
  
    # To calculate the Winning 
    # Probability of Player 1 
    pb1 = prob(r2, r1) 
  
    # get user input on which is better
    while True:
        try:
            winner = int(input('Which player do you think is better?\n'+
                               '{} (1) or {} (2)\n'.format(p1, p2)))
        except ValueError:
            print("Not an integer! Try again.")
        else:
            if winner not in [1, 2]:
                print('Please enter "1" or "2"\n')
            else:
                break
        
    # update elo ratings for p1 winning
    if (winner == 1) : 
        r1 = r1 + k * (1 - pb1) 
        r2 = r2 + k * (0 - pb2) 
      
    # update elo rating for p2 winning
    else : 
        r1 = r1 + k * (0 - pb1) 
        r2 = r2 + k * (1 - pb2) 
      
    print("Updated ratings:") 
    print("p1 =", round(r1, 6)," p2 =", round(r2, 6)) 
    return (r1, r2)

def mash(data):
    # set all ratings to 1000 to start
    ratings_dict = dict.fromkeys(data['player'].tolist(), 1000)
    while True:
        # randomly pick 2 players to compare
        keys = random.sample(list(ratings_dict), 2)
    
        # get elos
        upd_elos = elorating(keys[0], ratings_dict[keys[0]], keys[1], ratings_dict[keys[1]])
        
        # update elos
        ratings_dict[keys[0]] = upd_elos[0]
        ratings_dict[keys[1]] = upd_elos[1]
        
        # ask if user wants to continue
        user_quit = input('Please enter "quit" if you would like to finish\n')
        if user_quit == 'quit':
            break
    
    # output final dataframe
    final_ratings = pd.DataFrame.from_dict(ratings_dict, orient='index')
    final_ratings = final_ratings.reset_index()
    
    final_ratings.columns = ['player', 'rating']

    final_ratings = final_ratings.sort_values(by=['rating'], ascending=False)
    print(final_ratings)
    print('OUTPUTTING FINAL RESULTS...')
    final_ratings.to_csv('final_ratings.csv')
    print('DONE')
    sys.exit()
    
if __name__ == "__main__": 
    
    # get user inputs
    inputs = get_inputs()
    #inputs = {'pos': 'wr', 'num_players': 10}
    
    # get data
    data = read_data(inputs)
    
    # start mashing
    mash(data)

