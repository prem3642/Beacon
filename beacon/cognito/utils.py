# -*- coding: utf-8 -*-
# Third Party Stuff
from pycognito import Cognito, dict_to_cognito


class CustomCognito(Cognito):
    """
    Adding some extra methods that are not available
    """

    def resend_confirmation_code(self):
        """
        Sends a verification code to the user to confirm verification.
        """
        params = {"ClientId": self.client_id, "Username": self.username}
        self._add_secret_hash(params, "SecretHash")
        self.client.resend_confirmation_code(**params)

    def admin_disable_user(self):
        """
        Marks the user as disabled on Cognito
        """
        self.client.admin_disable_user(
            UserPoolId=self.user_pool_id, Username=self.username
        )

    def admin_enable_user(self):
        """
        Marks the user as enabled on Cognito
        """
        self.client.admin_enable_user(
            UserPoolId=self.user_pool_id, Username=self.username
        )

    def admin_update_profile_with_email_verified(
        self, attrs, is_email_updated=False, attr_map=None
    ):
        """
        Marks the user as enabled on Cognito
        """
        user_attrs = dict_to_cognito(attrs, attr_map)
        if is_email_updated is True:
            user_attrs.append({"Name": "email_verified", "Value": "true"})
        self.client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=self.username,
            UserAttributes=user_attrs,
        )
