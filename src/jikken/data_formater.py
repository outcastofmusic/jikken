import pprint


def print_experiment(experiment_dict, stdout=False, stderr=False, variables=True, git=True, monitored=True):
    header = 100 * "-"
    print(header)
    db_info = "id: {} | status: {} | tags {}".format(
        experiment_dict['id'],
        experiment_dict['status'],
        experiment_dict['tags']
    )
    print(db_info)
    if git and experiment_dict['commit_id'] is not None:
        git_info = "commit_id: {} | dirty: {} | repo: {}".format(
            experiment_dict["commit_id"],
            experiment_dict["dirty"],
            experiment_dict["repo"],
        )
        print(git_info)
    mini_banner = "-" * 10
    if monitored and len(experiment_dict['monitored']) > 0:
        print("monitored".center(100), mini_banner.center(100), sep="\n")
        pprint.pprint(experiment_dict['monitored'])
    if variables:
        print("variables".center(100), mini_banner.center(100), sep="\n")
        pprint.pprint(experiment_dict['variables'])
    if stdout:
        print("stdout".center(100), mini_banner.center(100), experiment_dict['stdout'], sep="\n")
    if stderr:
        print("stderr".center(100), mini_banner.center(100), experiment_dict['stderr'], sep="\n")
    footer = 100 * "-"
    print(footer)
