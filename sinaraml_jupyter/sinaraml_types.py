from enum import Enum

class SinaraPipelineType(Enum):
    ML = 'ml'
    CV = 'cv'

    def __str__(self):
        return self.value
    
dataflow_fabric_default_repos = {
  SinaraPipelineType.ML: {
      'url': 'https://github.com/4-DS/dataflow_fabric_ml_default.git',
      'username': '1',
      'password': '2'
      },
  SinaraPipelineType.CV: {
      'url': 'https://github.com/4-DS/dataflow_fabric_cv_rest.git',
      'username': '',
      'password': ''
      }
}

step_template_default_repo = {
  SinaraPipelineType.ML: {
      'url': 'https://github.com/4-DS/pipeline-step_template.git',
      'provider_organization_api': 'https://api.github.com',
      'provider_organization_url': 'https://github.com/4-DS',
      'username': '',
      'password': ''
      },
  SinaraPipelineType.CV: {
      'url': 'https://github.com/4-DS/pipeline-step_template.git',
      'provider_organization_api': 'https://api.github.com',
      'provider_organization_url': 'https://github.com/4-DS',
      'username': '',
      'password': ''
      }
}

step_template_default_substep_notebook = {
    SinaraPipelineType.ML: 'do_step.ipynb',
    SinaraPipelineType.CV: 'do_step.ipynb' 
}