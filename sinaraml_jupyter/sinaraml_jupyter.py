#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from .org_manager import SinaraOrgManager


@dataclass
class Gitref:
    gitref: str

def check_any_org_exists():
    if not SinaraOrgManager.check_last_update():
        jupyter_cli_org = "https://github.com/4-DS/mlops_jupyter_organization.git"
        if os.environ.get('SINARA_ORG'):
            platform = os.environ.get('SINARA_PLATFORM')
            sinara_org = json.loads(os.environ.get('SINARA_ORG').replace("'", '"'))
            platform_short = platform.split('_')[-1]
            body = [body for body in sinara_org["cli_bodies"] if platform_short in body["platform_names"]]
            if body and "mlops_jupyter_organization" in body[0].keys():
                jupyter_cli_org = body[0]["mlops_jupyter_organization"]
        args = Gitref(gitref = jupyter_cli_org)
        SinaraOrgManager.install_from_git(args)

def init_cli(root_parser, subject_parser, platform=None):
    root_parser.subjects = []

    SinaraOrgManager.add_command_handlers(root_parser, subject_parser)

    org_name = 'personal'
    if platform and '_' in platform:
        org_name = platform.split('_')[0]
    org = SinaraOrgManager.load_organization(org_name)
    if org:
        org.add_command_handlers(root_parser, subject_parser)

def update_orgs():
    for org in SinaraOrgManager.get_orgs():
        from collections import namedtuple
        Args = namedtuple('Args', ['name', 'internal'])
        args = Args(name=org["name"], internal=True)
        SinaraOrgManager.update_org(args)

def setup_logging(use_vebose=False):
    logging.basicConfig(format="%(levelname)s: %(message)s")
    if use_vebose:
        logging.getLogger().setLevel(logging.DEBUG)

def get_cli_version():
    try:
        from ._version import __version__
        return __version__
    except Exception as e:
        logging.info(e)
    return 'unknown'

def main():

    exit_code = -1

    # add root parser and root subcommand parser (subject)
    parser = argparse.ArgumentParser()
    subject_subparser = parser.add_subparsers(title='subject', dest='subject', help=f"subject to use")
    parser.add_argument('-v', '--verbose', action='store_true', help="display verbose logs")
    parser.add_argument('--version', action='version', version=f"SinaraML Jupyter CLI {get_cli_version()}")

    sinara_platform = os.environ.get('SINARA_PLATFORM')
    for i in range(1, len(sys.argv)):
        a = sys.argv[i]
        if a.startswith('--platform'):
            sinara_platform = a.split('=')[1] if "=" in a else sys.argv[i+1]
            break
    
    #if not sinara_platform:
    check_any_org_exists()
    
    update_orgs()
    # each cli plugin adds and manages subcommand handlers (starting from subject handler) to root parser
    init_cli(parser, subject_subparser, sinara_platform)

    # parse the command line and get all arguments
    args = parser.parse_known_args()[0]

    # Setup logs format and verbosity level
    setup_logging(args.verbose)
    
    # display help if required arguments are missing
    if not args.subject:
        parser.print_help()
    elif not args.action:
        subparsers_actions = [
            action for action in parser._actions 
            if isinstance(action, argparse._SubParsersAction)]
        for subparsers_action in subparsers_actions:
            for choice, subparser in subparsers_action.choices.items():
                if args.subject == choice:
                    print(subparser.format_help())

    args.func(args)
    exit_code = 0
    # # call appropriate handler for the whole command line from a cli plugin if installed
    # if hasattr(args, 'func'):
    #     try:
    #         args.func(args)
    #         exit_code = 0
    #     except Exception as e:
    #         if args.verbose:
    #             logging.exception(e)
    #         else:
    #             logging.error(e)
    
    return exit_code

if __name__ == "__main__":
    main()