from argparse import ArgumentParser, _SubParsersAction, Namespace
from typing import List, Optional

from boxman.data.mode import Mode
from boxman.data.parsed_arguments import ParsedArguments


def add_install_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(name="install", help="Install packages")

    parser.add_argument(
        "packages", nargs="+", type=str, help="List of packages to install"
    )


def add_list_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(name="list", help="List packages in a repository")

    parser.add_argument(
        "repository",
        nargs="?",
        type=str,
        help="Repository to list packages from",
        default="",
    )


def add_search_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(
        name="search", help="Search for packages with a specific string in their name"
    )

    parser.add_argument("string", nargs=1, type=str, help="Search string")


def add_installed_parser(subparser: _SubParsersAction) -> None:
    subparser.add_parser(name="installed", help="List all installed packages")


def add_config_parser(subparser: _SubParsersAction) -> None:
    subparser.add_parser(name="config", help="Show the configuration")


def add_remove_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(name="remove", help="Remove the installed packages")

    parser.add_argument(
        "packages",
        nargs="+",
        type=str,
        help="List of packages to remove",
    )


def add_show_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(
        name="show", help="Show information about a specific package"
    )

    parser.add_argument(
        "package",
        nargs="?",
        type=str,
        help="Package to show information about",
        default="",
    )


def add_files_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(
        name="files", help="List installed file_list per package"
    )

    parser.add_argument(
        "package",
        nargs="?",
        type=str,
        help="Package to show installed files for",
        default=None,
    )


def add_update_parser(subparser: _SubParsersAction) -> None:
    parser = subparser.add_parser(
        name="update", help="Update all or specific installed packages"
    )

    parser.add_argument(
        "packages",
        nargs="*",
        type=str,
        help="List of packages to update (optional)",
    )


def get_mode_from_args(args: Namespace):
    mode = Mode.NOT_SET
    if args.mode:
        mode = Mode[args.mode.upper()]
    return mode


def get_argument_list_from_args(args: Namespace, mode: Mode):
    arguments = None
    if mode in [Mode.INSTALL, Mode.UPDATE, Mode.REMOVE]:
        arguments = args.packages
    elif mode in [Mode.SHOW, Mode.FILES]:
        arguments = [args.package]
    elif mode == Mode.LIST:
        arguments = [args.repository]
    elif mode == Mode.SEARCH:
        arguments = args.string
    return arguments


def parse_args(args_list: Optional[List[str]] = None) -> ParsedArguments:
    parser = ArgumentParser(
        description="A pacman compatible package manager which works with relative paths."
    )

    subparser = parser.add_subparsers(
        title="mode",
        dest="mode",
        required=True,
    )

    # Add subparsers to parser
    add_install_parser(subparser)
    add_list_parser(subparser)
    add_search_parser(subparser)
    add_installed_parser(subparser)
    add_config_parser(subparser)
    add_remove_parser(subparser)
    add_show_parser(subparser)
    add_files_parser(subparser)
    add_update_parser(subparser)

    # Parse and return the arguments
    args = parser.parse_args(args=args_list)
    mode = get_mode_from_args(args)
    arguments = get_argument_list_from_args(args, mode)
    return ParsedArguments(mode=mode, arguments=arguments)
