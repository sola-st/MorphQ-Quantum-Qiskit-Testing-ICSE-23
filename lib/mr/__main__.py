from lib.utils import load_config_and_check
from lib.mr import ChangeQubitOrder


def main():
    config = load_config_and_check("config/qmt_v08.yaml")
    mr = ChangeQubitOrder(
        "prova", code_of_source="FAKE CODE",
        metamorphic_strategies_config=config["metamorphic_strategies"],
        detectors_config=config["detectors"])
    print(mr)


main()