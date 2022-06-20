"""
Generate Template Configuration File

Type: Command-Line Tool

"""
import os
import pathlib

import click
from termcolor import colored

from lib.utils import load_config_and_check


def show_available_templates():
    """
    Show available templates
    """
    print("Available Templates:")
    template_files = os.listdir("./config/template_files")
    only_basename_files = [os.path.basename(x) for x in template_files]
    for i, template in enumerate(only_basename_files):
        print(f"{i+1}. {template}")
    return template_files


def query_for_template(from_template):
    """Prompt the user for a template file if it was not provided.

    Note that the templates are in the folder: config/templates
    and they have a special {{VERSION}} field which get replaced.
    ."""
    if from_template is None:
        template_files = show_available_templates()
        from_template = click.prompt(
            "Choose a template", type=int)
        from_template = str(os.path.join(
            "./config/template_files", template_files[from_template-1]))
    else:
        from_template = str(
            os.path.join("./config/template_files", from_template))
    if not os.path.exists(from_template):
        print(colored("Template file does not exist.", "red"))
        return
    return from_template


def derive_from_template(from_template, version):
    """Derive the new file from the template by replacing values.

    The template file is read and the {{VERSION}} field is replaced.
    """
    with open(from_template, "r") as f:
        template = f.read()
    new_str_content_config_file = template.replace("{{VERSION}}", version)
    target_location = str(os.path.join("./config", f"qmt_v{version}.yaml"))
    with open(target_location, "w") as f:
        f.write(new_str_content_config_file)
    print(colored(f"Setting file created: ./config/qmt_v{version}.yaml",
                  "green"))
    return target_location


def show_example_commands(version):
    """Show examples on how to use the newly created config file."""
    print("\nExample commands:")
    print(
        "\n- Simple experiment run (no monitoring):\n" +
        f"python3 -m lib.qmt config/qmt_v{version}.yaml" +
        "\n\n- Experiment run (monitoring via screen):\n" +
        f"screen -L -Logfile data/qmt_v{version}/" +
        f"log_fuzzy.txt -S qmt_v{version} " +
        f"python3 -m lib.qmt config/qmt_v{version}.yaml"
    )


def create_experiment_folder(new_config_file):
    """Create the experiment folder."""
    print("\nCreating experiment folder:")
    exp_folder_path = new_config_file.get("experiment_folder")
    print(f"mkdir -p {exp_folder_path}")
    pathlib.Path(exp_folder_path).mkdir(parents=True, exist_ok=True)
    print(colored(f"Experiment folder created: {exp_folder_path}", "green"))


def create_coverage_file(new_config_file, from_template, version):
    """Create the coverage file.

    The argument from_template is used to retrieve a corresponding coverage
    file in the folder template coverages. It looks for a file with the same
    name but different extension (.cover instead of .yaml).
    """
    print("\nCreating coverage file:")
    coverage_settings_filepath = \
        new_config_file.get("coverage_settings_filepath")
    path_coverage_template_file = str(os.path.join(
        "./config", "template_coverage",
        str(os.path.basename(from_template)).replace(".yaml", ".cover")))
    if not os.path.exists(path_coverage_template_file):
        print(colored(f"Corresponding coverage template file " +
                      f"does not exist: {path_coverage_template_file}.",
                      "red"))
        return
    with open(path_coverage_template_file, "r") as f:
        coverage_settings = f.read()
    import qiskit
    qiskit_path = os.path.dirname(qiskit.__file__)
    new_str_content_coverage_settings = \
        coverage_settings.replace("{{VERSION}}", version).replace(
            "{{QISKIT_PATH}}", qiskit_path)
    with open(coverage_settings_filepath, "w") as out_file:
        out_file.write(new_str_content_coverage_settings)
    print(colored(f"Coverage file created:: {coverage_settings_filepath}",
                  "green"))


def check_if_version_already_exists(version):
    """Check if the version already exists."""
    target_location = f"./config/qmt_v{version}.yaml"
    if os.path.exists(target_location):
        return True
    return False


def exclude_exp_folder_gitignore(new_config_file):
    """Add the experiment folder to the .gitignore file."""
    print("\nExcluding experiment folder from gitignore:")
    exp_folder_path = new_config_file.get("experiment_folder")
    print(f"echo '{exp_folder_path}' >> .gitignore")
    with open("./.gitignore", "a") as f:
        f.write(f"\n{exp_folder_path}")
    print(colored(f"Added to .gitignore: {exp_folder_path}", "green"))

# LEVEL 0


@click.command()
@click.option('--from_template', default=None, help='File to copy.')
@click.option('--version',
              prompt='Choose a version for this run',
              help='The version of this run.')
def new_config(version, from_template):
    """Generate a new config file."""
    if check_if_version_already_exists(version):
        print(colored(f"Version {version} already exists.", "red"))
        show_example_commands(version)
        return
    from_template = query_for_template(from_template)
    target_location = derive_from_template(from_template, version)
    config = load_config_and_check(
        target_location, required_keys=[
            "experiment_folder",
            "coverage_settings_filepath"])
    create_coverage_file(config, from_template, version)
    create_experiment_folder(config)
    exclude_exp_folder_gitignore(config)
    show_example_commands(version)


if __name__ == '__main__':
    new_config()
