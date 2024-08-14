from rest_access_policy import AccessPolicy


from .models import Store, User



# all views with permitted users in json


class ServerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["signup", "login", "verify_activation", "request_reset_password", "verify_password_reset_token", "reset_password"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": [
                "logout"
            ],
            "principal": ["authenticated"],
            "effect": "allow",
            
        },
        {
            "action": [
                "create_customers",
                "update_customer",
                "retrieve_customer",
                "ban",
                "audio_to_query",
                "create_product",
                "update_product",
                "retrieve_product",
                "delete_product"
                
                
                
                
            ],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_admin:admin",}
    
    ]

    def is_admin(self, request, view, action, field) -> bool:
        try:
            User.objects.get(pk=request.data["user"])
        except:
            return False
        return True
