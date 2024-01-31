from enum import Enum

class SinaraPipelineType(Enum):
    ML = 'ml'
    CV = 'cv'

    def __str__(self):
        return self.value

dataflow_fabric_default_repos = {
  SinaraPipelineType.ML: 'https://github.com/4-DS/dataflow_fabric_ml_default.git',
  SinaraPipelineType.CV: 'https://github.com/4-DS/dataflow_fabric_cv_rest.git'
}

step_template_default_repo = {
    SinaraPipelineType.ML: 'https://github.com/4-DS/pipeline-step_template.git',
    SinaraPipelineType.CV: 'https://github.com/4-DS/pipeline-step_template.git'
}

step_template_default_substep_notebook = {
    SinaraPipelineType.ML: 'do_step.ipynb',
    SinaraPipelineType.CV: 'do_step.ipynb' 
}