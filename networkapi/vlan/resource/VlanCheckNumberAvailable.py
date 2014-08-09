# -*- coding:utf-8 -*-
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.log import Log
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError

import logging
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError, \
    AmbienteError
from networkapi.vlan.models import Vlan, VlanNotFoundError
from networkapi.settings import MIN_VLAN_NUMBER_01, MAX_VLAN_NUMBER_01, \
    MIN_VLAN_NUMBER_02, MAX_VLAN_NUMBER_02

logger = logging.getLogger('VlanCheckNumberAvailable')


class VlanCheckNumberAvailable(RestResource):

    log = Log('VlanCheckNumberAvailable')

    def handle_get(self, request, user, *args, **kwargs):
        """Handle GET requests to check if environment has a number available.

        URLs: /vlan/check_number_available/<environment>/<num_vlan>/
        """
        try:
            id_env = kwargs.get('id_environment')
            num_vlan = kwargs.get('num_vlan')
            id_vlan = kwargs.get('id_vlan')

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid env ID
            if not is_valid_int_greater_zero_param(id_env):
                self.log.error(
                    u'The id_env parameter is not a valid value: %s.', id_env)
                raise InvalidValueError(None, 'env_id', id_env)

            # Valid num Vlan
            if not is_valid_int_greater_zero_param(num_vlan):
                self.log.error(
                    u'The num_vlan parameter is not a valid value: %s.', num_vlan)
                raise InvalidValueError(None, 'num_vlan', id_env)
            else:
                num_vlan = int(num_vlan)

            if is_valid_int_greater_zero_param(id_vlan):
                vlan_to_edit = Vlan().get_by_pk(id_vlan)
                if vlan_to_edit.num_vlan == num_vlan:
                    return self.response(dumps_networkapi({'has_numbers_availables': True}))

            environment = Ambiente().get_by_pk(id_env)
            vlan = Vlan()
            vlan.ambiente = environment

            # Check if environment has min/max num_vlan value or use the value
            # that was configured in settings
            if (vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1) or (vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2):
                min_num_01 = vlan.ambiente.min_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.min_num_vlan_2
                max_num_01 = vlan.ambiente.max_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.max_num_vlan_2
                min_num_02 = vlan.ambiente.min_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.min_num_vlan_1
                max_num_02 = vlan.ambiente.max_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.max_num_vlan_1
            else:
                min_num_01 = MIN_VLAN_NUMBER_01
                max_num_01 = MAX_VLAN_NUMBER_01
                min_num_02 = MIN_VLAN_NUMBER_02
                max_num_02 = MAX_VLAN_NUMBER_02

            has_numbers_availables = False
            availables_numbers = vlan.calculate_vlan_number(
                min_num_01, max_num_01, True)
            if num_vlan not in availables_numbers:
                availables_numbers = vlan.calculate_vlan_number(
                    min_num_02, max_num_02, True)
                if num_vlan in availables_numbers:
                    has_numbers_availables = True
            else:
                has_numbers_availables = True

            if Vlan.objects.filter(num_vlan=num_vlan, ambiente=environment):
                has_numbers_availables = True

            return self.response(dumps_networkapi({'has_numbers_availables': has_numbers_availables}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except VlanNotFoundError, e:
            return self.response_error(116)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except AmbienteNotFoundError:
            return self.response_error(112)
        except Exception:
            return self.response_error(1)
