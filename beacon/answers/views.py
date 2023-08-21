# -*- coding: utf-8 -*-
# Third Party Stuff
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View
from requests.exceptions import RequestException
from rest_framework.exceptions import ValidationError

# beacon Stuff
from beacon.users.services import get_bwb_data
from beacon.users.utils import get_relationship_from_user, send_f2f_data_to_bwb_server

from .models import UserAppointment


@method_decorator(staff_member_required, name="dispatch")
class ResendF2FAppointmentDataView(View):
    appointment_detail_url = "/admin/answers/userappointment/{id}/change/"
    appointment_list_url = "/admin/answers/userappointment/"

    def get(self, request, *args, **kwargs):
        appointment_id = self.kwargs.get("pk")
        appointment = UserAppointment.objects.filter(id=appointment_id).first()
        success_url = self.appointment_detail_url.format(id=appointment_id)
        if appointment is None:
            messages.error(request, "User Appointment with this id does not exists!")
            success_url = self.appointment_list_url
        else:
            if appointment.appointment_method == UserAppointment.FACE_TO_FACE:
                user = appointment.user_response.user
                if user:
                    relationship = get_relationship_from_user(user)
                    bwb_data = get_bwb_data(
                        user.__dict__,
                        str(user.id),
                        str(user.mdlive_id),
                        relationship,
                        appointment.user_response,
                        appointment,
                        user.organisation,
                    )
                    try:
                        response = send_f2f_data_to_bwb_server(
                            str(appointment.id), bwb_data
                        )
                        messages.success(
                            request,
                            f"Data sent successfully with inquiry id: {response}",
                        )
                    except RequestException as e:
                        messages.error(request, f"Error in sending data: {e}")
                    except ValidationError as e:
                        messages.error(request, f"Error in sending data: {e}")
                else:
                    messages.error(
                        request, "User is not attached with this appointment!"
                    )
            else:
                messages.error(
                    request, "User Appointment is not a face to face appointment!"
                )
        return HttpResponseRedirect(success_url)
