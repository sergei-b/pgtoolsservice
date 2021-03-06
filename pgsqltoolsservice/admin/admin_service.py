# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from pgsqltoolsservice.admin.contracts import (
    DatabaseInfo, GetDatabaseInfoParameters, GetDatabaseInfoResponse, GET_DATABASE_INFO_REQUEST)
from pgsqltoolsservice.connection.contracts import ConnectionType
from pgsqltoolsservice.hosting import RequestContext, ServiceProvider
from pgsqltoolsservice.utils import constants


class AdminService(object):
    """Service for general database administration support"""

    def __init__(self):
        self._service_provider: ServiceProvider = None

    def register(self, service_provider: ServiceProvider):
        self._service_provider = service_provider

        # Register the request handlers with the server
        self._service_provider.server.set_request_handler(
            GET_DATABASE_INFO_REQUEST, self._handle_get_database_info_request
        )

        if self._service_provider.logger is not None:
            self._service_provider.logger.info('Admin service successfully initialized')

    # REQUEST HANDLERS #####################################################

    def _handle_get_database_info_request(self, request_context: RequestContext, params: GetDatabaseInfoParameters) -> None:
        # Retrieve the connection service
        connection_service = self._service_provider[constants.CONNECTION_SERVICE_NAME]
        connection = connection_service.get_connection(params.owner_uri, ConnectionType.DEFAULT)

        # Get database info
        database_name = connection.get_dsn_parameters()['dbname']
        owner_query = 'SELECT pg_catalog.pg_get_userbyid(db.datdba) FROM pg_catalog.pg_database db WHERE db.datname = %s'
        with connection.cursor() as cursor:
            cursor.execute(owner_query, (database_name,))
            owner_result = cursor.fetchall()[0][0]

        # Set up and send the response
        options = {
            DatabaseInfo.OWNER: owner_result
        }
        request_context.send_response(GetDatabaseInfoResponse(DatabaseInfo(options)))
