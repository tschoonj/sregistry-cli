'''

Copyright (C) 2016-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

def main(args, parser, subparser):

    from sregistry.main import get_client

    images = args.image
    if not isinstance(images, list):
        images = [images]

    for image in images:
        cli = get_client(image, quiet=args.quiet)
        cli.add(image_path=image,
                image_uri=args.name,
                copy=args.copy)
