def Wagner_Whitin_DP(D: list[float], K: float, h: float):
    """
    Wagner Whitin algorithm for optimal ordering if demand is deterministic varying
    
    Args:
        D: List of demand
        K: Fixed ordering cost, CHF/Order
        h: Unit holding cost, CHF/pallet
        
    Returns:
        F: List of total cost per time step
        orders_periods: Sequence of replenishment periods
        Q: Sequence of order quantities
    """
    # Initialize the data structures
    T=len(D)
    if T==0:
        return 0.0, []
    
    D_0=[0]+D

    # Precompute cost matrix L
    l = [[0.0] * (T + 1) for _ in range(T + 1)]

    for i in range(1, T + 1):
        l[i][i] = K + 0.5 * h * D_0[i]              # only that period’s demand; Holding Cost of current period:  + h * D_0[i]
        cost = 0.0                    # Holding Cost of current period:  h * D_0[i]
        for j in range(i + 1, T + 1):
            cost += h * (j - i) * D_0[j]
            l[i][j] = K + cost

    # DP initialization
    F = [0.0] + [float("inf")] * T          # F[0] = 0
    prev = [-1] * (T + 1)

    # Forward DP: F[t] = min_{0≤j<t} {F[j] + K + h*H[j+1][t] }
    for j in range(1, T + 1):
        # k = last period satisfied before the new order
        for i in range(0, j):
            # Order immediately after period k, i.e. in period k+1
            cost_candidate = F[i] + l[i + 1][j]
            if cost_candidate < F[j] - 1e-12:
                F[j] = cost_candidate
                prev[j] = i
            elif abs(cost_candidate - F[j]) <= 1e-12 and i < prev[j]:
                prev[j] = i

    # Backtrack optimal order periods
    orders = []
    t = T
    while t > 0:
        orders.append(prev[t])
        t = prev[t]  # Move to previous state
    orders.reverse()

    order_periods = [t + 1 for t in orders]   # 1‑indexed

    Q = []
    seg_ends = orders[1:] + [T]
    for start, end in zip(orders, seg_ends):
        Q.append(sum(D[start:end]))

    return F[T], order_periods, Q


if __name__=="__main__":
    # Example
    '''
    D=[10,20,25,30,35]
    K=100
    h=1
    '''

    # Numerical solution example
    '''
    D=[0.31, 0.62, 1.03, 1.23, 1.54] # Material demand in the first months
    K=79.18 # Ordering cost
    '''
    D=[0.09,	0.18,	0.30,	0.36,	0.45]
    K= 78.67
    h= 0.55*30 # monthly 

    '''
    D=[[0.31,	0.62,	1.03,	1.24,	1.55],
       [1.03,	2.06,	3.44,	4.13,	5.16],
       [2.52,	5.05,	8.41,	10.10,	12.62],
       [0.88,	1.76,	2.93,	3.51,	4.39],
       [0.30,	0.61,	1.01,	1.21,	1.52],
       [0.41,	0.82,	1.36,	1.63,	2.04],
       [0.63,	1.26,	2.10,	2.52,	3.15],
       [0.68,	1.36,	2.27,	2.73,	3.41],
       [0.09,	0.18,	0.30,	0.36,	0.45],
       [0.32,	0.64,	1.07,	1.29,	1.61],
       [1.34,	2.67,	4.46,	5.35,	6.69],
       [1.20,	2.39,	3.99,	4.78,	5.98],
       [0.41,	0.81,	1.35,	1.62,	2.03],
       [0.51,	1.01,	1.69,	2.03,	2.53],
       [45.74,	91.48,	152.46,	182.95,	228.69],
       [21.50,	42.99,	71.66,	85.99,	107.49],
       [0.83,	1.66,	2.77,	3.32,	4.15],
       [5.53,	11.06,	18.44,	22.13,	27.66],
       [0.98,	1.95,	3.26,	3.91,	4.89],
       [1.39,	2.78,	4.64,	5.57,	6.96],
       [0.45,	0.90,	1.51,	1.81,	2.26],
       [0.18,	0.35,	0.59,	0.71,	0.89]]

    K=[79.18, 72.20, 84.06, 76.80,
        81.24, 74.03, 77.83, 74.75,
        78.67, 74.78, 94.47, 109.89,
        73.09, 66.87, 31.82, 29.52,
        50.27, 50.18, 50.36, 49.82, 46.17, 49.73]
    
    Material = ["ABS1", "ABS2", "PC","PCA", 
                "POM1","POM2", "POM3", "POM4", 
                "TPE1", "TPE2", "METAL1", "METAL2", 
                "W1", "W2", "FGT1", "FGT2", 
                "PACK1", "PACK2", "PACK3", "PACK4", "PACK5", "PACK6"]
    '''

    total_cost, orders, Q = Wagner_Whitin_DP(D, K, h)
    print(f"Total Cost: {total_cost} CHF")
    print(f"Order Periods: {orders}")
    print(Q)

    '''
    for k in range(len(K)):
        total_cost, orders, Q = Wagner_Whitin_DP(D[k], K[k], h)
        print(total_cost)
    '''