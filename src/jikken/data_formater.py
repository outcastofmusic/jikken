import pprint
from  blessings import Terminal


def format_header(term:Terminal, value: str, name:str):
    """ format bold """
    return "{t.reverse} {name} {t.normal}: {t.bold} {value} {t.normal}| ".format(t=term, value=value, name=name)


class PrintExperiment:
    def __init__(self, stdout=False, stderr=False, variables=True, git=True, monitored=True):
        self.print_stdout = stdout
        self.print_stderr = stderr
        self.print_variables = variables
        self.print_git = git
        self.print_monitored = monitored
        self.term = Terminal()
        self.banner = 100 * "-"
        self.mini_banner = 10 * "-"

    def print_db_info(self, experiment_dict):
        """Print the general experiment info """

        db_info = "| ".join([
            format_header(self.term, experiment_dict['id'], "id"),
            format_header(self.term, experiment_dict['status'], "status"),
            format_header(self.term, experiment_dict['tags'], "tags"),
            format_header(self.term, experiment_dict['schema_hash'], "schema hash"),
            format_header(self.term, experiment_dict['parameter_hash'], "param hash"),
                              ])
        print(db_info)

    def print_git_info(self, experiment_dict):
        """Print git info if available"""
        if experiment_dict["commit_id"] is not None:
            git_info = " | ".join([
                format_header(self.term, experiment_dict['commit_id'], "commit"),
                format_header(self.term, experiment_dict['dirty'], "dirty"),
                format_header(self.term, experiment_dict['repo'], "repo"),
            ] )
            print(git_info)

    def print_subsection(self, data_dict, name):
        """Print subsection with monitored data"""
        if len(data_dict) > 0:
            print("\n","{t.reverse} {t.underline} {name} {t.normal}".format(t=self.term, name=name).center(100), sep="\n")
            pprint.pprint(data_dict)

    def print_experiment(self, experiment_dict, stdout=False, stderr=False, variables=True, git=True, monitored=True):
        if experiment_dict['type'] == 'experiment':
            self.print_db_info(experiment_dict)
            if self.print_git:
                self.print_git_info(experiment_dict)
            if self.print_monitored:
                self.print_subsection(experiment_dict['monitored'], "monitored")
            if self.print_variables:
                self.print_subsection(experiment_dict['variables'], "variables")
            if self.print_stdout:
                self.print_subsection(experiment_dict['stdout'], "stdout")
            if self.print_stderr:
                self.print_subsection(experiment_dict['stderr'], "stderr")
            print(self.term.bold(self.banner))
