# Abel Kahsai
# June 19, 2025

# define order_size, venues, lambda_over, lambda_under, theta_queue
def allocate(order_size, venues, lambda_over, lambda_under, theta_queue):
    """Implement Cont-Kukanov allocation strategy"""
    step = 100 #Search in 100-share chunks
    splits = [[]] #Start with empty allocation

    # Make all possible split outcomes
    for venue in venues:
        new_splits = []
        for alloc in splits:
            used = sum(alloc)
            max_v = min(order_size - used, venue['ask_size'])
            for q in range(0, max_v + 1, step):
                new_splits.append(alloc + [q])
        splits = new_splits

    # Find best split
    best_cost = float('inf')
    best_split = []

    for alloc in splits:
        if sum(alloc) != order_size:
            continue
        cost = compute_cost(alloc, venues, order_size, lambda_over, lambda_under, theta_queue)

        if cost < best_cost:
            best_cost = cost
            best_split = alloc
    return best_split, best_cost

# define compute_cost
def compute_cost(split, venues, order_size, lambda_o, lambda_u, theta):
    """Compute total cost for a given split"""
    executed = 0
    cash_spent = 0

    for i in range(len(venues)):
        exe = min(split[i], venues[i]['ask_size'])
        executed += exe
        cash_spent += exe * (venues[i]['ask'] + venues[i]['fee'])

        # Maker rebate for unfilled orders
        maker_rebate = max(split[i] - exe, 0) * venues[i]['rebate']
        cash_spent -= maker_rebate
        
    # underfill, overfill, risk_pen, cost_pen
    underfill = max(order_size - executed, 0)
    overfill = max(executed - order_size, 0)
    risk_pen = theta * (underfill + overfill)
    cost_pen = lambda_u * underfill + lambda_o * overfill
    
    return cash_spent + risk_pen + cost_pen