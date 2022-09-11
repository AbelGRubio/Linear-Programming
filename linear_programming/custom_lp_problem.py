from pulp import *
import numpy as np


class CustomLpProblem(LpProblem):
    def __init__(self, name: str = 'No name',
                 sense: str = 'minimize', **kwargs):

        sense_ = const.LpMaximize

        if sense == 'minimize':
            sense_ = const.LpMinimize

        name = name.replace(' ', '_')

        self.problem_type = f'{sense=}'.split('=')[0]
        super().__init__(name=name, sense=sense_)
        self.variable_names = None
        self._n_vars_dependents = 0
        self.name_vars_dependents = []
        self._n_vars_independents = 0
        self.name_vars_independents = []
        self._cost_matrix = None
        self._cost_constrains = None
        self._signs_constrains = None
        self.DV_variables = None
        self.allocation = None
        self._obj_fun = None

    @property
    def n_vars_dependents(self) -> int:
        return self._n_vars_dependents

    @n_vars_dependents.setter
    def n_vars_dependents(self, n_vars_dependents: int) -> None:
        self._n_vars_dependents = n_vars_dependents
        if self._n_vars_dependents > 0:
            numbers = [_n for _n in range(1, self._n_vars_dependents + 1)]
            self.name_vars_dependents = LpVariable.matrix("Y", numbers,
                                                          cat="Integer",
                                                          lowBound=0)
            print(f'Dependent variables names created {self.name_vars_dependents}')
            self._define_cost_matrix_vars()

    @property
    def n_vars_independents(self) -> int:
        return self._n_vars_independents

    @n_vars_independents.setter
    def n_vars_independents(self, n_vars_independents: int) -> None:
        self._n_vars_independents = n_vars_independents
        if self._n_vars_independents > 0:
            numbers = [_n for _n in range(1, self._n_vars_independents + 1)]
            self.name_vars_independents = LpVariable.matrix("X", numbers,
                                                            cat="Integer",
                                                            lowBound=0)
            print(f'Independent variables names created {self.name_vars_independents}')
            self._define_cost_matrix_vars()

    @property
    def cost_matrix(self):
        return self._cost_matrix

    @cost_matrix.setter
    def cost_matrix(self, matrix: np.ndarray):
        _nvd, _nvi = matrix.shape

        assert _nvi == self._n_vars_independents and _nvd == self._n_vars_dependents, 'Error cost matrix definition'

        self._cost_matrix = matrix

    @property
    def cost_constrains(self):
        return self._cost_constrains

    @cost_constrains.setter
    def cost_constrains(self, cost_constrains_matrix: np.ndarray):
        self._cost_constrains = cost_constrains_matrix

    @property
    def signs_constrains(self):
        return self._signs_constrains

    @signs_constrains.setter
    def signs_constrains(self, sings: str):
        if len(sings) == self._cost_constrains.shape[0]:
            self._signs_constrains = sings
            print(f'Signs constrains defined {self._signs_constrains}')

    @property
    def fun_obj(self):
        return self._obj_fun

    @fun_obj.setter
    def fun_obj(self, fun: lpSum or lpDot):
        print(f'Defined objective function: {fun}')
        self._obj_fun = fun
        self += self._obj_fun

    def _define_cost_matrix_vars(self):
        if self._n_vars_dependents > 0 and self._n_vars_independents > 0:
            self.variable_names = [str(i) + str(j) for j in range(1, self._n_vars_independents + 1)
                                   for i in range(1, self._n_vars_dependents + 1)]
            self.variable_names.sort()
            print("Variable Indices:", self.variable_names)

    def _define_dv_variables(self):
        if self._n_vars_dependents > 0 and self._n_vars_independents > 0:
            self.DV_variables = LpVariable.matrix("Z", self.variable_names,
                                                  cat="Integer", lowBound=0)
            self.allocation = np.array(self.DV_variables).reshape(self._n_vars_dependents,
                                                                  self._n_vars_independents)
            print("Decision Variable/Allocation Matrix: ")
            print(self.allocation)

    def _add_constraints(self):
        for n, i, v, m in zip(
                range(1, len(self.signs_constrains) + 1),
                self.signs_constrains,
                self.cost_constrains,
                self.cost_matrix.transpose()):
            print(m * self.name_vars_dependents, i, v)
            value = lpSum(m * self.name_vars_dependents) >= v
            self += value, f'Constrain_{n}'

    def define_fun_obj(self):
        self._define_dv_variables()
        self._obj_fun = lpSum(self.allocation * self._cost_matrix)
        self += self._obj_fun
        return self._obj_fun

    def add_constraints(self):
        self._add_constraints()

    def result(self):
        print("Result problem: ")
        print("Total Cost:", self.objective.value())
        for v in self.variables():
            try:
                print(v.name, "=", v.value())
            except Exception as e:
                print(f"error couldnt find value {e}")

        if self.allocation:
            for i in range(self._n_vars_dependents):
                print("Var dependent ", str(i + 1))
                print(lpSum(self.allocation[i][j].value() for j in range(self._n_vars_independents)))

