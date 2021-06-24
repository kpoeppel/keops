from keops.python_engine.formulas.VectorizedScalarOp import VectorizedScalarOp
from keops.python_engine.utils.math_functions import keops_log

class Log(VectorizedScalarOp):

    """the logarithm vectorized operation"""

    string_id = "Log"
    
    ScalarOpFun = keops_log
    
    @staticmethod
    def Derivative(f):  
        return 1/f