import datetime

from django.utils.deprecation import MiddlewareMixin


class UserStatusAuth(MiddlewareMixin):
    def process_request(self,request):
        from django.contrib.auth.models import AnonymousUser
        if isinstance(request.user,AnonymousUser):
            return
        else:
            from web.models import Transaction, UserInfo
            user_id = request.user.id
            user_obj = UserInfo.objects.filter(id=user_id).first()
            transacs=Transaction.objects.filter(user=user_obj).order_by('-price_policy__id')
            #can I order the results by a field in the foreign table?Let's try it.
            #Yes,we can
            for transac in transacs:
                # we store the object pricepolicy to the attribute of request.user.status
                if transac.end_time > datetime.datetime.now() or transac.end_time is None:
                    request.user.status = transac.price_policy
                    break
            return
            #consider this case: if a user is in the status of pripol2, but he want to upgrade
            #his priviledge to pripol3, So the transaction will have two inexpiry entries and how
            #the hell we should do?
            #when he upgrade his pripol to 3,the endtime of pripol should be extended