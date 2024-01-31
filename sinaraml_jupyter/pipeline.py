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

    @staticmethod
    def add_command_handlers(root_parser, subject_parser):
        SinaraPipeline.root_parser = root_parser
        SinaraPipeline.subject_parser = subject_parser
        parser_server = subject_parser.add_parser(SinaraPipeline.subject, help='sinara pipeline subject')
        server_subparsers = parser_server.add_subparsers(title='action', dest='action', help='Action to do with subject')

        SinaraPipeline.add_create_handler(server_subparsers)

    @staticmethod
    def add_create_handler(server_cmd_parser):
        SinaraPipeline.create_parser = server_cmd_parser.add_parser('create', help='create sinara pipeline')
        SinaraPipeline.create_parser.add_argument('--type', default=SinaraPipelineType.ML, type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.create_parser.set_defaults(func=SinaraPipeline.create)

    @staticmethod
    def create(args):
        dataflow_fabric_repo_url = dataflow_fabric_default_repos[args.type]
        repo_folder = PurePath(tempfile.gettempdir()) / '.sinaraml' / args.type
        Path(repo_folder).mkdir(parents=True, exist_ok=False)
        repo_folder = Path(repo_folder)
        work_dir = Path(__file__).resolve().parent

        if not repo_folder.exists():
            git_cmd = f"git clone --recursive {dataflow_fabric_repo_url} {repo_folder}"
            process = subprocess.run(git_cmd, cwd=work_dir, universal_newlines=True, shell=True)
            if process.returncode != 0:
                raise Exception(work_dir, git_cmd, output=process.stdout)
        
        create_pipeline_cmd = f"python sinara_pipeline_create.py {step_template_default_repo} {step_template_default_substep_notebook}"
        process = subprocess.run(create_pipeline_cmd, cwd=repo_folder, universal_newlines=True, shell=True)
        if process.returncode != 0:
            raise Exception(work_dir, create_pipeline_cmd, output=process.stdout)