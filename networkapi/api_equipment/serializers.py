# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.api_ip.serializers import Ipv4DetailsSerializer
from networkapi.api_ip.serializers import Ipv6DetailsSerializer
from networkapi.api_network.serializers import Ipv4Serializer
from networkapi.api_network.serializers import Ipv6Serializer
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import Marca
from networkapi.equipamento.models import Modelo
from networkapi.equipamento.models import TipoEquipamento
from networkapi.util.serializers import DynamicFieldsModelSerializer


class BrandDetailsSerializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = Marca
        fields = (
            'id',
            'name'
        )


class ModelDetailsSerializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    brand = serializers.SerializerMethodField('get_brand')

    def get_brand(self, obj):

        return self.extends_serializer(obj.marca, 'brand')

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'brand': {
                    'serializer': BrandDetailsSerializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'brand__details': {
                    'serializer': BrandDetailsSerializer,
                    'kwargs': {
                    }
                },
            }

        return cls.mapping

    class Meta:
        model = Modelo
        fields = (
            'id',
            'name',
            'brand'
        )

        default_fields = (
            'id',
            'name'
        )


class EquipmentTypeSerializer(DynamicFieldsModelSerializer):

    equipment_type = serializers.Field(source='tipo_equipamento')

    class Meta:
        model = TipoEquipamento
        fields = (
            'id',
            'equipment_type'
        )


class EquipmentSerializer(DynamicFieldsModelSerializer):

    equipment_type = serializers.Field(source='tipo_equipamento')
    model = serializers.Field(source='modelo')
    name = serializers.Field(source='nome')
    # groups = serializers.Field(source='grupos')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name',
            'equipment_type',
            'model'
        )


class EquipmentBasicSerializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name'
        )


class EquipmentV3Serializer(DynamicFieldsModelSerializer):

    ipv4 = serializers.SerializerMethodField('get_ipv4')

    ipv6 = serializers.SerializerMethodField('get_ipv6')

    equipment_type = serializers.SerializerMethodField('get_equipment_type')

    model = serializers.SerializerMethodField('get_model')

    name = serializers.Field(source='nome')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name',
            'equipment_type',
            'model',
            'ipv4',
            'ipv6'
        )

        default_fields = (
            'id',
            'name'
        )

    def get_model(self, obj):

        return self.extends_serializer(obj.modelo, 'model')

    def get_equipment_type(self, obj):

        return self.extends_serializer(obj.tipo_equipamento, 'equipment_type')

    def get_ipv4(self, obj):
        ips = obj.ipequipamento_set.all()
        ips = [ip.ip for ip in ips]

        return self.extends_serializer(ips, 'ipv4')

    def get_ipv6(self, obj):
        ips = obj.ipv6equipament_set.all()
        ips = [ip.ip for ip in ips]

        return self.extends_serializer(ips, 'ipv6')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'ipv4': self.setup_eager_loading_ipv4,
            'ipv6': self.setup_eager_loading_ipv6
        }

        return mapping

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'model': {
                    'serializer': ModelDetailsSerializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'equipment_type': {
                    'serializer': EquipmentTypeSerializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'ipv4': {
                    'serializer': Ipv4Serializer,
                    'kwargs': {
                        'many': True,
                    }
                },
                'ipv6': {
                    'serializer': Ipv6Serializer,
                    'kwargs': {
                        'many': True,
                    }
                },
                'ipv4__details': {
                    'serializer': Ipv4DetailsSerializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv4',)
                    }
                },
                'ipv6__details': {
                    'serializer': Ipv6DetailsSerializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv6',)
                    }
                },
                'equipment_type__details': {
                    'serializer': EquipmentTypeSerializer,
                    'kwargs': {
                    }
                },
                'model__details': {
                    'serializer': ModelDetailsSerializer,
                    'kwargs': {

                    }
                }
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_ipv4(queryset):
        queryset = queryset.prefetch_related(
            'ipequipamento_set',
            'ipequipamento_set__ip',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ipv6(queryset):
        queryset = queryset.prefetch_related(
            'ipv6equipament_set',
            'ipv6equipament_set__ip',
        )
        return queryset
