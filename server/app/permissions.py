from rest_access_policy import AccessPolicy


from app.models import Store



# all views with permitted users in json


class ServerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": [
             
                "create_user",
                "landing_page_products",
                "ProductImageViewSet",
                "get_product_reviews",
                "redirect_url",
                "specification",
                "<method:get>",
            ],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": [
               
            ],
            "principal": ["admin"],
            "effect": "allow",
        },
        {
            "action": [
                
            ],
            "principal": ["staff"],
            "effect": "allow",
        },
        {
            "action": [
                "stores",
                "IsOwnerSearchProduct",
                "ProductAPIView",
            ],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_store_owner:owner",
        },
        {
            "action": [
                
            ],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_marketer:owner",
        },
        {
            "action": [
               "UserViewSet",
               "wishlistViewSet",
               "reviews",
               "recent",
               "Orders",
               "address",
               "request_refund",
               "UserLogout",
               "create_checkout_session",
               "capture_checkout_session",
            ],
            "principal": "authenticated",
            "effect": "allow",
        },


    ]

    def is_store_owner(self, request, view, action, field) -> bool:
        try:
            Store.objects.get(pk=request.data["store"])
        except:
            return False
        return True
