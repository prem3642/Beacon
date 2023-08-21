# -*- coding: utf-8 -*-
# Third Party Stuff
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.viewsets import GenericViewSet

# beacon Stuff
from beacon.base import response

from . import permissions, services
from .serializers import SCCUserForceSyncSerializer, SCCUserSyncSerializer

User = get_user_model()
log = logging.getLogger(__name__)


class SCCSyncViewSet(GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.SCCAccess,)

    # Making auth classes None to run only permission classes
    def get_authenticators(self):
        return list()

    @action(methods=["POST"], detail=False, url_path="sync")
    def sync(self, request):
        try:
            data=request.data
            data['providerId']="959422"
            data['vendorId']="E970051"
            log.info(f"SCC Sync API Request Body Received: {data}")
            serializer = SCCUserSyncSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            bwb_data = services.convert_scc_data_into_bwb_format(
                serializer.validated_data
            )
            user_id, diff = services.process_user_sync_request(bwb_data)
            response_message = {"message": "User synced successfully"}
            services.create_scc_api_log(
                user_id=user_id,
                request=data,
                response=response_message,
                is_successful=True,
                is_incoming=True,
                change_diff=diff,
            )
            return response.Ok(response_message)
        except (ValidationError, APIException) as e:
            # Sending `None` to user_id because sync API doesn't necessarily act upon
            # one user instance as it is detail=False. Also, the API fails in scenarios
            # when no exact user is found matched with the request data. Either way,
            # failure of this API can't be associated to an individual user instance.
            data=request.data
            data['providerId']="959422"
            data['vendorId']="E970051"
            services.create_scc_api_log(
                user_id=None,
                request=data,
                response=e.detail,
                is_successful=False,
                is_incoming=True,
                change_diff=None,
            )
            raise e

    # It is a PATCH request, but its method has been changed to PUT, because SCC
    # system wasn't compatible with PATCH HTTP requests.
    @action(methods=["PUT"], detail=True, url_path="force-sync")
    def force_sync(self, request, pk):
        log.info(f"SCC Force Sync API Request Body Received: {request.data}")
        instance = self.get_object()
        try:
            data=request.data
            data['providerId']="959422"
            data['vendorId']="E970051"
            serializer = SCCUserForceSyncSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            bwb_data = services.convert_scc_data_into_bwb_format(
                serializer.validated_data
            )
            change_diff = services.force_save_user_data(instance, bwb_data)
            response_message = {"message": "User updated successfully"}
            services.create_scc_api_log(
                instance.id,
                request=data,
                response=response_message,
                is_successful=True,
                is_incoming=True,
                change_diff=change_diff,
            )
            return response.Ok(response_message)
        except (ValidationError, APIException) as e:
            data=request.data
            data['providerId']="959422"
            data['vendorId']="E970051"
            services.create_scc_api_log(
                user_id=instance.id,
                request=data,
                response=e.detail,
                is_successful=False,
                is_incoming=True,
                change_diff=None,
            )
            raise e
