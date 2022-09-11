from linear_programming import CustomLpProblem
import numpy as np
from pulp import lpSum, LpVariable, PULP_CBC_CMD, LpStatus

if __name__ == '__main__':

    """minimization problem"""
    problem_02 = CustomLpProblem(name='Refinery problem',
                                 sense='minimize')

    """vars independents = 3, gasoline, kerosene and jet fue """
    problem_02.n_vars_independents = 3

    """vars dependents = 2,  light crude oil, heavy crude oil """
    problem_02.n_vars_dependents = 2

    problem_02.cost_matrix = np.array([[0.4, 0.2, 0.35],
                                       [0.32, 0.4, 0.2]])

    problem_02.cost_constrains = np.array([1e6, 4e5, 25e4])
    problem_02.signs_constrains = ['>='] * 3

    problem_02.fun_obj = lpSum(np.array([11, 9]) * problem_02.name_vars_dependents)
    problem_02.add_constraints()
    problem_02.writeLP("problem_02.lp")
    problem_02.solve(PULP_CBC_CMD())

    status = LpStatus[problem_02.status]
    problem_02.result()
    f = 1
    pass

