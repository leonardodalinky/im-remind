#!/usr/bin/python3
import os
import sys
import requests
import time
import hashlib
import argparse
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, TextIO, Optional


parser = argparse.ArgumentParser(description="Message reminder based on IM.")
# subparsers
subparsers = parser.add_subparsers(dest="command", help="Sub-command help")
parser.add_argument(
    "-t",
    "--timeout",
    type=float,
    help="Timeout in seconds. Default is 10 sec.",
    default=10.0,
)
parser.add_argument(
    "-m",
    "--max-length",
    type=int,
    help="Max length of message. Default is 256. If max length < 0, then ignore.",
    default=256,
)
parser.add_argument(
    "--truncate",
    dest="truncate",
    action="store_true",
    help="Truncate message instead of throwing error when exceed the max-length.",
)
parser.add_argument(
    "--conf", type=argparse.FileType("r", encoding="utf-8"), help="Optional specified config file."
)
parser.add_argument("--stdout", action="store_true", help="Print qq message to stdout.")
parser.add_argument("--dryrun", action="store_true", help="Only check without sending msg.")
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")

# qq
qq_subparser = subparsers.add_parser("qq", help="Send QQ message")
qq_subparser.add_argument("-q", "--qq", type=str, help="QQ ID to be @.")
qq_subparser.add_argument("-g", "--group", type=str, help="Group ID to send message.")
qq_subparser.add_argument("--api-path", type=str, help="API path to send message.")
qq_subparser.add_argument("--token", type=str, help="Token to send message.")
qq_subparser.add_argument(
    "-f",
    "--file",
    type=argparse.FileType("r", encoding="utf-8"),
    help="File to read from.",
)
qq_subparser.add_argument(
    "msg", nargs="?", type=str, help="Message to send. Or use pipe to read from stdin."
)

# tg
tg_subparser = subparsers.add_parser("tg", help="Send Telegram message")
tg_subparser.add_argument("--api-path", type=str, help="API path to send message.")
tg_subparser.add_argument("--token", type=str, help="Token to send message.")
tg_subparser.add_argument(
    "-f",
    "--file",
    type=argparse.FileType("r", encoding="utf-8"),
    help="File to read from.",
)
tg_subparser.add_argument(
    "msg", nargs="?", type=str, help="Message to send. Or use pipe to read from stdin."
)


def get_env_config(conf: Optional[TextIO] = None) -> Dict[str, Any]:
    if conf is not None:
        return yaml.safe_load(conf)
    config_paths = [
        Path.home() / ".im_remind.yaml",
        Path.home() / ".im_remind.yml",
        Path.home() / ".config" / "im_remind.yaml",
        Path.home() / ".config" / "im_remind.yml",
    ]
    for config_path in config_paths:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    return {
        "qq": {
            "api-path": os.environ.get("QQ_API_PATH", None),
            "token": os.environ.get("QQ_TOKEN", None),
            "session": {
                "qq": os.environ.get("QQ_SESSION_QQ", None),
                "group": os.environ.get("QQ_SESSION_GROUP", None),
            },
        },
        "tg": {
            "api-path": os.environ.get("TG_API_PATH", None),
            "token": os.environ.get("TG_TOKEN", None),
        },
    }


def send_qq_msg(
    msg: str,
    timeout: float = 10.0,
    qid=None,
    gid=None,
    token=None,
    api_path=None,
    dryrun=False,
    conf=None,
) -> Dict[str, Any]:
    """
    Send QQ message.

    Args:
        msg: Message to send.
        timeout: Timeout in seconds.
        qid (Optional[str]): QQ ID to be @.
        gid (Optional[str]): Group ID to send message.
        token (Optional[str]): Token to send message.
        api_path (Optional[str]): API path to send message.
        dryrun (Optional[bool]): Only check without sending msg.
        conf (Optional[TextIO]): Config file.
    """
    conf = get_env_config(conf)
    if token is None:
        token = conf["qq"]["token"]
    if api_path is None:
        api_path = conf["qq"]["api-path"]
    if qid is None:
        qid = str(conf["qq"]["session"]["qq"])
    if gid is None:
        gid = str(conf["qq"]["session"]["group"])
    assert token is not None
    assert api_path is not None
    assert qid is not None
    assert gid is not None
    ts = int(time.time())
    req_body = {
        "msg": msg,
        "uid": qid,
        "gid": gid,
        "ts": ts,
        "sign": hashlib.md5(
            (msg + str(gid) + str(qid) + str(ts) + token).encode("utf-8")
        ).hexdigest(),
    }
    logging.debug("Message body: ", req_body)
    if dryrun:
        return {}
    ret = requests.post(
        api_path,
        json=req_body,
        timeout=timeout,
    )
    ret.raise_for_status()
    return ret.json()


def send_tg_msg(
    msg: str,
    timeout: float = 10.0,
    token=None,
    api_path=None,
    dryrun=False,
    conf=None,
) -> Dict[str, Any]:
    """
    Send Telegram message.

    Args:
        msg: Message to send.
        timeout: Timeout in seconds.
        token (Optional[str]): Token to send message.
        api_path (Optional[str]): API path to send message.
        dryrun (Optional[bool]): Only check without sending msg.
        conf (Optional[TextIO]): Config file.
    """
    conf = get_env_config(conf)
    if token is None:
        token = conf["tg"]["token"]
    if api_path is None:
        api_path = conf["tg"]["api-path"]
    assert token is not None
    assert api_path is not None
    req_body = {"msg": msg, "token": token}
    logging.debug("Message body: ", req_body)
    if dryrun:
        return {}
    ret = requests.post(
        api_path,
        json=req_body,
        timeout=timeout,
    )
    ret.raise_for_status()
    return {
        "ret": ret.text,
    }


def main():
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    if args.command is None:
        parser.print_help()
        return

    has_stdin_msg = not sys.stdin.isatty()
    if hasattr(args, "msg") and args.msg is not None:
        logging.debug(f"Message from argument: {args.msg}")
        msg = args.msg
    elif args.file is not None:
        logging.debug(f"Read from file {args.file.name}.")
        msg = args.file.read()
    elif has_stdin_msg:
        logging.debug("Read from stdin.")
        msg = sys.stdin.read()
    else:
        logging.error("No message to send.")
        sys.exit(1)

    if 0 <= args.max_length < len(msg):
        if not args.truncate:
            logging.error(f"Message is too long. Max length is {args.max_length}.")
            sys.exit(1)
        else:
            msg = msg[: args.max_length]

    if args.command == "qq":
        ret = send_qq_msg(
            msg,
            timeout=args.timeout,
            qid=args.qq,
            gid=args.group,
            token=args.token,
            api_path=args.api_path,
            dryrun=args.dryrun,
        )
    elif args.command == "tg":
        ret = send_tg_msg(
            msg, timeout=args.timeout, token=args.token, api_path=args.api_path, dryrun=args.dryrun
        )
    else:
        logging.error("Unknown command.")
        sys.exit(1)

    logging.debug(f"Response: {ret}")

    if args.stdout:
        sys.stdout.write(msg)

    return 0


if __name__ == "__main__":
    main()
