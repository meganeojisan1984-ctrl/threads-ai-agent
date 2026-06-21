from threads_ai_agent.cli import build_parser


def test_cli_parser_accepts_known_commands():
    args = build_parser().parse_args(["analyze", "--data-dir", "tmp-data"])

    assert args.command == "analyze"
    assert args.data_dir == "tmp-data"


def test_cli_parser_accepts_trends_command():
    args = build_parser().parse_args(["trends"])

    assert args.command == "trends"
