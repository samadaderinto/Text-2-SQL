from rest_access_policy import AccessPolicy


from .models import Store, User



# all views with permitted users in json


class ServerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": [
             "AuthViewSet",
             'ProductViewSet',
             'OrderViewSet'
                
            ],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": [
                'QueryService',
                'CustomerViewSet',
                'SettingsViewSet'
            ],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_admin:admin",
        }
    
    ]

    def is_admin(self, request, view, action, field) -> bool:
        try:
            User.objects.get(pk=request.data["user"])
        except:
            return False
        return True
