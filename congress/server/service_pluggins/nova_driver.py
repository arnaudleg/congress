#!/usr/bin/env python
# Copyright (c) 2013 VMware, Inc. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
from congress.server.service_pluggins.datasource_driver import DataSourceDriver
import datetime
import logging
from novaclient.client import Client
from congress.server.service_pluggins.settings import OS_USERNAME, \
    OS_PASSWORD, OS_AUTH_URL, OS_TENANT_NAME

logger = logging.getLogger(__name__)


class NovaDriver(DataSourceDriver):
    USERNAME = OS_USERNAME
    PASSWORD = OS_PASSWORD
    AUTH_URL = OS_AUTH_URL
    TENANT_NAME = OS_TENANT_NAME
    SERVERS = "servers"
    FLAVORS = "flavors"
    HOSTS = "hosts"
    FLOATING_IPS = "floating_IPs"

    last_updated = -1

    def __init__(self, **creds):
        credentials = self.get_nova_credentials_v2()
        self.nova_client = Client(**credentials)

    def update_from_datasource(self):
        self.servers = self._get_tuple_list(
            self.nova_client.servers.list(detailed=True), self.SERVERS)
        self.flavors = self._get_tuple_list(
            self.nova_client.flavors.list(), self.FLAVORS)
        self.hosts = self._get_tuple_list(self.nova_client.hosts.list(),
                                          self.HOSTS)
        self.floating_ips = self._get_tuple_list(
            self.nova_client.floating_ips.list(), self.FLOATING_IPS)
        self.last_updated = datetime.datetime.now()

    def get_all(self, type):
        if type == self.SERVERS:
            return self.servers
        elif type == self.FLAVORS:
            return self.flavors
        elif type == self.HOSTS:
            return self.hosts
        elif type == self.FLOATING_IPS:
            return self.floating_ips

    def get_tuple_names(self):
        return (self.SERVERS, self.FLAVORS, self.HOSTS)

    def get_tuple_metadata(self, type):
        if type == self.SERVERS:
            return ("id", "name", "host_id", "status", "tenant_id",
                    "user_id", "image_id", "flavor_id")
        elif type == self.FLAVORS:
            return ("id", "name", "vcpus", "ram", "disk", "ephemeral",
                    "rxtx_factor")
        elif type == self.HOSTS:
            return ("host_name", "service", "zone")
        elif type == self.FLOATING_IPS:
            return ("floating_ip", "id", "ip", "host_id", "pool")
        else:
            return ()

    def get_last_updated_time(self):
        return self.last_updated

    def get_nova_credentials_v2(self):
        d = {}
        d['version'] = '2'
        d['username'] = self.USERNAME
        d['api_key'] = self.PASSWORD
        d['auth_url'] = self.AUTH_URL
        d['project_id'] = self.TENANT_NAME
        return d

    def _get_tuple_list(self, obj, type):
        t_list = []
        if type == self.SERVERS:
            for s in obj:
                image = s.image["id"]
                flavor = s.flavor["id"]
                tuple = (s.id, s.name, s.hostId, s.status, s.tenant_id,
                         s.user_id, image, flavor)
                t_list.append(tuple)
        elif type == self.FLAVORS:
            for f in obj:
                tuple = (f.id, f.name, f.vcpus, f.ram, f.disk, f.ephemeral,
                         f.rxtx_factor)
                t_list.append(tuple)
        elif type == self.HOSTS:
            for h in obj:
                tuple = (h.host_name, h.service, h.zone)
                t_list.append(tuple)
        elif type == self.FLOATING_IPS:
            for i in obj:
                tuple = (i.fixed_ip, i.id, i.ip, i.instance_id, i.pool)
                t_list.append(tuple)
        return t_list


def main():
    driver = NovaDriver()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -'
                                  ' %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Last updated: %s" % driver.get_last_updated_time())

    logger.info("Starting Nova Sync Service")
    logger.info("Tuple Names : " +
                str(driver.get_tuple_names()))
    logger.info("Tuple Metadata - 'servers' : " +
                str(driver.get_tuple_metadata(driver.SERVERS)))
    #sync with the nova service
    driver.update_from_datasource()
    logger.info("Servers: %s" % driver.get_all(driver.SERVERS))
    logger.info("Flavors: %s" % driver.get_all(driver.FLAVORS))
    logger.info("Hosts: %s" % driver.get_all(driver.HOSTS))
    logger.info("Floating IPs: %s" % driver.get_all(driver.FLOATING_IPS))
    logger.info("Last updated: %s" % driver.get_last_updated_time())
    logger.info("Sync completed")

    logger.info("-----------------------------------------")

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        # Let system.exit() calls complete normally
        raise
    except Exception:
        raise
