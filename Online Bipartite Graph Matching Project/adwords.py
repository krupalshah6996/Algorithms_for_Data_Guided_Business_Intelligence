import pandas as pd
import random
import numpy as np
import sys
from copy import deepcopy
random.seed(0)
# def helper(bid, budget_1, budget_2):
#     return bid*(1 - np.exp((budget_2 - budget_1)/budget_2 - 1))

def calculate_revenue_greedy(budget_dict, bid_dict, queries):
    revenue = 0.0
    
    for query in queries:
        current_bid = bid_dict[query]
        highest_bid = -1
        highest_bidder = list(current_bid.keys())[0]
        flag = False
        for key in current_bid.keys():
            if budget_dict[key] >= current_bid[key]:
                flag = True
                break
        if flag:
            for key in current_bid.keys():
                if budget_dict[key] >= current_bid[key]:
                    if highest_bid < current_bid[key]:
                        highest_bidder = key
                        highest_bid = current_bid[key]
                    elif highest_bid == current_bid[key]:
                        if highest_bidder > key:
                            highest_bidder = key
                            highest_bid = current_bid[key]
            revenue += bid_dict[query][highest_bidder]
            budget_dict[highest_bidder] -= bid_dict[query][highest_bidder] 

    return revenue
        
def calculate_revenue_balance(budget_dict, bid_dict, queries):
    revenue = 0.0
    
    for query in queries:
        current_bid = bid_dict[query]
        # highest_bid = -1
        highest_bidder = list(current_bid.keys())[0]
        flag = False
        for key in current_bid.keys():
            if budget_dict[key] >= current_bid[key]:
                flag = True
                break
        if flag:
            for key in current_bid.keys():
                if budget_dict[key] >= current_bid[key]:
                    if budget_dict[highest_bidder] < budget_dict[key]:
                        highest_bidder = key
                        # highest_bid = current_bid[key]
                    elif budget_dict[highest_bidder] == budget_dict[key]:
                        if highest_bidder > key:
                            highest_bidder = key
            revenue += bid_dict[query][highest_bidder]
            budget_dict[highest_bidder] -= bid_dict[query][highest_bidder]        
        

    return revenue

def calculate_revenue_msvv(budget_dict, original_budget_dict, bid_dict, queries):
    revenue = 0.0

    
    for query in queries:
        current_bid = bid_dict[query]
        # highest_bid = -1
        highest_bidder = list(current_bid.keys())[0]
        # print(bid_dict)
        # print(highest_bidder)
        flag = False
        for key in current_bid.keys():
            if budget_dict[key] >= current_bid[key]:
                flag = True
                break
        if flag:
            for key in current_bid.keys():
                if budget_dict[key] >= current_bid[key]:
                    # temp = bid_dict[highest_bidder]
                    bid_1 = current_bid[highest_bidder]*(1 - np.exp((original_budget_dict[highest_bidder] - budget_dict[highest_bidder])/original_budget_dict[highest_bidder] - 1))
                    # bid_1 = helper(bid_dict[highest_bidder], budget_dict[highest_bidder], original_budget_dict[highest_bidder])
                    bid_2 = current_bid[key]*(1 - np.exp((original_budget_dict[key] - budget_dict[key])/original_budget_dict[key] - 1))
                    # bid_2 = helper(bid_dict[key], budget_dict[key], original_budget_dict[key])
                    if bid_2 > bid_1:
                        highest_bidder = key
                        # highest_bid = current_bid[key]
                    elif bid_1 == bid_2:
                        if highest_bidder > key:
                            highest_bidder = key
            revenue += bid_dict[query][highest_bidder]
            budget_dict[highest_bidder] -= bid_dict[query][highest_bidder]        
       

    return revenue   

if __name__ == "__main__":
    input_algorithm = sys.argv[1]
    queries_file = open('queries.txt','r').readlines()
    queries = []
    budget_dict = {}
    bid_dict = {}

    for query in queries_file:
        queries.append(query.strip())

    bidder_data = pd.read_csv('bidder_dataset.csv')
    for i in range(len(bidder_data)):
        advertiser = bidder_data.iloc[i]['Advertiser']
        keyword = bidder_data.iloc[i]['Keyword']
        bid_value = bidder_data.iloc[i]['Bid Value']
        budget = bidder_data.iloc[i]['Budget']
        if advertiser not in budget_dict.keys():
            budget_dict[advertiser] = budget
        if keyword not in bid_dict.keys():
            bid_dict[keyword] = {}
        if advertiser not in bid_dict[keyword].keys():
            bid_dict[keyword][advertiser] = bid_value
    print(budget_dict)
    final_revenue = 0.0
    revenue = 0.0
    if len(sys.argv) != 2:
        print("Invalid Input")
    elif input_algorithm == "greedy":
        temp_budget = deepcopy(budget_dict)
        print("Revenue: ",round(calculate_revenue_greedy(temp_budget, bid_dict, queries),2))
        for i in range(100):
            random.shuffle(queries)
            temp_budget = deepcopy(budget_dict)
            revenue += calculate_revenue_greedy(temp_budget, bid_dict, queries)
        final_revenue = revenue/100
    elif input_algorithm == "balance":
        temp_budget = deepcopy(budget_dict)
        print("Revenue: ",round(calculate_revenue_balance(temp_budget, bid_dict, queries),2))
        for i in range(100):
            random.shuffle(queries)
            temp_budget = deepcopy(budget_dict)
            revenue += calculate_revenue_balance(temp_budget, bid_dict, queries)
        final_revenue = revenue/100
    elif input_algorithm == "msvv":
        temp_budget = deepcopy(budget_dict)
        print("Revenue: ",round(calculate_revenue_msvv(temp_budget, budget_dict, bid_dict, queries),2))
        for i in range(100):
            random.shuffle(queries)
            temp_budget = deepcopy(budget_dict)
            revenue += calculate_revenue_msvv(temp_budget, budget_dict, bid_dict, queries)
        final_revenue = revenue/100
    else:
        print("Invalid Input")
    
    # print(round(final_revenue,2))
    print("Competitive  Ratio:",round(final_revenue/sum(budget_dict.values()),2))
    
