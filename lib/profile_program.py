# profile the qiskit functions called during th eexecution of a program

import cProfile
import pstats

def profile_program(circuit, backend, shots=1024):
    """Run the program and return results and called functions."""
    cProfile.run('my_job = execute(circuit, backend)', 'c_profile_result')
    result = my_job.result()
    out_dict = result.get_counts()
    c_profile_result = pstats.Stats('c_profile_result')
    return out_dict, c_profile_result