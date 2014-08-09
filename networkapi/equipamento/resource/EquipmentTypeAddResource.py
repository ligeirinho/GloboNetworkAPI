# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads, XMLError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_regex
from networkapi.equipamento.models import TipoEquipamento, EquipamentoError, TipoEquipamentoDuplicateNameError


class EquipmentTypeAddResource(RestResource):

    log = Log('EquipmentTypeAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert a Equipment Type.

        URL: equipmenttype/
        """

        try:

            self.log.info("Add Equipment Script")

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            equipment_type_map = networkapi_map.get('equipment_type')
            if equipment_type_map is None:
                msg = u'There is no value to the equipment_type tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            name = equipment_type_map.get('name')

            # Valid Name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100) or not is_valid_regex(name, "^[A-Za-z0-9 -]+$"):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Business Rules
            equipment_type = TipoEquipamento()

            # save Equipment Type
            equipment_type.insert_new(user, name)

            etype_dict = dict()
            etype_dict['id'] = equipment_type.id

            return self.response(dumps_networkapi({'equipment_type': etype_dict}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except TipoEquipamentoDuplicateNameError, e:
            return self.response_error(312, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError, e:
            return self.response_error(1)

        except XMLError, e:
            return self.response_error(1)
