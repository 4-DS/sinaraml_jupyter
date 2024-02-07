from .sinaraml_types import SinaraPipelineType, \
                            dataflow_fabric_default_repos, \
                            step_template_default_repo, \
                            step_template_default_substep_notebook
import subprocess
from pathlib import Path
import tempfile
import os
import shutil

class SinaraPipeline():

    subject = 'pipeline'
    root_parser = None
    subject_parser = None
    create_parser = None
    pull_parser = None
    push_parser = None

    @staticmethod
    def add_command_handlers(root_parser, subject_parser):
        SinaraPipeline.root_parser = root_parser
        SinaraPipeline.subject_parser = subject_parser
        parser_pipeline = subject_parser.add_parser(SinaraPipeline.subject, help='sinara pipeline subject')
        pipeline_subparsers = parser_pipeline.add_subparsers(title='action', dest='action', help='Action to do with subject')

        SinaraPipeline.add_create_handler(pipeline_subparsers)
        SinaraPipeline.add_pull_handler(pipeline_subparsers)
        SinaraPipeline.add_push_handler(pipeline_subparsers)

    @staticmethod
    def add_create_handler(pipeline_cmd_parser):
        SinaraPipeline.create_parser = pipeline_cmd_parser.add_parser('create', help='create sinara pipeline')
        SinaraPipeline.create_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.create_parser.set_defaults(func=SinaraPipeline.create)

    @staticmethod
    def add_pull_handler(pipeline_cmd_parser):
        SinaraPipeline.pull_parser = pipeline_cmd_parser.add_parser('pull', help='pull sinara pipeline')
        SinaraPipeline.pull_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.pull_parser.set_defaults(func=SinaraPipeline.pull)

    @staticmethod
    def add_push_handler(pipeline_cmd_parser):
        SinaraPipeline.push_parser = pipeline_cmd_parser.add_parser('push', help='push sinara pipeline')
        SinaraPipeline.push_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.push_parser.set_defaults(func=SinaraPipeline.push)

    @staticmethod
    def ensure_dataflow_fabric_repo_exists(args):
        dataflow_fabric_repo_url = dataflow_fabric_default_repos[args.type]
        repo_folder = Path(tempfile.gettempdir()) / '.sinaraml' / str(args.type)

        if repo_folder.exists():
            shutil.rmtree(repo_folder)
        repo_folder.mkdir(parents=True, exist_ok=True)

        git_cmd = f"git clone --recursive {dataflow_fabric_repo_url} {repo_folder}"
        process = subprocess.run(git_cmd, cwd=repo_folder, universal_newlines=True, shell=True)
        if process.returncode != 0:
            raise Exception(git_cmd)

        return repo_folder

    @staticmethod
    def call_dataflow_fabric_command(dataflow_fabric_command, work_dir):
        process = subprocess.run(dataflow_fabric_command, cwd=work_dir, universal_newlines=True, shell=True)
        if process.returncode != 0:
            raise Exception(dataflow_fabric_command)
        
    @staticmethod
    def ensure_pipeline_type(args, command):
        type_input = None
        while not type_input:
            try:
                type_input = int(input(f"Please, enter pipeline type to {command} 1) ML 2) CV: "))
            except:
                type_input = None
        if type_input == 1:
            args.type = SinaraPipelineType.ML
        elif type_input == 2:
            args.type = SinaraPipelineType.CV
        else:
            args.type = None

    @staticmethod
    def create(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "create")
        
        create_pipeline_cmd = f"python sinara_pipeline_create.py --step_template_git={step_template_default_repo[args.type]} --step_template_nb_substep={step_template_default_substep_notebook[args.type]} --current_dir={curr_dir}"
        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        SinaraPipeline.call_dataflow_fabric_command(create_pipeline_cmd, repo_folder)

    @staticmethod
    def pull(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "pull")

        pull_pipeline_cmd = f"python sinara_pipeline_pull.py --step_template_git={step_template_default_repo[args.type]} --step_template_nb_substep={step_template_default_substep_notebook[args.type]} --current_dir={curr_dir}"
        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        SinaraPipeline.call_dataflow_fabric_command(pull_pipeline_cmd, repo_folder)

    @staticmethod
    def push(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "push")

        push_pipeline_cmd = f"python sinara_pipeline_push.py --step_template_git={step_template_default_repo[args.type]} --step_template_nb_substep={step_template_default_substep_notebook[args.type]} --current_dir={curr_dir}"
        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        SinaraPipeline.call_dataflow_fabric_command(push_pipeline_cmd, repo_folder)