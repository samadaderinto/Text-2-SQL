from rest_access_policy import AccessPolicy


class ServerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": [
                "signup",
                "verify_activation",
                "login",
                "request_reset_password",
                "verify_password_reset_token",
                "reset_password",
                "refresh_token"
            ],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": [
                "create_customer",
                "update_customer",
                "retrieve_customer",
                "ban",
                "audio_to_query",
                "create_product",
                "update_product",
                "retrieve_product",
                "delete_product",
                "get_admin",
                "edit_admin_info",
                "update_store",
                "list_stores",
                "retrieve_store",
                "get_notification_info",
                "update_notification_info",
                "retrieve_order",
                "update_order",
                "create_order",
                "download_order",
                "delete_order",
                "logout",
                "elastic_searcher",
                "get_store",
                
                "confirm_create",
                "confirm_delete",
                "confirm_update"
                
          
            ],
            "principal": ["authenticated"],
            "effect": "allow",
        },
    ]
