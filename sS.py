import math

def g_k(k, C_h, C_s, lambda_m: float, LT: int = 1):
    """
    Holding and shortage cost calculation
    
    Args:
        k: Inventory Position (IP), pallet
        C_s: Shortage Cost, CHF/pallet
        C_h: Holding Cost, CHF/(pallet·day)
        lambda_m: Average Material Consumption Rate, pallet/day
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
    g = (C_h + C_s) * total - C_s * (k - mu)
    return g

def Inventory_Position_Expected_Visits(s, S, mu):
    m_vals = {S: 1}  # Store m_k for k in [s+1, S]
    
    # Compute from high k to low k (S-1 downto s+1)
    for k in range(S-1, s, -1):
        total = 0
        for i in range(k+1, S+1):
            d = i - k
            prob = (mu**d) * math.exp(-mu) / math.factorial(d)
            total += m_vals[i] * prob
        m_vals[k] = total
    
    return m_vals

def compute_prob_dist(m_vals, s, S):
    IP_prob={} # Store inventory distribution
    M = sum(m_vals[k] for k in range(s+1, S+1))
    for k in range(s+1, S+1): # k=s+1, s+2, ..., S
        IP_prob[k]=m_vals[k] / M
    return IP_prob

def s_S_policy_cost(s, S, C_h, C_s, lambda_m: float, LT: int = 1, C_T: float=30):
    m_vals = Inventory_Position_Expected_Visits(s, S, lambda_m*LT)
    IP_prob_dist = compute_prob_dist(m_vals, s, S)
    M = sum(m_vals.values())
    holding_shortage_total = 0
    for k in range(s+1, S+1):
        holding_shortage_total+=IP_prob_dist[k]*g_k(k, C_h, C_s, lambda_m, LT)
    Cost = C_T * lambda_m / M + holding_shortage_total
    return Cost

def s_S_policy(C_h, C_s, lambda_m: float, LT: int = 1, C_T: float=30, max_k=100, max_S=200):
    """
    Optimal (s,S) policy calculation
    
    Args:
        C_T: Delivery cost, CHF/delivery
        C_s: Onsite Shortage Cost, CHF/pallet
        C_h: Internal Holding Cost, CHF/(pallet·day)
        lambda_m: Average Material Consumption Rate, pallet/day
        LT: Delivery Lead Time, day
        
    Returns:
        s: Reorder inventory position 
        S: Order-up-to inventory position
    """
    # Step 1: 
    # Grid search for optimal k*
    k=1
    while k<max_k:
        if g_k(k, C_h, C_s, lambda_m, LT) >= g_k(k+1, C_h, C_s, lambda_m, LT):
            k+=1
        else:
            break
    if k>=max_k:
        raise RuntimeError(f"k_min not found in range (1, {max_k})")
    k_min=k
    
    S_opt= k_min
    s = S_opt - 1

    # try s = S∗ − 1 , s = S∗ − 2 , ... until C(s, S*)<=g(s)
    while s_S_policy_cost(s, S_opt, C_h, C_s, lambda_m)> g_k(s, C_h, C_s, lambda_m) and s>0:
        s-=1
    s_opt = s
    C_opt=s_S_policy_cost(s_opt, S_opt, C_h, C_s, lambda_m)

    # Step 2: 
    S = S_opt + 1
    while S<=max_S:
        # Terminal Condition (Step): 
        if g_k(S, C_h, C_s, lambda_m) > C_opt: 
            return s_opt, S_opt
        # Step 3: Check if policy improves
        elif s_S_policy_cost(s_opt, S, C_h, C_s, lambda_m) < C_opt:
            S_opt = S
            # Step 4: 
            s = s_opt
            while s_S_policy_cost(s, S_opt, C_h, C_s, lambda_m) <= g_k(s+1, C_h, C_s, lambda_m) and s < S_opt:
                s = s + 1
            s_opt = s
            C_opt=s_S_policy_cost(s_opt, S_opt, C_h, C_s, lambda_m)
        # Else: Go back to step 2
        S += 1
    else: 
        raise RuntimeError("max_S exhausted")


if  __name__=="__main__":
    '''
    C_h=5.14
    C_s=238.14
    lambda_m=0.57
    s, S=s_S_policy(C_h, C_s, lambda_m)
    print(f"Optimal s = {s}, S = {S}")
    '''
    C_h = [5.14, 5.14, 5.14, 5.14, 
           5.14, 5.14, 5.14, 5.14, 
           5.14, 5.14, 8.56, 8.56,
           3.42, 3.42, 1.37, 1.37,
           1.37, 1.37, 1.37, 1.37]
    
    C_s = [121.87, 36.56, 14.94, 31.67, 
           124.16, 51.96, 33.72, 31.10, 
           416.76, 117.15, 28.20, 17.75, 
           52.34, 41.88, 39.44, 5.92,
           33.53, 23.53, 72.41, 184.94]

    lambda_m = [0.07, 0.23, 0.57, 0.20,
                0.07, 0.09, 0.14, 0.16,
                0.02, 0.07, 0.30, 0.27,
                0.09, 0.12, 0.19, 1.26,
                0.22, 0.32, 0.10, 0.04]
    
    Material = ["ABS1", "ABS2", "PC","PCA", 
                "POM1","POM2", "POM3", "POM4", 
                "TPE1", "TPE2", "METAL1", "METAL2", 
                "W1", "W2", "PACK1", "PACK2", 
                "PACK3", "PACK4", "PACK5", "PACK6"]
    
    for i in range (len(C_h)):
        s, S = s_S_policy(C_h[i], C_s[i], lambda_m[i])
        print(f"Material {Material[i]}: Optimal s = {s}, S = {S}")

    s, S = s_S_policy(0.86, 8.244, 10.40, 1, 31.82)
    print(f"Material FGT1: Optimal s = {s}, S = {S}")

    s, S = s_S_policy(0.86, 9.874, 4.89, 1, 29.52)
    print(f"Material FGT2: Optimal s = {s}, S = {S}")
