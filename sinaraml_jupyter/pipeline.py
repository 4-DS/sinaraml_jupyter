from .sinaraml_types import SinaraPipelineType, \
                            dataflow_fabric_default_repos, \
                            step_template_default_repo, \
                            step_template_default_substep_notebook
import subprocess
from pathlib import Path
import tempfile
import os
import shutil
import logging

class SinaraPipeline():

    subject = 'pipeline'
    root_parser = None
    subject_parser = None
    create_parser = None
    pull_parser = None
    push_parser = None
    update_parser = None

    @staticmethod
    def add_command_handlers(root_parser, subject_parser):
        SinaraPipeline.root_parser = root_parser
        SinaraPipeline.subject_parser = subject_parser
        parser_pipeline = subject_parser.add_parser(SinaraPipeline.subject, help='sinara pipeline subject')
        pipeline_subparsers = parser_pipeline.add_subparsers(title='action', dest='action', help='Action to do with subject')

        SinaraPipeline.add_create_handler(pipeline_subparsers)
        SinaraPipeline.add_pull_handler(pipeline_subparsers)
        SinaraPipeline.add_push_handler(pipeline_subparsers)
        SinaraPipeline.add_update_handler(pipeline_subparsers)

    @staticmethod
    def add_create_handler(pipeline_cmd_parser):
        SinaraPipeline.create_parser = pipeline_cmd_parser.add_parser('create', help='create sinara pipeline')
        SinaraPipeline.create_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.create_parser.add_argument('--fabric', type=str, help='sinara fabric repo url')
        SinaraPipeline.create_parser.add_argument('--fabric_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.create_parser.add_argument('--fabric_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.create_parser.add_argument('--step_template', type=str, help='sinara step template repo url')
        SinaraPipeline.create_parser.add_argument('--step_template_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.create_parser.add_argument('--step_template_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.create_parser.add_argument('--step_template_provider_organization_api', type=str, help='sinara step template repo git provider api url')
        SinaraPipeline.create_parser.add_argument('--step_template_provider_organization_url', type=str, help='sinara step template repo git provider organization url')
        SinaraPipeline.create_parser.set_defaults(func=SinaraPipeline.create)

    @staticmethod
    def add_pull_handler(pipeline_cmd_parser):
        SinaraPipeline.pull_parser = pipeline_cmd_parser.add_parser('pull', help='pull sinara pipeline')
        SinaraPipeline.pull_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.pull_parser.add_argument('--fabric', type=str, help='sinara fabric repo url')
        SinaraPipeline.pull_parser.add_argument('--fabric_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.pull_parser.add_argument('--fabric_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.pull_parser.add_argument('--step_template', type=str, help='sinara step template repo url')
        SinaraPipeline.pull_parser.add_argument('--step_template_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.pull_parser.add_argument('--step_template_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.pull_parser.add_argument('--step_template_provider_organization_api', type=str, help='sinara step template repo git provider api url')
        SinaraPipeline.pull_parser.add_argument('--step_template_provider_organization_url', type=str, help='sinara step template repo git provider organization url')
        SinaraPipeline.pull_parser.set_defaults(func=SinaraPipeline.pull)

    @staticmethod
    def add_push_handler(pipeline_cmd_parser):
        SinaraPipeline.push_parser = pipeline_cmd_parser.add_parser('push', help='push sinara pipeline')
        SinaraPipeline.push_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.push_parser.add_argument('--fabric', type=str, help='sinara fabric repo url')
        SinaraPipeline.push_parser.add_argument('--fabric_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.push_parser.add_argument('--fabric_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.push_parser.add_argument('--step_template', type=str, help='sinara step template repo url')
        SinaraPipeline.push_parser.add_argument('--step_template_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.push_parser.add_argument('--step_template_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.push_parser.add_argument('--step_template_provider_organization_api', type=str, help='sinara step template repo git provider api url')
        SinaraPipeline.push_parser.add_argument('--step_template_provider_organization_url', type=str, help='sinara step template repo git provider organization url')
        SinaraPipeline.push_parser.set_defaults(func=SinaraPipeline.push)

    @staticmethod
    def add_update_handler(pipeline_cmd_parser):
        SinaraPipeline.update_parser = pipeline_cmd_parser.add_parser('update', help='update sinara pipeline components')
        SinaraPipeline.update_parser.add_argument('component', choices=['sinaralib'], type=str, help='sinara component to update')
        SinaraPipeline.update_parser.add_argument('--type', type=SinaraPipelineType, choices=list(SinaraPipelineType), help='sinara pipeline type (default: %(default)s)')
        SinaraPipeline.update_parser.add_argument('--fabric', type=str, help='sinara fabric repo url')
        SinaraPipeline.update_parser.add_argument('--fabric_git_user', type=str, help='sinara fabric repo git user name')
        SinaraPipeline.update_parser.add_argument('--fabric_git_password', type=str, help='sinara fabric repo git password')
        SinaraPipeline.update_parser.set_defaults(func=SinaraPipeline.update)

    @staticmethod
    def ensure_dataflow_fabric_repo_exists(args):
        fabric_repo_url, fabric_repo_username, fabric_repo_password = SinaraPipeline.get_fabric_repo(args)
        repo_folder = Path(tempfile.gettempdir()) / '.sinaraml' / str(args.type)

        if repo_folder.exists():
            shutil.rmtree(repo_folder)
        repo_folder.mkdir(parents=True, exist_ok=True)

        git_cmd = f"git -c credential.helper=\'!f() {{ sleep 1; echo \"username=${{GIT_USER}}\"; echo \"password=${{GIT_PASSWORD}}\"; }}; f\' clone --recursive {fabric_repo_url} {repo_folder}"

        temp_env = os.environ.copy()
        temp_env["GIT_USER"] = fabric_repo_username
        temp_env["GIT_PASSWORD"] = fabric_repo_password
        process = subprocess.run(git_cmd,
                                 cwd=repo_folder,
                                 universal_newlines=True,
                                 shell=True,
                                 env=temp_env)
        if process.returncode != 0:
            raise Exception(git_cmd)

        return repo_folder

    @staticmethod
    def call_dataflow_fabric_command(dataflow_fabric_command, work_dir):
        process = subprocess.run(dataflow_fabric_command, cwd=work_dir, universal_newlines=True, shell=True, env=os.environ)
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
    def get_step_template_repo(args):
        repo_url = step_template_default_repo[args.type]['url'] \
            if not args.step_template else args.step_template
        
        repo_user = step_template_default_repo[args.type]['username'] \
            if not args.step_template_git_user else args.step_template_git_user
        
        repo_password = step_template_default_repo[args.type]['password'] \
            if not args.step_template_git_password else args.step_template_git_password
        
        repo_provider_organization_api = step_template_default_repo[args.type]['provider_organization_api'] \
            if not args.step_template_provider_organization_api else args.step_template_provider_organization_api

        repo_provider_organization_url = step_template_default_repo[args.type]['provider_organization_url'] \
            if not args.step_template_provider_organization_url else args.step_template_provider_organization_url

        return repo_url, repo_user, repo_password, \
               repo_provider_organization_api, repo_provider_organization_url

    @staticmethod
    def get_fabric_repo(args):
        repo_url = dataflow_fabric_default_repos[args.type]['url'] \
            if not args.fabric else args.fabric
        
        repo_user = dataflow_fabric_default_repos[args.type]['username'] \
            if not args.fabric_git_user else args.fabric_git_user
        
        repo_password = dataflow_fabric_default_repos[args.type]['password'] \
            if not args.fabric_git_password else args.fabric_git_password        

        return repo_url, repo_user, repo_password

    @staticmethod
    def create(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "create")

        step_template_url, step_template_username, \
             step_template_password, \
             step_template_provider_organization_api, \
             step_template_provider_organization_url = SinaraPipeline.get_step_template_repo(args)
        substep_name = step_template_default_substep_notebook[args.type]
        
        create_pipeline_cmd = f"python sinara_pipeline_create.py "\
                              f"--git_step_template_url={step_template_url} "\
                              f"--step_template_nb_substep={substep_name} "\
                              f"--current_dir={curr_dir} "\
                              f"--git_step_template_username={step_template_username} "\
                              f"--git_step_template_password={step_template_password} "\
                              f"--git_provider_organization_api={step_template_provider_organization_api} "\
                              f"--git_provider_organization_url={step_template_provider_organization_url}"
        
        try:
            repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
            SinaraPipeline.call_dataflow_fabric_command(create_pipeline_cmd, repo_folder)
        except Exception as e:
            logging.debug(e)
            raise Exception('Error while executing fabric scripts, launch CLI with --verbose to see details')

    @staticmethod
    def pull(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "pull")

        step_template_url, step_template_username, \
             step_template_password, \
             step_template_provider_organization_api, \
             step_template_provider_organization_url = SinaraPipeline.get_step_template_repo(args)
        substep_name = step_template_default_substep_notebook[args.type]

        pull_pipeline_cmd = f"python sinara_pipeline_pull.py "\
                            f"--git_step_template_url={step_template_url} "\
                            f"--step_template_nb_substep={substep_name} "\
                            f"--current_dir={curr_dir} "\
                            f"--git_step_template_username={step_template_username} "\
                            f"--git_step_template_password={step_template_password} "\
                            f"--git_provider_organization_api={step_template_provider_organization_api} "\
                            f"--git_provider_organization_url={step_template_provider_organization_url}"
        
        try:
            repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
            SinaraPipeline.call_dataflow_fabric_command(pull_pipeline_cmd, repo_folder)
        except Exception as e:
            logging.debug(e)
            raise Exception('Error while executing fabric scripts, launch CLI with --verbose to see details')

    @staticmethod
    def push(args):
        curr_dir = os.getcwd()

        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, "push")

        step_template_url, step_template_username, \
             step_template_password, \
             step_template_provider_organization_api, \
             step_template_provider_organization_url = SinaraPipeline.get_step_template_repo(args)
        substep_name = step_template_default_substep_notebook[args.type]

        push_pipeline_cmd = f"python sinara_pipeline_push.py "\
                            f"--git_step_template_url={step_template_url} "\
                            f"--step_template_nb_substep={substep_name} "\
                            f"--current_dir={curr_dir} "\
                            f"--git_step_template_username={step_template_username} "\
                            f"--git_step_template_password={step_template_password} "\
                            f"--git_provider_organization_api={step_template_provider_organization_api} "\
                            f"--git_provider_organization_url={step_template_provider_organization_url}"

        try:
            repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
            SinaraPipeline.call_dataflow_fabric_command(push_pipeline_cmd, repo_folder)
        except Exception as e:
            logging.debug(e)
            raise Exception('Error while executing fabric scripts, launch CLI with --verbose to see details')

    @staticmethod
    def update(args):

        if args.component == "sinaralib":
            update_sinaralib_pipeline_cmd = f"python sinara_pipeline_update_sinaralib.py"
        else:
            raise Exception(f'Component {args.component} is not supported by update')
        
        if not args.type:
            while not args.type:
                SinaraPipeline.ensure_pipeline_type(args, f"update {args.component}")

        try:
            repo_folder = SinaraPipeline.ensure_dataflow_fabric_repo_exists(args)
            SinaraPipeline.call_dataflow_fabric_command(update_sinaralib_pipeline_cmd, repo_folder)
        except Exception as e:
            logging.debug(e)
            raise Exception('Error while executing fabric scripts, launch CLI with --verbose to see details')