#!/usr/bin/env python3

import gurobipy as g
import numpy as np
import sys
import math

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file) as fin:
    grid = fin.readline().split()
    n_people = int(grid[0])  # pocet lidi
    n_payments = int(grid[1])  # pocet plateb
    payments_line = [int(a) for a in fin.readline().split()]
    people_payments_line = [int(a) for a in fin.readline().split()]

paid_by_person_array = [0] * n_people
sum_price = 0
for a in range(n_payments):
    sum_price += payments_line[a]
    paid_by_person_array[people_payments_line[a] - 1] += payments_line[a]

target_payment_by_person = sum_price / n_people

model = g.Model()

# kdo X komu Y
is_paid_matrix = [[0] * n_people for a in range(n_people)]  # matice kdo komu platil
payments_matrix = [[0] * n_people for a in range(n_people)]  # matice kdo komu kolik platil

for a in range(n_people):
    for b in range(n_people):
        is_paid_matrix[a][b] = model.addVar(vtype=g.GRB.BINARY, lb=0)
        payments_matrix[a][b] = model.addVar(vtype=g.GRB.CONTINUOUS, lb=0)

model.update()
# chci nejmensi pocet presunu castek mezi lidmi
model.setObjective(g.quicksum([is_paid_matrix[a][b] for a in range(n_people) for b in range(n_people)]),
                   sense=g.GRB.MINIMIZE)

for a in range(n_people):
    # pro kazdou sobu bude platit ze to co ma zaplatit se musi rovnat tomu co zaplatil - co prijmul+ co dal ostatnim
    # model.addConstr(paid_by_person_array[a] - g.quicksum([payments_matrix[b][a] for b in range(n_people)]) + g.quicksum([payments_matrix[a][b] for b in range(n_people)]) == target_payment_by_person)
    if paid_by_person_array[a] >= target_payment_by_person:
        model.addConstr(paid_by_person_array[a] - g.quicksum(
            [payments_matrix[b][a] for b in range(n_people)]) == target_payment_by_person)
    if paid_by_person_array[a] < target_payment_by_person:
        model.addConstr(paid_by_person_array[a] + g.quicksum(
            [payments_matrix[a][b] for b in range(n_people)]) == target_payment_by_person)

for a in range(n_people):
    for b in range(n_people):
        model.addConstr(payments_matrix[a][b] <= (100000 + sum_price) * is_paid_matrix[a][b])

model.optimize()

if model.Status == g.GRB.OPTIMAL:
    with open(output_file, 'w+') as fout:
        fout.write(str(int(model.objVal)) + "\n")
        for a in range(n_people):
            for b in range(n_people):
                if is_paid_matrix[a][b].x > 0.5:
                    fout.write(str(a + 1) + " " + str(b + 1) + " " + str(round(payments_matrix[a][b].x, 2)) + "\n")
