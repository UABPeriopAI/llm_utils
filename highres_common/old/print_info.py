def print_experiment_info(experiment):
    """
    This function prints the name, experiment ID, artifact location, and lifecycle stage of an
    experiment.

    Args:
      experiment: The experiment object that contains the mlflow experiment information.
    """

    print("Name: {}".format(experiment.name))
    print("Experiment ID: {}".format(experiment.experiment_id))
    print("Artifact Location: {}".format(experiment.artifact_location))
    print("Lifecycle_stage: {}".format(experiment.lifecycle_stage))


def print_run_info(run):
    """
    It prints out the run_id, experiment_id, params, artifact_uri, and status of a run

    Args:
      run: The run object that contains the mlflow run information.
    """

    print("run_id: {}".format(run.info.run_id))
    print("experiment_id: {}".format(run.info.experiment_id))
    print("params: {}".format(run.data.params))
    print("artifact_uri: {}".format(run.info.artifact_uri))
    print("status: {}".format(run.info.status))
