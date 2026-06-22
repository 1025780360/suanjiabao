import base64
from datetime import date, timedelta

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ProfileView(APIView):
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class MembershipInfoView(APIView):
    """获取当前用户的会员信息"""
    def get(self, request):
        from .models import Membership, Subscription, UserQuota
        membership = Membership.objects.filter(user=request.user, is_active=True).select_related("tenant").first()
        if not membership:
            return Response({"detail": "未加入任何档口"}, status=404)

        tenant = membership.tenant

        # 试用到期自动降级
        if tenant.trial_ends_at and timezone.now() >= tenant.trial_ends_at and tenant.plan != "free":
            tenant.apply_plan("free")
            tenant.trial_ends_at = None
            tenant.save()

        today_quota, _ = UserQuota.objects.get_or_create(membership=membership, date=date.today())

        from costing.models import QuickStyle, QuickCategory
        style_count = QuickStyle.objects.filter(tenant=tenant, created_by=request.user).count()
        template_count = QuickCategory.objects.filter(tenant=tenant, created_by=request.user).count()

        # 到期时间
        trial_days = 0
        expire_date = ""
        # 判断是否为注册试用（没有付费订阅记录）
        has_paid = tenant.subscriptions.filter(amount__gt=0).exists()
        if tenant.trial_ends_at:
            if tenant.trial_ends_at > timezone.now():
                trial_days = max(1, (tenant.trial_ends_at - timezone.now()).days + 1)
                expire_date = (tenant.trial_ends_at + timedelta(hours=8)).strftime("%Y-%m-%d")
            else:
                expire_date = "已过期"
        is_trial = bool(tenant.trial_ends_at and tenant.trial_ends_at > timezone.now() and not has_paid)

        return Response({
            "plan": tenant.plan,
            "planLabel": dict(tenant.Plan.choices).get(tenant.plan, ""),
            "isTrial": is_trial,
            "trialDaysLeft": trial_days if is_trial else 0,
            "expireDate": expire_date,
            "styleQuota": tenant.total_style_quota,
            "styleExtra": tenant.style_extra,
            "styleUsed": style_count,
            "aiDailyQuota": tenant.total_ai_quota,
            "aiExtra": tenant.ai_extra,
            "aiUsedToday": today_quota.ai_used,
            "templateQuota": tenant.total_template_quota,
            "templateUsed": template_count,
            "canBatch": tenant.can_batch,
            "canCompare": tenant.can_compare,
            "canExport": tenant.can_export,
            "canAiPrice": tenant.can_ai_price,
            "teamSize": tenant.team_size,
        })


class UpgradePlanView(APIView):
    """提交付款申请 / 获取付款信息"""
    def _payment_qr_image(self, request, method):
        if method.qr_image_data:
            return method.qr_image_data
        if method.qr_image:
            return request.build_absolute_uri(method.qr_image.url)
        return ""

    def get(self, request):
        """获取收款方式"""
        from .models import PaymentMethod
        methods_qs = PaymentMethod.objects.filter(is_active=True)
        methods = []
        for m in methods_qs:
            methods.append({
                "id": m.id,
                "name": m.name,
                "qr_image": self._payment_qr_image(request, m),
                "instructions": m.instructions,
            })
        return Response({"methods": methods})

    def post(self, request):
        """提交付款申请 或 上传收款码"""
        from .models import Membership, PaymentMethod, PaymentRequest

        # 如果是收款码上传（有 qr_image 文件）
        if request.FILES.get("qr_image") and request.user.is_staff:
            name = request.data.get("name", "")
            instructions = request.data.get("instructions", "")
            image_file = request.FILES["qr_image"]
            content_type = image_file.content_type or "application/octet-stream"
            image_data = base64.b64encode(image_file.read()).decode("ascii")
            m = PaymentMethod.objects.create(
                name=name,
                instructions=instructions,
                qr_image_data=f"data:{content_type};base64,{image_data}",
            )
            return Response({"ok": True, "id": m.id})

        # 付款申请
        plan = request.data.get("plan")
        billing = request.data.get("billing", "monthly")
        extension = request.data.get("extension")
        from .models import Membership, PaymentRequest
        plan = request.data.get("plan")
        billing = request.data.get("billing", "monthly")
        extension = request.data.get("extension")

        membership = Membership.objects.filter(user=request.user, is_active=True).select_related("tenant").first()
        if not membership:
            return Response({"detail": "未加入任何档口"}, status=404)

        tenant = membership.tenant

        # 根据计费周期算价格
        plan_prices = {
            "pro": {"monthly": 29, "quarterly": 69, "yearly": 279},
            "ultimate": {"monthly": 69, "quarterly": 169, "yearly": 659},
        }

        if plan and plan in dict(tenant.Plan.choices):
            amount = (plan_prices.get(plan, {})).get(billing, 29)
            billing_label = {"monthly": "月付", "quarterly": "季付", "yearly": "年付"}.get(billing, "")
            PaymentRequest.objects.create(
                tenant=tenant, user=request.user, plan=plan, amount=amount,
                admin_note=billing_label,
            )
            return Response({"ok": True, "message": f"已提交{billing_label}付款申请，转账后联系管理员确认"})

        if extension:
            etype = extension.get("type")
            eamount = extension.get("amount", 0)
            amount = {"style": 10 * (eamount // 5), "ai": 8 * eamount, "template": 6 * (eamount // 2)}.get(etype, 0)
            PaymentRequest.objects.create(
                tenant=tenant, user=request.user, plan=tenant.plan, amount=amount,
                extension_type=etype, extension_amount=eamount,
            )
            return Response({"ok": True, "message": "已提交扩容申请，转账后联系管理员确认"})

        return Response({"detail": "请指定 plan 或 extension"}, status=400)

    def delete(self, request, pk=None):
        """删除收款码"""
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        from .models import PaymentMethod
        PaymentMethod.objects.filter(id=pk).delete()
        return Response({"ok": True})
