import math
from typing import List, Tuple

def lcm(a: int, b: int) -> int:
    """Compute the Least Common Multiple of two integers."""
    return abs(a * b) // math.gcd(a, b) if a and b else 0

def lcm_of_list(nums: List[int]) -> int:
    """Compute the LCM of a list of integers."""
    if not nums:
        return 1
    current_lcm = nums[0]
    for num in nums[1:]:
        current_lcm = lcm(current_lcm, num)
    return current_lcm

def compute_inventory_profile(m_i: int, d_i: float, f_i: int, M: int) -> List[float]:
    """Compute inventory profile for an item over M periods."""
    return [d_i * (m_i - ((t - f_i) % m_i)) for t in range(1, M+1)]

def staggering_algorithm(m: List[int], d: List[float], T_max: int = 10000) -> Tuple[List[int], float]:
    """
    Heuristic algorithm for minimizing peak warehouse capacity in multi-item inventory scheduling.
    
    Args:
        m: List of cycle multipliers for each item
        d: List of demand rates per period for each item
        T_max: Maximum simulation period length (default=10000)
        
    Returns:
        schedules: Optimal starting periods for each item
        H: Minimum peak warehouse capacity
    """
    N = len(m)
    # 1. Determine global cycle length M
    M_cycle = lcm_of_list(m)
    M = M_cycle if M_cycle <= T_max else T_max
    
    # 2. Initialize data structures
    schedules = [0] * N
    contributions = [None] * N
    total_inv = [0.0] * M
    
    # 3. Sort items by lot size (m_i * d_i) ascending
    items = [(i, m[i], d[i]) for i in range(N)]
    items.sort(key=lambda x: x[1]*x[2])
    
    # 4. Process first item (smallest lot size)
    idx0, m0, d0 = items[0]
    schedules[idx0] = 1
    contributions[idx0] = compute_inventory_profile(m0, d0, 1, M)
    total_inv = contributions[idx0][:]
    
    # 5. Sequentially schedule remaining items
    for j in range(1, len(items)):
        i, m_i, d_i = items[j]
        base = total_inv[:]  # Current inventory without new item
        best_peak = float('inf')
        best_f = None
        best_contribution = None
        
        # Evaluate all possible starting periods
        for f in range(1, m_i + 1):
            candidate_contrib = compute_inventory_profile(m_i, d_i, f, M)
            candidate_total = [base[t] + candidate_contrib[t] for t in range(M)]
            peak_candidate = max(candidate_total)
            
            if peak_candidate < best_peak:
                best_peak = peak_candidate
                best_f = f
                best_contribution = candidate_contrib
        
        # Commit best schedule for this item
        schedules[i] = best_f
        contributions[i] = best_contribution
        total_inv = [base[t] + best_contribution[t] for t in range(M)]
    
    # 6. Improvement phase
    improved = True
    while improved:
        improved = False
        current_peak = max(total_inv)
        
        for idx, m_i, d_i in items:
            current_f = schedules[idx]
            base = [total_inv[t] - contributions[idx][t] for t in range(M)]
            best_f = current_f
            best_contribution = contributions[idx]
            
            # Test alternative starting periods
            for f in range(1, m_i + 1):
                if f == current_f:
                    continue
                
                candidate_contrib = compute_inventory_profile(m_i, d_i, f, M)
                candidate_total = [base[t] + candidate_contrib[t] for t in range(M)]
                peak_candidate = max(candidate_total)
                
                if peak_candidate < current_peak:
                    current_peak = peak_candidate
                    best_f = f
                    best_contribution = candidate_contrib
                    improved = True
            
            # Update if improvement found
            if best_f != current_f:
                schedules[idx] = best_f
                contributions[idx] = best_contribution
                total_inv = [base[t] + best_contribution[t] for t in range(M)]
    
    # 7. Final peak calculation
    H = max(total_inv)
    H = math.ceil(round(H,1))
    return schedules, H

# Example Usage
if __name__ == "__main__":
    m = [2,1,1,1,2,2,1,1,3,2,1,1,2,2,2,1,2,2,3,5]  # Cycle multipliers
    d = [0.07,0.23,0.57,0.20,0.07,0.09,0.14,0.16,0.02,0.07,0.30,0.27,0.09,0.12,0.19,1.26,0.22,0.32,0.10,0.04]  # Demand rates (units per time unit)
    
    # Run algorithm
    schedules, H = staggering_algorithm(m, d)
    
    # Output results
    print(f"Optimal Peak Inventory (H_m) = {H:.2f}")
    print("\nReplenishment Schedules:")
    for i, (m_i, d_i) in enumerate(zip(m, d)):
        print(f"Material {i}: cycle={m_i}, demand={d_i}, start period={schedules[i]}")
