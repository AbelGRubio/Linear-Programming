from pulp import *
import pandas as pd
import numpy as np


class CustomLpProblem(LpProblem):
    def __init__(self, name: str = 'No name',
                 sense=const.LpMinimize, **kwargs):
        self.problem_type = f'{LpMinimize=}'.split('=')[0]
        super().__init__(name=name, sense=sense)
        self.variable_names = []
        self._warehouses = 0
        self._customers = 0
        self._cost_matrix = np.zeros((1, 1))
        self._cost_demands = np.zeros((1, 1))
        self._warehouse_supply = np.zeros((1, 1))
        self.DV_variables = None
        self.allocation = None
        self.obj_fun = None

    @property
    def n_warehouses(self) -> int:
        return self._warehouses

    @n_warehouses.setter
    def n_warehouses(self, n_warehouses: int) -> None:
        self._warehouses = n_warehouses
        self._define_variables_name()

    @property
    def n_customers(self) -> int:
        return self._customers

    @n_customers.setter
    def n_customers(self, n_customers: int) -> None:
        self._customers = n_customers
        self._define_variables_name()

    def _define_variables_name(self):
        self.variable_names = [str(i) + str(j) for j in range(1, self._customers + 1)
                               for i in range(1, self._warehouses + 1)]
        self.variable_names.sort()
        print("Variable Indices:", self.variable_names)
        self._define_dv_variables()

    @property
    def cost_matrix(self):
        return self._cost_matrix

    @cost_matrix.setter
    def cost_matrix(self, matrix: np.ndarray):
        _w, _c = matrix.shape

        assert _w == self.n_warehouses and _c == self.n_customers, 'Error cost matriz definition'

        self._cost_matrix = matrix
        self.define_fun_obj()

    @property
    def cost_demands(self):
        return self._cost_demands

    @cost_demands.setter
    def cost_demands(self, matrix: np.ndarray):
        self._cost_demands = matrix
        self._add_demand_constraints()

    @property
    def warehouse_supply(self):
        return self._cost_demands

    @warehouse_supply.setter
    def warehouse_supply(self, matrix: np.ndarray):
        _w,  = matrix.shape

        assert _w == self.n_warehouses, 'Error cost matriz definition'

        self._warehouse_supply = matrix
        self._add_supply_constraints()

    def _define_dv_variables(self):
        if self.n_warehouses > 0 and self.n_customers > 0:
            self.DV_variables = LpVariable.matrix("X", self.variable_names, cat="Integer", lowBound=0)
            self.allocation = np.array(self.DV_variables).reshape(self.n_warehouses, self.n_customers)
            print("Decision Variable/Allocation Matrix: ")
            print(self.allocation)

    def define_fun_obj(self):
        self.obj_fun = lpSum(self.allocation * self._cost_matrix)
        self += self.obj_fun
        return self.obj_fun

    def _add_supply_constraints(self):
        for i in range(self.n_warehouses):
            value = lpSum(self.allocation[i][j] for j in range(self.n_customers)) <= self._warehouse_supply[i]
            print(value)
            self += value, "Supply_Constraints_" + str(i)

    def _add_demand_constraints(self):
        for j in range(self.n_customers):
            value = lpSum(self.allocation[i][j] for i in range(self.n_warehouses)) >= self._cost_demands[j]
            print(value)
            self += value, "Demand_Constraints_" + str(j)

    def add_constraints(self):
        self._add_demand_constraints()
        self._add_supply_constraints()

    def result(self):
        print("Result problem: ")
        print("Total Cost:", self.objective.value())
        for v in self.variables():
            try:
                print(v.name, "=", v.value())
            except:
                print("error couldnt find value")

        for i in range(self.n_warehouses):
            print("Warehouse ", str(i + 1))
            print(lpSum(self.allocation[i][j].value() for j in range(self.n_customers)))


if __name__ == '__main__':
    model = CustomLpProblem(name='Problem-01:_Supplied_warehouses',
                            sense=LpMinimize)
    model.n_customers = 4
    model.n_warehouses = 2
    model.cost_matrix = np.array([[1, 3, 0.5, 4],
                                  [2.5, 5, 1.5, 2.5]])
    model.cost_demands = np.array([35000, 22000, 18000, 30000])
    model.warehouse_supply = np.array([60000, 80000])

    model.writeLP("Supply_demand_prob.lp")
    model.solve(PULP_CBC_CMD())
    status = LpStatus[model.status]

    # print(status)
    print("Total Cost:", model.objective.value())

    print('\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    model.result()
    f = 1
    pass