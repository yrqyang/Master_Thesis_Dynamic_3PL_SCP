from pyomo.environ import *
import math
from pyomo.opt import SolverFactory, SolverManagerFactory
import os
os.environ['NEOS_EMAIL'] = 'yanruiqi.yang@epfl.ch'

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b) if a and b else 0

def lcm_of_list(nums):
    if not nums:
        return 1
    current_lcm = nums[0]
    for num in nums[1:]:
        current_lcm = lcm(current_lcm, num)
    return current_lcm

# Example data
'''N = 5  # Number of materials
m = [2, 3, 4, 5, 6]  # Cycle multipliers
d = [10, 20, 15, 30, 25]  # Demand rates (units per time unit)
T_B = 1  # Base cycle time
D = [d_i * T_B for d_i in d]  # Demand per period'''
# External 
N = 22  # Number of materials
m = [64,33,23,37,65,54,44,42,118,61,34,38,54,46,3,4,31,12,29,24,40,67]  # Cycle multipliers
d = [0.07,0.23,0.57,0.20,0.07,0.09,0.14,0.16,0.02,0.07,0.30,0.27,0.09,0.12,10.40,4.89,0.19,1.26,0.22,0.32,0.10,0.04]  # Demand rates (units per time unit)
T_B = 1  # Base cycle time
D = [d_i * T_B for d_i in d]

# Calculate global cycle M = LCM(m_i)
M = lcm_of_list(m)

if M> 10000:
    M=10000  # Limit the maximum time horizon

# Precompute inventory contributions A[i, s, tau]
A = {}
for i in range(N):
    for s in range(1, m[i] + 1):  # Use m[i] not m(i)
        for tau in range(1, M + 1):
            r = (tau - s) % m[i]  # Time since last replenishment
            inv_val = D[i] * (m[i] - r)  # Inventory level
            A[i, s, tau] = inv_val

# Create Pyomo model
model = ConcreteModel()

# Sets
model.I = Set(initialize=range(N))  # Materials
model.T = Set(initialize=range(1, M + 1))  # Time periods

# Define index set for x variables
model.x_index = Set(initialize=[
    (i, s) for i in range(N) for s in range(1, m[i] + 1)
])

# Variables
model.H_m = Var(domain=NonNegativeReals)  # Peak inventory
model.x = Var(model.x_index, domain=Binary)  # Replenishment indicators

# Objective: Minimize peak inventory
model.obj = Objective(expr=model.H_m, sense=minimize)

# Constraints
# Each material has exactly one replenishment time
model.one_replenishment = ConstraintList()
for i in model.I:
    model.one_replenishment.add(
        sum(model.x[i, s] for s in range(1, m[i] + 1)) == 1
    )

# Total inventory at each time <= H_m
model.inventory_constraint = ConstraintList()
for tau in model.T:
    total_inv = 0
    for i in model.I:
        for s in range(1, m[i] + 1):
            total_inv += model.x[i, s] * A[i, s, tau]
    model.inventory_constraint.add(total_inv <= model.H_m)

solver_manager = SolverManagerFactory('neos', validate=False)

# Solve the model remotely on NEOS
results = solver_manager.solve(model, opt='couenne', tee=True)

# Load the solution into the model
model.solutions.load_from(results)

# Display results
print("Solution:\n")
# Output results
if results.solver.status == SolverStatus.ok:
    print("\nOptimal Solution is Found")
    print(f"Optimal Peak Inventory (H_m) = {model.H_m.value:.2f}")
    print("\nReplenishment Schedules:")
    for i in model.I:
        for s in range(1, m[i] + 1):
            if model.x[i, s].value > 0.5:  # Binary variable is 1
                print(f"Material {i}: replenished at time s = {s}")
else:
    print("No optimal solution found")