import math

def g_k(k, C_S, lambda_m: float, LT: int, C_H: float =0.55):
    """
    Holding and shortage cost calculation
    
    Args:
        k: Inventory Position (IP), pallet
        C_S: Shortage Cost, CHF/pallet
        C_H: Holding Cost, CHF/(pallet·day)
        lambda_m: Average Material Consumption Rate, CHF/Order
        LT: Lead Time, day
        
    Returns:
        g: Holding and Shortage Cost
    """
    mu = lambda_m * LT  # Mean demand during lead time
    total = 0.0
    if k > 0:
        for d in range(0, k):  # d from 0 to k-1
            p = (mu**d) * math.exp(-mu) / math.factorial(d)
            total += (k - d) * p
            
    # Cost calculation (handles all integer k, including negatives)
    g = (C_H + C_S) * total - C_S * (k - mu)
    return g


def R_Q_policy(C_O, C_S, lambda_m: float, LT: int, C_H: float =0.55):
    """
    Optimal (R,Q) policy calculation
    
    Args:
        C_O: Ordering cost, CHF/order
        C_S: Shortage Cost, CHF/pallet
        C_H: Holding Cost, CHF/(pallet·day)
        lambda_m: Average Material Consumption Rate, CHF/Order
        LT: Lead Time, day
        
    Returns:
        R: Reorder point 
        Q: Reorder quantity
    """

    # Grid search for optimal k*
    k=1
    while k<10000:
        if g_k(k, C_S, lambda_m, LT, C_H) >= g_k(k+1, C_S, lambda_m, LT, C_H):
            k+=1
        else:
            break
    k_min=k

    if g_k(k_min, C_S, lambda_m, LT, C_H)<=0:
        return print("Error: Negative cost g(k)!")

    # Initialization
    R=k_min -1 # R(1)
    Q=1 
    CQ=C_O*lambda_m+g_k(k_min, C_S, lambda_m, LT, C_H) # C(1)

    C_next=CQ*Q/(Q+1)+1/(Q+1)*min(
                                  g_k(R, C_S, lambda_m, LT, C_H),
                                  g_k(R + Q + 1, C_S, lambda_m, LT, C_H)
                                )    # C(Q+1)=C(2)

    # Iteratively improve Q
    max_iter = 1000
    sign=False
    for _ in range(max_iter):
        if C_next>CQ:
            sign=True
            break
        
        # Increase order quantity
        Q += 1

        # Adjust reorder point
        if g_k(R, C_S, lambda_m, LT, C_H) < g_k(R + Q, C_S, lambda_m, LT, C_H):
            R -= 1

        # Update costs
        CQ = C_next
        C_next = CQ * (Q/(Q+1)) + (1/(Q+1)) * min(
                                                  g_k(R, C_S, lambda_m, LT, C_H),
                                                  g_k(R + Q + 1, C_S, lambda_m, LT, C_H)
                                                )
    if sign==False:
        print("Warning: Max iterations reached")

    return R,Q

if  __name__=="__main__":
    # Input parameters
    '''
    # Example: ABS1
    C_O = 79.18     # CHF/order
    C_S = 1032.81   # CHF/pallet (profit-based)
    lambda_m = 0.07 # pallet/day
    LT = 15         # days
    C_H = 0.55     # CHF/(pallet·day)

    Output: R = 4, Q = 5
    '''
    
    C_O = [79.18, 72.2, 84.06, 76.8,
            81.24, 74.03, 77.83, 74.75,
            78.67, 74.78, 94.47, 109.89,
            73.09, 66.87, 50.27, 50.18,
            50.36, 49.82, 46.17,49.73] # CHF/order
    C_S = [1032.81, 382.47, 238.14, 352.73,
            1053.06, 500.78, 369.68, 345.41,
            3243.73,990.82,282.71,354.01,
            633.07,519.06,272.62,104.89,
            243.17,192.39,431.31,999.30] # CHF/pallet (profit-based)
    lambda_m = [0.07, 0.23, 0.57, 0.20,
                0.07, 0.09, 0.14, 0.16,
                0.02, 0.07, 0.30, 0.27,
                0.09, 0.12, 0.19, 1.26,
                0.22, 0.32, 0.10, 0.04]
 # pallet/day
    LT = [15, 15, 15, 15, 
          15, 15, 15, 15,
          15, 15, 10, 10,
          20, 20, 10, 10,
          10, 10, 10, 10]        # days
    C_H = 0.55     # CHF/(pallet·day)

    Material = ["ABS1", "ABS2", "PC","PCA", 
                "POM1","POM2", "POM3", "POM4", 
                "TPE1", "TPE2", "METAL1", "METAL2", 
                "W1", "W2", "PACK1", "PACK2", 
                "PACK3", "PACK4", "PACK5", "PACK6"]
    

    # Compute optimal policy
    # R, Q = R_Q_policy(C_O, C_S, lambda_m, LT, C_H)
    # print(f"Optimal R = {R}, Q = {Q}")
    for i in range (len(C_O)):
        R, Q = R_Q_policy(C_O[i], C_S[i], lambda_m[i], LT[i], C_H)
        print(f"Material {Material[i]}: Optimal R = {R}, Q = {Q}")

    