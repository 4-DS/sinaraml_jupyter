from .sinaraml_types import SinaraPipelineType, \
                            dataflow_fabric_default_repos, \
                            step_template_default_repo, \
                            step_template_default_substep_notebook
import subprocess
from pathlib import Path, PurePath
import tempfile

class SinaraPipeline():

    subject = 'pipeline'
    root_parser = None
    subject_parser = None
    create_parser = None
    clone_parser = None
    push_parser = None

    @staticmethod
    def add_command_handlers(root_parser, subject_parser):
        SinaraPipeline.root_parser = root_parser
        SinaraPipeline.subject_parser = subject_parser
        parser_pipeline = subject_parser.add_parser(SinaraPipeline.subject, help='sinara pipeline subject')
        pipeline_subparsers = parser_pipeline.add_subparsers(title='action', dest='action', help='Action to do with subject')

        SinaraPipeline.add_create_handler(pipeline_subparsers)
        SinaraPipeline.add_clone_handler(pipeline_subparsers)
        SinaraPipeline.add_push_handler(pipeline_subparsers)

    @staticmethod
    def add_create_handler(pipeline_cmd_parser):
        SinaraPipeline.create_parser = pipeline_cmd_parser.add_parser('create', help='create sinara pipeline')
        SinaraPipeline.create_parser.add_argument('--type', default=SinaraPipelineType.ML, type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.create_parser.set_defaults(func=SinaraPipeline.create)

    @staticmethod
    def add_clone_handler(pipeline_cmd_parser):
        SinaraPipeline.clone_parser = pipeline_cmd_parser.add_parser('clone', help='clone sinara pipeline')
        SinaraPipeline.clone_parser.add_argument('--type', default=SinaraPipelineType.ML, type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.clone_parser.set_defaults(func=SinaraPipeline.clone)

    @staticmethod
    def add_push_handler(pipeline_cmd_parser):
        SinaraPipeline.push_parser = pipeline_cmd_parser.add_parser('push', help='push sinara pipeline')
        SinaraPipeline.push_parser.add_argument('--type', default=SinaraPipelineType.ML, type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.push_parser.set_defaults(func=SinaraPipeline.push)

    @staticmethod
    def ensure_dataflow_fabric_repo_exists(args):
        dataflow_fabric_repo_url = dataflow_fabric_default_repos[args.type]
        repo_folder = PurePath(tempfile.gettempdir()) / '.sinaraml' / str(args.type)
        Path(repo_folder).mkdir(parents=True, exist_ok=True)
        repo_folder = Path(repo_folder)
        work_dir = Path(__file__).resolve().parent

        if not (repo_folder / '.git').exists():
            git_cmd = f"git clone --recursive {dataflow_fabric_repo_url} {repo_folder}"
            process = subprocess.run(git_cmd, cwd=work_dir, universal_newlines=True, shell=True)
            if process.returncode != 0:
                raise Exception(git_cmd)
            
        return repo_folder

    @staticmethod
    def call_dataflow_fabric_command(dataflow_fabric_command, work_dir):
        process = subprocess.run(dataflow_fabric_command, cwd=work_dir, universal_newlines=True, shell=True)
        if process.returncode != 0:
            raise Exception(dataflow_fabric_command)

    @staticmethod
    def create(args):
        create_pipeline_cmd = f"python sinara_pipeline_create.py {step_template_default_repo[args.type]} {step_template_default_substep_notebook[args.type]}"

        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        
        SinaraPipeline.call_dataflow_fabric_command(create_pipeline_cmd, repo_folder)

    @staticmethod
    def clone(args):
        clone_pipeline_cmd = f"python sinara_pipeline_clone.py {step_template_default_repo[args.type]} {step_template_default_substep_notebook[args.type]}"

        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        
        SinaraPipeline.call_dataflow_fabric_command(clone_pipeline_cmd, repo_folder)

    @staticmethod
    def push(args):
        push_pipeline_cmd = f"python sinara_pipeline_push.py {step_template_default_repo[args.type]} {step_template_default_substep_notebook[args.type]}"

        repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
        
        SinaraPipeline.call_dataflow_fabric_command(push_pipeline_cmd, repo_folder)