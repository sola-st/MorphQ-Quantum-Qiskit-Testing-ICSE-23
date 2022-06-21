from lib.utils import load_config_and_check
from lib.mr import ChangeQubitOrder
from lib.qmt import execute_single_py_program
from lib.utils import break_function_with_timeout


def main():
    my_path = "data/qmt_v24/programs/followup/828b24cfdfc8460cb217597bc8ada1f6.py"
    break_function_with_timeout(
        routine=execute_single_py_program,
        seconds_to_wait=120,
        message="Change 'budget_time_per_program_couple'" +
                " in config yaml file.",
        args=(my_path,)
    )


main()