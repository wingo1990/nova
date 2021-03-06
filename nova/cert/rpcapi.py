# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012, Red Hat, Inc.
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

"""
Client side of the cert manager RPC API.
"""

from oslo.config import cfg

import nova.openstack.common.rpc.proxy

rpcapi_opts = [
    cfg.StrOpt('cert_topic',
               default='cert',
               help='the topic cert nodes listen on'),
]

CONF = cfg.CONF
CONF.register_opts(rpcapi_opts)

rpcapi_cap_opt = cfg.StrOpt('cert',
        help='Set a version cap for messages sent to cert services')
CONF.register_opt(rpcapi_cap_opt, 'upgrade_levels')


class CertAPI(nova.openstack.common.rpc.proxy.RpcProxy):
    '''Client side of the cert rpc API.

    API version history:

        1.0 - Initial version.
        1.1 - Added get_backdoor_port()

        ... Grizzly supports message version 1.1.  So, any changes to existing
        methods in 2.x after that point should be done such that they can
        handle the version_cap being set to 1.1.
    '''

    #
    # NOTE(russellb): This is the default minimum version that the server
    # (manager) side must implement unless otherwise specified using a version
    # argument to self.call()/cast()/etc. here.  It should be left as X.0 where
    # X is the current major API version (1.0, 2.0, ...).  For more information
    # about rpc API versioning, see the docs in
    # openstack/common/rpc/dispatcher.py.
    #
    BASE_RPC_API_VERSION = '1.0'

    VERSION_ALIASES = {
        'grizzly': '1.1',
    }

    def __init__(self):
        version_cap = self.VERSION_ALIASES.get(CONF.upgrade_levels.cert,
                                               CONF.upgrade_levels.cert)
        super(CertAPI, self).__init__(
                topic=CONF.cert_topic,
                default_version=self.BASE_RPC_API_VERSION,
                version_cap=version_cap)

    def revoke_certs_by_user(self, ctxt, user_id):
        return self.call(ctxt, self.make_msg('revoke_certs_by_user',
                                             user_id=user_id))

    def revoke_certs_by_project(self, ctxt, project_id):
        return self.call(ctxt, self.make_msg('revoke_certs_by_project',
                                             project_id=project_id))

    def revoke_certs_by_user_and_project(self, ctxt, user_id, project_id):
        return self.call(ctxt,
                self.make_msg('revoke_certs_by_user_and_project',
                              user_id=user_id, project_id=project_id))

    def generate_x509_cert(self, ctxt, user_id, project_id):
        return self.call(ctxt, self.make_msg('generate_x509_cert',
                                             user_id=user_id,
                                             project_id=project_id))

    def fetch_ca(self, ctxt, project_id):
        return self.call(ctxt, self.make_msg('fetch_ca',
                                             project_id=project_id))

    def fetch_crl(self, ctxt, project_id):
        return self.call(ctxt, self.make_msg('fetch_crl',
                                             project_id=project_id))

    def decrypt_text(self, ctxt, project_id, text):
        return self.call(ctxt, self.make_msg('decrypt_text',
                                             project_id=project_id,
                                             text=text))
