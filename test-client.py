#! /usr/bin/env python3

import argparse
import logging
import os
import sys

import grpc

from client import create_client_channel, PoskaShipStub
from common import message_to_dict

logging.basicConfig(
    stream=sys.stderr,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
)
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


def main():
    """
    Entry point for script, see `--help` for usage
    """
    def parse_args():
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('remote', nargs='?', default='www.passetonhack.fr')
        args = parser.parse_args()
        return args

    args = parse_args()
    logger.debug('args = %r', args)
    try:
        with create_client_channel(args.remote, tls=True) as cc:
            stub = PoskaShipStub(*cc)
            me = stub.Me()
            print('me = ', message_to_dict(me))

    # pylint: disable-next=broad-exception-caught
    except grpc.RpcError as rpc_error:
        logger.error("Received error: %s", rpc_error)
    except Exception as e:
        te = type(e)
        show_bt = logger.getEffectiveLevel() <= logging.DEBUG
        logger.error(
            'Caught exception %s.%s: %s',
            te.__module__, te.__name__, str(e), exc_info=show_bt
        )
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
