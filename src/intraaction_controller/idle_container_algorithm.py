import math
import sys
from math import factorial as fac

def power_over_fac(x, n):
    return x**n / fac(n)

def Qos_value_algorithm(lambd, n, mu, Qos_time):
    '''
    lambd: lambda, the interval obeys negative exponential distribution
    n: the number of containers in the serverless platform
    mu: the processing capacity of each container
    pi_k: the probability that there are k queries in the system
    
    Return:
    cal: the distribution function of the waiting time
    '''

    if mu == 0 or n == 0:
        return 0

    rou = lambd / (mu * n)
    nXrou = lambd / mu

    if rou >= 1:
        return 0
    
    pi_0 = 1 / (sum([power_over_fac(nXrou, k) for k in range(n)]) + power_over_fac(nXrou, n) / (1 - rou))
    pi_n = power_over_fac(nXrou, n) * pi_0

    e_index = -n*mu*(1 - rou)*Qos_time
    cal = 1 - pi_n / (1 - rou) * math.exp(e_index)
    return cal
    
def idle_status_check(lambd, n, mu, Qos_time, Qos_value_cal, Qos_value_requirement):
    '''
    Qos_time: the Qos target time required by action
    Qos_value_requirement: the Qos required by action
    Qos_value_cal: the Qos now reaching by action
    
    Return:
    idle_sign: marking whether the idle container exists  
    '''

    idle_sign = False
    if Qos_value_cal > Qos_value_requirement and n > 1:
        judge = Qos_value_algorithm(lambd, n - 1, mu, Qos_time)
        idle_sign = judge > Qos_value_requirement
        # if judge > Qos_value_requirement:
        #     idle_sign = True
        # else: idle_sign = False
    return idle_sign