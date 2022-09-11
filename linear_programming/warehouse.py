from pulp import *
import numpy as np
from linear_programming.custom_lp_problem import CustomLpProblem


class WarehouseProblem(CustomLpProblem):
    def __init__(self, name: str = 'No name',
                 sense=const.LpMinimize, **kwargs):

        super().__init__(name=name, sense=sense)
        self._warehouse_supply = None
        self._cost_demands = None

    @property
    def n_warehouses(self) -> int:
        return self.n_vars_dependents

    @n_warehouses.setter
    def n_warehouses(self, n_warehouses: int):
        self.n_vars_dependents = n_warehouses

    @property
    def n_customers(self) -> int:
        return self.n_vars_independents

    @n_customers.setter
    def n_customers(self, n_customers: int):
        self.n_vars_independents = n_customers

    @property
    def warehouse_supply(self):
        return self._warehouse_supply

    @warehouse_supply.setter
    def warehouse_supply(self, matrix: np.ndarray):
        _w,  = matrix.shape

        assert _w == self.n_warehouses, 'Error cost matriz definition'

        self._warehouse_supply = matrix

    @property
    def cost_demands(self):
        return self._cost_demands

    @cost_demands.setter
    def cost_demands(self, matrix: np.ndarray):
        self._cost_demands = matrix

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
            except Exception as e:
                print("error couldnt find value")

        for i in range(self.n_warehouses):
            print("Warehouse ", str(i + 1))
            print(lpSum(self.allocation[i][j].value() for j in range(self.n_customers)))


if __name__ == '__main__':
    model = WarehouseProblem(name='Problem-01:_Supplied_warehouses',
                             sense='minimize')
    model.n_customers = 4
    model.n_warehouses = 2
    model.cost_matrix = np.array([[1, 3, 0.5, 4],
                                  [2.5, 5, 1.5, 2.5]])
    model.cost_demands = np.array([35000, 22000, 18000, 30000])
    model.warehouse_supply = np.array([60000, 80000])
    model.define_fun_obj()

    model.add_constraints()

    model.writeLP("Supply_demand_prob.lp")
    model.solve(PULP_CBC_CMD())

    status = LpStatus[model.status]

    print(model)

    print('\n\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    model.result()
