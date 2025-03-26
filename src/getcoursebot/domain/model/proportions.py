from dataclasses import dataclass
from enum import Enum
from decimal import Decimal as D


class TargetProcent(Enum):
    FAST_SLIM = D("-0.8")
    FLUENTLY_SLIM = D("-0.9")
    DEFAULT = D("1")
    FLUENTLY_SET = D("1.1")
    FAST_SET = D("1.2")

    def is_slim(self) -> bool:
        return self in [
            TargetProcent.FAST_SLIM, 
            TargetProcent.FLUENTLY_SLIM
        ]
    
    def is_set(self) -> bool:
        return self in [
            TargetProcent.FLUENTLY_SET, 
            TargetProcent.FAST_SET
        ]
    
    def is_default(self) -> bool:
        return self == TargetProcent.DEFAULT


class СoefficientActivity(Enum):
    MIN_A = D("1.2")
    LOW_A = D("1.375")
    MEDIUM_A = D("1.55")
    HIGH_A = D("1.725")
    DEFAULT_A = D("1")


@dataclass
class KBJU:
    b: D
    j: D
    u: D


@dataclass
class Proportions:
    age: int
    height: int
    weight: int
    coefficient: СoefficientActivity
    target_procent: TargetProcent

    def calculate_kkal(self) -> D:
        x = D(self.target_procent)
        normal_kkal = D(D("10") * self.weight + D("6.25") * self.height - D("5") * self.age - D("161")) * D(self.coefficient)
        # if x == D("-20") or x == D("-10"):
        #     value_procent = normal_kkal*(x)
        # elif x == D("20") or x == D("10"):
        #     value_procent = normal_kkal*(x)
        # else:
        #     # print(normal_kkal, "n2")
        #     # print(value_procent, 'B2')
        #     value_procent = D("0")
        val = normal_kkal * x
        x = abs(val)
        if x < 1200:
            x = D("1200")

        return x.quantize(D("1"))
    
    def calculate_kbju(self):
        b = D(str(D("1.5")*self.weight)).quantize(D("1"))
        j = D(self.weight).quantize(D("1"))
        return KBJU(
            b,
            j,
            abs(D(str((self.calculate_kkal()-D("100")-(j*D("9"))-(b*D("4")))/D("4"))).quantize(D("1")))
        )