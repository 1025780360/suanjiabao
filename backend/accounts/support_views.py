from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Membership, PaymentRequest, SupportMessage, SupportRoom, Tenant


class SupportChatView(APIView):
    """客服聊天：获取消息 / 发送消息"""

    def get_room(self, user):
        membership = Membership.objects.filter(user=user, is_active=True).select_related("tenant").first()
        if not membership or not membership.tenant:
            return None
        room, _ = SupportRoom.objects.get_or_create(
            tenant=membership.tenant,
            defaults={"user": user},
        )
        return room

    def get(self, request):
        room = self.get_room(request.user)
        if not room:
            return Response({"messages": []})
        msgs = room.messages.order_by("-created_at")[:50]
        data = [{
            "id": m.id,
            "content": m.content,
            "isStaff": m.is_staff,
            "createdAt": (m.created_at + timedelta(hours=8)).strftime("%H:%M"),
        } for m in reversed(msgs)]
        return Response({"messages": data, "roomId": room.id})

    def post(self, request):
        room = self.get_room(request.user)
        if not room:
            return Response({"detail": "未加入档口"}, status=400)
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"detail": "消息不能为空"}, status=400)
        msg = SupportMessage.objects.create(
            room=room, sender=request.user, content=content, is_staff=False,
        )
        room.updated_at = timezone.now()
        room.save()
        return Response({"ok": True, "id": msg.id})


class SupportPendingPaymentsView(APIView):
    """客服查看待确认付款"""

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        pending = PaymentRequest.objects.filter(status="pending").select_related("tenant", "user").order_by("-created_at")[:20]
        data = [{
            "id": p.id,
            "tenant": p.tenant.name,
            "plan": p.get_plan_display(),
            "amount": f"¥{int(p.amount)}",
            "extension": p.extension_type and f"{p.extension_type}+{p.extension_amount}",
            "createdAt": (p.created_at + timedelta(hours=8)).strftime("%m-%d %H:%M"),
        } for p in pending]
        return Response({"payments": data})

    def post(self, request):
        """确认到账"""
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        pid = request.data.get("id")
        try:
            pr = PaymentRequest.objects.get(id=pid, status="pending")
            pr.confirm()
            return Response({"ok": True})
        except PaymentRequest.DoesNotExist:
            return Response({"detail": "未找到"}, status=404)


class SupportRoomListView(APIView):
    """客服查看所有聊天室"""

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        rooms = SupportRoom.objects.filter(is_active=True).select_related("tenant", "user").order_by("-updated_at")[:20]
        data = [{
            "id": r.id,
            "tenant": r.tenant.name,
            "user": r.user.display_name or r.user.username,
            "updatedAt": r.updated_at.strftime("%m-%d %H:%M"),
        } for r in rooms]
        return Response({"rooms": data})


class SupportStaffChatView(APIView):
    """客服发送消息 / 查看某个聊天室"""

    def get(self, request, room_id):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        try:
            room = SupportRoom.objects.get(id=room_id)
        except SupportRoom.DoesNotExist:
            return Response({"messages": []})
        msgs = room.messages.order_by("-created_at")[:50]
        data = [{
            "id": m.id,
            "content": m.content,
            "isStaff": m.is_staff,
            "createdAt": (m.created_at + timedelta(hours=8)).strftime("%H:%M"),
        } for m in reversed(msgs)]
        return Response({"messages": data, "tenant": room.tenant.name})

    def post(self, request, room_id):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"detail": "消息不能为空"}, status=400)
        try:
            room = SupportRoom.objects.get(id=room_id)
        except SupportRoom.DoesNotExist:
            return Response({"detail": "聊天室不存在"}, status=404)
        msg = SupportMessage.objects.create(
            room=room, sender=request.user, content=content, is_staff=True,
        )
        room.updated_at = timezone.now()
        room.save()
        return Response({"ok": True, "id": msg.id})


class SupportMembersView(APIView):
    """客服管理用户会员"""

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        tenants = Tenant.objects.all().order_by("-created_at")
        data = []
        for t in tenants:
            owner = t.memberships.filter(role="owner").select_related("user").first()
            trial_info = ""
            if t.trial_ends_at:
                if t.trial_ends_at > timezone.now():
                    days = (t.trial_ends_at - timezone.now()).days + 1
                    trial_info = f"试用剩余{days}天"
                else:
                    trial_info = "试用已过期"
            data.append({
                "id": t.id,
                "name": t.name,
                "owner": owner.user.display_name or owner.user.username if owner else "-",
                "plan": t.get_plan_display(),
                "planKey": t.plan,
                "trialInfo": trial_info,
                "styleUsed": t.created_quickstyle_set.count() if hasattr(t, 'created_quickstyle_set') else 0,
                "createdAt": (t.created_at + timedelta(hours=8)).strftime("%Y-%m-%d"),
            })
        return Response({"members": data})

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "无权限"}, status=403)
        tid = request.data.get("id")
        plan = request.data.get("plan")
        try:
            t = Tenant.objects.get(id=tid)
            t.apply_plan(plan)
            t.trial_ends_at = None  # 手动设置后取消试用状态
            t.save()
            from .models import Subscription
            Subscription.objects.create(tenant=t, plan=plan, amount=0)
            return Response({"ok": True})
        except Tenant.DoesNotExist:
            return Response({"detail": "未找到"}, status=404)
