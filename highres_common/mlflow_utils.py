
class MlflowInfo:
    def __init__(self, experiment=None, run=None):
        self.experiment = experiment
        self.run = run

    def print_experiment_info(self):
        """
        This function prints the name, experiment ID, artifact location, and lifecycle stage of an
        experiment.

        Args:
        experiment: The experiment object that contains the mlflow experiment information.
        """

        if not self.experiment:
            print("No experiment provided.")
            return
        
        print("Experiment Info")
        print(f"Name: {self.experiment.name}")
        print(f"Experiment ID: {self.experiment.experiment_id}")
        print(f"Artifact Location: {self.experiment.artifact_location}")
        print(f"Lifecycle Stage: {self.experiment.lifecycle_stage}")


    def print_run_info(self):
        """
        It prints out the run_id, experiment_id, params, artifact_uri, and status of a run

        Args:
        run: The run object that contains the mlflow run information.
        """

        if not self.run:
            print("No run provided.")
            return
        
        print("Run Info")
        print(f"Run ID: {self.run.info.run_id}")
        print(f"Experiment ID: {self.run.info.experiment_id}")
        print(f"Artifact Uri: {self.run.info.artifact_uri}")
        print(f"Status: {self.run.info.status}")
        print("Params: ")
        for k, v in self.run.data.params.items():
            print(f"    - {k}: {v}")
            
    def print_run_metrics(self):
        if not self.run:
            print("No run provided.")

        print("Run Metrics")
        for k, v in self.run.data.metrics.items():
            print(f" - {k}: {v}")

    def print_run_tags(self):
        if not self.run:
            print("No run provided.")
        print("Run Tags")

        for k, v in self.run.data.tags.items():
            print(f" - {k}: {v}")
            