'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

from sregistry.logger import bot
from sregistry.main import ApiConnection
import google
import json
import sys
import os

from retrying import retry
from google.cloud import storage
from googleapiclient.discovery import build as discovery_build
from oauth2client.client import GoogleCredentials

from .build import ( 
    build,
    run_build,
    load_build_config
)
from .delete import ( delete, destroy )
from .logs import ( logs, list_logs, print_log )
from .pull import pull
from .push import ( push, upload )
from .query import ( container_query, list_containers, search, search_all )


class Client(ApiConnection):

    def __init__(self, secrets=None, base=None, init=True, **kwargs):
 
        self._update_secrets()
        self._update_headers()

        # Do we need storage client now?
        if init is True:
            self._init_client()

        super(ApiConnection, self).__init__(**kwargs)

    def _speak(self):
        '''add the bucket name to be printed to the user at appropriate times
        '''
        bot.info('[bucket][%s]' % self._bucket_name)

    def _update_secrets(self):
        '''The user is required to have an application secrets file in his
           or her environment. The information isn't saved to the secrets
           file, but the client exists with error if the variable isn't found.
        '''
        env = 'GOOGLE_APPLICATION_CREDENTIALS'
        self._secrets = self._get_and_update_setting(env)
        if self._secrets is None:
            bot.error('You must export %s to use Google Storage client' %env)
            sys.exit(1)


    def _init_client(self):
        '''init client will check if the user has defined a bucket that
           differs from the default, use the application credentials to 
           get the bucket, and then instantiate the client.
        '''

        # Get storage and compute services
        self._get_services()

        env = 'SREGISTRY_GOOGLE_STORAGE_BUCKET'
        self._bucket_name = self._get_and_update_setting(env)

        # If the user didn't set in environment, use default
        if self._bucket_name is None:
            self._bucket_name = 'sregistry-gcloud-build-%s' %os.environ['USER']

        # The build bucket is for uploading .tar.gz files
        self._build_bucket_name = "%s_cloudbuild" % self._bucket_name

        # Main storage bucket for containers, and dependency bucket with targz
        self._bucket = self._get_bucket(self._bucket_name)
        self._build_bucket = self._get_bucket(self._build_bucket_name)


    def _get_services(self, version='v1'):
        '''get version 1 of the google compute and storage service

            Parameters
            ==========
            version: version to use (default is v1)
        '''
        self._bucket_service = storage.Client()
        creds = GoogleCredentials.get_application_default()
        self._storage_service = discovery_build('storage', version, credentials=creds)
        self._build_service = discovery_build('cloudbuild', version, credentials=creds)


    def _get_bucket(self, bucket_name):
        '''get a bucket based on a bucket name. If it doesn't exist, create it.

           Parameters
           ==========
           bucket_name: the name of the bucket to get (or create). It should
                        not contain google, and should be all lowercase with -
                        or underscores.
        '''

        # Case 1: The bucket already exists
        try:
            bucket = self._bucket_service.get_bucket(bucket_name)

        # Case 2: The bucket needs to be created
        except google.cloud.exceptions.NotFound:
            bucket = self._bucket_service.create_bucket(bucket_name)

        # Case 3: The bucket name is already taken
        except:
            bot.error('Cannot get or create %s' % bucket_name)
            sys.exit(1)

        return bucket


    def _get_project(self, project=None):
        '''get project returns the active project, and exists if not found.
         
           Parameters
           ==========
           project: a project to default to, if not found in the environment
           zone: a default zone, will be us-west1-a by default

        '''
        return self._required_get_and_update('SREGISTRY_GOOGLE_PROJECT', project)


    def _get_zone(self, zone='us-west1-a'):
        '''get zone returns the zone set in the environment, or the default
         
           Parameters
           ==========
           zone: a default zone, will be us-west1-a by default

        '''
        return self._get_and_update_setting('SREGISTRY_GOOGLE_ZONE', zone)


Client.pull = pull
Client.push = push
Client._upload = upload
Client.delete = delete
Client.destroy = destroy

# Build functions
Client.build = build
Client._run_build = run_build
Client._load_build_config = load_build_config

Client.search = search
Client._search_all = search_all
Client._container_query = container_query
Client._list_containers = list_containers
