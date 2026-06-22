import json
import math
import re
import urllib.error
import urllib.request

from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.models import Membership

from .models import AiChatMessage, AiProviderSetting, QuickCategory, QuickStyle
from .serializers import AiChatMessageSerializer, QuickCategorySerializer, QuickStyleSerializer

MAX_AI_CHAT_MESSAGES = 80


def get_current_tenant(user):
    membership = Membership.objects.filter(user=user, is_active=True).select_related("tenant").first()
    if membership:
        return membership.tenant
    return None


class TenantUserQuerysetMixin:
    def get_tenant(self):
        return get_current_tenant(self.request.user)

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return self.model.objects.none()
        return self.model.objects.filter(tenant=tenant, created_by=self.request.user)

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        serializer.save(tenant=tenant, created_by=self.request.user)


class QuickCategoryListCreateView(TenantUserQuerysetMixin, generics.ListCreateAPIView):
    model = QuickCategory
    serializer_class = QuickCategorySerializer


class QuickCategoryDeleteView(TenantUserQuerysetMixin, generics.DestroyAPIView):
    model = QuickCategory
    serializer_class = QuickCategorySerializer
    lookup_field = 'key'


class QuickStyleListCreateView(TenantUserQuerysetMixin, generics.ListCreateAPIView):
    model = QuickStyle
    serializer_class = QuickStyleSerializer

    def create(self, request, *args, **kwargs):
        tenant = self.get_tenant()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get("name")
        existing = QuickStyle.objects.filter(tenant=tenant, created_by=self.request.user, name=name).first()
        if existing:
            instance = serializer.update(existing, serializer.validated_data)
            return Response(self.get_serializer(instance).data)
        else:
            instance = serializer.save(tenant=tenant, created_by=self.request.user)
            return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)


class QuickStyleDeleteView(TenantUserQuerysetMixin, generics.RetrieveDestroyAPIView):
    model = QuickStyle
    serializer_class = QuickStyleSerializer


class AiChatHistoryView(TenantUserQuerysetMixin, generics.ListAPIView):
    model = AiChatMessage
    serializer_class = AiChatMessageSerializer
    pagination_class = None

    def get_queryset(self):
        tenant = self.get_tenant()
        if not tenant:
            return AiChatMessage.objects.none()
        ids = list(
            AiChatMessage.objects.filter(tenant=tenant, created_by=self.request.user)
            .order_by("-created_at")
            .values_list("id", flat=True)[:MAX_AI_CHAT_MESSAGES]
        )
        return AiChatMessage.objects.filter(id__in=ids).order_by("created_at")


def prune_ai_chat_history(tenant, user):
    queryset = AiChatMessage.objects.filter(tenant=tenant, created_by=user).order_by("-created_at")
    keep_ids = list(queryset.values_list("id", flat=True)[:MAX_AI_CHAT_MESSAGES])
    if keep_ids:
        AiChatMessage.objects.filter(tenant=tenant, created_by=user).exclude(id__in=keep_ids).delete()


def round_money(value):
    return round(float(value or 0), 2)


def first_number(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def detect_category(text):
    if re.search(r"短袖|t恤|T恤|体恤|tee", text, re.IGNORECASE):
        return "T恤"
    if "卫衣" in text:
        return "卫衣"
    if "裤" in text:
        return "裤子"
    if "裙" in text:
        return "连衣裙"
    if "外套" in text or "夹克" in text:
        return "外套"
    return ""


def detect_style_name(text, current_name=""):
    match = re.search(r"(?:创建|新建|建|新增|录入|保存|算|做|报价|帮我算)(?:一款|一件|一个|这件|款式)?\s*([^，。,.；;]+)", text)
    if match:
        name = match.group(1).strip()
        name = re.split(r"面料|车缝|加工|吊牌|胶袋|辅料|包装|想赚|利润|客户要|做\d+", name)[0].strip()
        if name and not re.search(r"改成|改一下|多少钱|多少|成本|报价|算价|利润", name):
            return name[:30]
    return current_name or ""


def detect_intent(text, draft):
    cost_words = r"算|成本|报价|利润|面料|用量|加工|车缝|裁剪|印花|辅料|包装|损耗|想赚|客户要|改成|改为"
    create_words = r"创建|新建|建款|建一个|建一款|新增|录入|保存款式|款式"
    if re.search(cost_words, text):
        return "costing"
    if re.search(create_words, text):
        return "style"
    if draft.get("fabrics") or draft.get("processes"):
        return "costing"
    return "assistant"


def explicit_create_requested(text):
    return bool(re.search(r"创建|新建|建款|建一款|建一个|新增款式|录入款式|帮我建", text))


def import_existing_style_requested(text):
    return bool(re.search(r"导入|选择|打开|用已有|已有款式|现有款式", text))


def has_cost_signal(draft):
    has_fabric = bool(draft.get("fabrics")) and any(
        float(item.get("price") or 0) > 0 or float(item.get("usage") or 0) > 0
        for item in draft.get("fabrics", [])
    )
    has_process = bool(draft.get("processes")) and any(float(item.get("fee") or 0) > 0 for item in draft.get("processes", []))
    return has_fabric or has_process or draft.get("expectedProfit") not in [None, ""]


def creation_missing_questions(draft):
    field, question = creation_missing_info(draft)
    return [question] if question else []


def creation_missing_info(draft):
    if not draft.get("styleName"):
        return "styleName", "老板，这款叫什么名字？比如：牛仔外套、纯棉短袖。"
    if not draft.get("category") or draft.get("category") == "未确定":
        return "category", "这款属于什么品类？比如 T 恤、卫衣、裤子、连衣裙、外套。"
    fabrics = draft.get("fabrics") or []
    first_fabric = fabrics[0] if fabrics else {}
    if not fabrics or not first_fabric.get("price"):
        return "fabricPrice", "面料单价多少？你可以直接回：26一公斤，或者 18一米。"
    if not first_fabric.get("usage"):
        return "fabricUsage", "一件大概用多少面料？你可以回：180克、0.18公斤，或者 1.2米。"
    processes = draft.get("processes") or []
    first_process = processes[0] if processes else {}
    if not processes or not first_process.get("fee"):
        return "processFee", "加工费大概多少钱一件？你可以直接回：7。"
    if draft.get("expectedProfit") in [None, ""]:
        return "expectedProfit", "老板，这款你想一件赚多少钱？你可以直接回：8。"
    return "", ""


def apply_short_answer_to_last_question(message, draft):
    text = str(message or "").strip()
    field = draft.get("_lastMissingField")
    if field == "styleName" and text and not re.search(r"面料|用量|加工|车缝|辅料|包装|利润|想赚|多少钱", text):
        draft["styleName"] = text[:30]
        if not draft.get("category") or draft.get("category") == "未确定":
            draft["category"] = detect_category(text) or draft.get("category") or "未确定"
        return draft
    if field == "category":
        category = detect_category(text)
        if category:
            draft["category"] = category
        return draft
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        return draft
    value = float(text)
    if field == "fabricPrice":
        fabric = draft["fabrics"][0] if draft.get("fabrics") else {
            "name": draft.get("styleName") or "主面料",
            "price": 0,
            "priceUnit": "kg",
            "usage": 0,
            "usageUnit": "kg",
            "lossRate": 0.05,
        }
        fabric["price"] = value
        draft["fabrics"] = [fabric, *draft.get("fabrics", [])[1:]]
    elif field == "processFee":
        process = draft["processes"][0] if draft.get("processes") else {"name": "加工", "fee": 0}
        process["fee"] = value
        draft["processes"] = [process, *draft.get("processes", [])[1:]]
    elif field == "expectedProfit":
        draft["expectedProfit"] = value
    elif field == "quantity":
        draft["quantity"] = int(value)
    return draft


def usage_from_text(text):
    match = re.search(r"一件(?:大概|约|用|要|耗)\s*(\d+(?:\.\d+)?)\s*(克|g|公斤|斤|kg|米|m)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"用量\s*(\d+(?:\.\d+)?)\s*(克|g|公斤|斤|kg|米|m)", text, re.IGNORECASE)
    if not match:
        match = re.search(r"^(\d+(?:\.\d+)?)\s*(克|g|公斤|斤|kg|米|m)$", text.strip(), re.IGNORECASE)
    if not match:
        return None, ""
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit in ["克", "g"]:
        return value / 1000, "kg"
    if unit == "斤":
        return value * 0.5, "kg"
    if unit in ["公斤", "kg"]:
        return value, "kg"
    return value, "m"


def parse_cost_draft(message, previous):
    draft = {
        "styleName": "",
        "category": "",
        "fabrics": [],
        "processes": [],
        "accessoryPack": 2.2,
        "expectedProfit": None,
        "quantity": 100,
        **(previous or {}),
    }
    draft["fabrics"] = [dict(item) for item in draft.get("fabrics", [])]
    draft["processes"] = [dict(item) for item in draft.get("processes", [])]

    text = message.strip()
    style_name = detect_style_name(text, draft.get("styleName", ""))
    if style_name:
        draft["styleName"] = style_name

    category = detect_category(text)
    if category:
        draft["category"] = category

    quantity = first_number(text, [r"客户要\s*(\d+(?:\.\d+)?)\s*件", r"做\s*(\d+(?:\.\d+)?)\s*件"])
    if quantity:
        draft["quantity"] = int(quantity)

    loss_rate = first_number(text, [r"损耗(?:率)?(?:改成|按|用|是)?\s*(\d+(?:\.\d+)?)\s*%"])
    if loss_rate is not None:
        loss_rate = loss_rate / 100

    fabric_price = first_number(text, [
        r"面料\s*(\d+(?:\.\d+)?)\s*(?:元|块)?\s*(?:一|/)?\s*(?:公斤|kg|米|m)",
        r"面料(?:单价|价格)?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:元|块)?\s*(?:一|/)?\s*(?:公斤|kg)",
    ])
    usage, usage_unit = usage_from_text(text)
    if fabric_price is not None or usage is not None or loss_rate is not None:
        fabric = draft["fabrics"][0] if draft["fabrics"] else {
            "name": draft.get("styleName") or "主面料",
            "price": 0,
            "priceUnit": "kg",
            "usage": 0,
            "usageUnit": "kg",
            "lossRate": 0.05,
        }
        if fabric_price is not None:
            fabric["price"] = fabric_price
        if usage is not None:
            fabric["usage"] = round_money(usage)
            fabric["usageUnit"] = usage_unit
        if loss_rate is not None:
            fabric["lossRate"] = loss_rate
        else:
            fabric.setdefault("lossRate", 0.05)
        if not draft["fabrics"]:
            draft["fabrics"].append(fabric)

    process_fee = first_number(text, [
        r"(?:加工费|加工|车缝|裁剪|印花|整烫)(?:改成|改为|是|费|费用)?\s*(\d+(?:\.\d+)?)",
    ])
    if process_fee is not None:
        process_name = "车缝"
        for name in ["车缝", "裁剪", "印花", "整烫", "洗水", "加工"]:
            if name in text:
                process_name = "加工" if name == "加工" else name
                break
        existing = draft["processes"][0] if draft["processes"] else None
        if existing:
            existing["name"] = existing.get("name") or process_name
            existing["fee"] = process_fee
        else:
            draft["processes"].append({"name": process_name, "fee": process_fee})

    accessory = first_number(text, [r"(?:辅料|包装|吊牌|胶袋|主唛)[^0-9]{0,8}(\d+(?:\.\d+)?)"])
    if accessory is not None:
        draft["accessoryPack"] = accessory

    profit = first_number(text, [r"(?:想赚|赚|利润)(?:一件)?(?:改成|改为|是)?\s*(\d+(?:\.\d+)?)"])
    if profit is not None:
        draft["expectedProfit"] = profit

    if not draft.get("category"):
        draft["category"] = detect_category(draft.get("styleName", "")) or "未确定"

    return draft


def calculate_cost(draft):
    fabrics = draft.get("fabrics", [])
    fabric_cost = sum(
        float(item.get("price") or 0) * float(item.get("usage") or 0) * (1 + float(item.get("lossRate", 0.05) or 0))
        for item in fabrics
    )
    process_cost = sum(float(item.get("fee") or 0) for item in draft.get("processes", []))
    accessory_cost = float(draft.get("accessoryPack") or 2.2)
    other_cost = 1.6
    single_cost = fabric_cost + process_cost + accessory_cost + other_cost
    expected_profit = float(draft.get("expectedProfit") or 0)
    suggested_price = math.ceil(single_cost + expected_profit)
    minimum_price = math.ceil(single_cost * 1.18)
    single_profit = suggested_price - single_cost
    quantity = int(draft.get("quantity") or 100)
    return {
        "fabricCost": round_money(fabric_cost),
        "processCost": round_money(process_cost),
        "accessoryCost": round_money(accessory_cost),
        "otherCost": round_money(other_cost),
        "singleCost": round_money(single_cost),
        "suggestedPrice": suggested_price,
        "minimumPrice": minimum_price,
        "singleProfit": round_money(single_profit),
        "profitFor100": round_money(single_profit * 100),
        "profitFor500": round_money(single_profit * 500),
        "profitForQuantity": round_money(single_profit * quantity),
    }


def build_reply(draft, calculation, missing, changed_text="", intent="costing", ready_to_save=False):
    if missing:
        return "老板，还差一个关键数：" + missing[0]
    if ready_to_save:
        if calculation:
            return (
                f"这款资料齐了：{draft.get('styleName') or '这款'}。\n"
                f"单件成本约 {calculation['singleCost']} 元，建议报价 {calculation['suggestedPrice']} 元。\n"
                "你确认没问题，就点下面保存为款式。"
            )
        return f"这款资料齐了：{draft.get('styleName') or '这款'}。你确认没问题，就点下面保存为款式。"
    if intent in ["style", "assistant"] and not has_cost_signal(draft):
        name = draft.get("styleName") or "这款"
        category = draft.get("category") or "未确定"
        return f"可以，先按{name}来记。\n品类：{category}。\n接下来我会问几个关键数，资料齐了再让你保存。"
    lines = [
        f"已算好：{draft.get('styleName') or '这款'}，单件成本约 {calculation['singleCost']} 元。",
        f"建议报价 {calculation['suggestedPrice']} 元，最低别低于 {calculation['minimumPrice']} 元。",
        f"做 100 件预计赚 {calculation['profitFor100']} 元，做 500 件预计赚 {calculation['profitFor500']} 元。",
    ]
    if changed_text:
        lines.insert(0, changed_text)
    lines.append("低于最低接单价不建议接，容易忙完没利润。")
    return "\n".join(lines)


AI_SYSTEM_PROMPT = """
你是服装档口 AI 助手，服务广州服装档口老板和中小服装工厂老板。回复要像微信聊天，简短自然，一句两句说清楚。

你必须只输出 JSON：
{
  "reply": "给老板的回复",
  "intent": "assistant",
  "needMoreInfo": false,
  "readyToSave": false,
  "costDraft": {}
}

核心原则：
- 默认 intent=assistant，costDraft={}。不要主动建款或追问成本。
- 老板明确说「建款/新建/算成本/报价/这款多少钱」才进入工作模式。
- 老板说「算了/不弄了/取消/不管了」立刻清空 costDraft，轻松回应。
- 能用现有信息直接回答就直接回答，别追问。
- 对话历史里老板已经给过的信息不要再问。
- 老板只说「帮我看看」「这个怎么样」这种模糊话，就简短回答功能介绍，别追问数据。

只有老板明确要建款或算成本时：
- 把他说的信息记到 costDraft（款名、面料、加工费、利润等）
- 真缺关键信息时才问一个，别连环追问
- 能从上下文猜的就用默认值：损耗 0.05、辅料 2.2、数量 100
- 资料齐了 readyToSave=true
"""


def compact_style_for_ai(style):
    return {
        "styleName": style.get("name") or style.get("styleName") or "",
        "category": style.get("category") or "",
        "fabrics": style.get("fabrics") or [],
        "processes": style.get("processes") or [],
        "accessoryPack": style.get("accessoryPack") or style.get("accessory_pack") or 2.2,
        "expectedProfit": style.get("expectedProfit") or style.get("expected_profit"),
        "quantity": style.get("quantity") or 100,
    }


def get_ai_provider_config():
    config = AiProviderSetting.objects.filter(provider="deepseek", is_active=True).order_by("-updated_at").first()
    if config and config.api_key:
        return {
            "api_key": config.api_key,
            "base_url": config.base_url,
            "model": config.model,
        }
    if settings.DEEPSEEK_API_KEY:
        return {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "model": settings.DEEPSEEK_MODEL,
        }
    raise RuntimeError("请先在后台的 AI 助手配置里填写 DeepSeek API 密钥")


def call_deepseek_assistant(message, context):
    provider = get_ai_provider_config()

    existing_styles = [compact_style_for_ai(item) for item in context.get("existingStyles", [])[:30]]
    selected_styles = [compact_style_for_ai(item) for item in context.get("selectedStyles", [])[:10]]
    has_selected = bool(context.get("hasSelectedStyles")) or len(selected_styles) > 0
    recent_messages = (context.get("recentMessages") or [])[-12:]
    payload = {
        "model": provider["model"],
        "messages": [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "message": message,
                        "hasSelectedStyles": has_selected,
                        "lastCostDraft": context.get("lastCostDraft") or {},
                        "selectedStyles": selected_styles,
                        "recentMessages": recent_messages,
                        "existingStyles": existing_styles,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
        "stream": False,
    }
    url = provider["base_url"].rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {provider['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"DeepSeek request failed: {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DeepSeek request failed: {exc.reason}") from exc

    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


def normalize_ai_payload(payload, previous, message=""):
    draft = {
        "styleName": "",
        "category": "",
        "fabrics": [],
        "processes": [],
        "accessoryPack": 2.2,
        "expectedProfit": None,
        "quantity": 100,
        **(previous or {}),
        **(payload.get("costDraft") or {}),
    }
    draft["fabrics"] = [dict(item) for item in draft.get("fabrics", []) if isinstance(item, dict)]
    draft["processes"] = [dict(item) for item in draft.get("processes", []) if isinstance(item, dict)]
    for item in draft["fabrics"]:
        item.setdefault("name", draft.get("styleName") or "主面料")
        item.setdefault("price", 0)
        item.setdefault("priceUnit", "kg")
        item.setdefault("usage", 0)
        item.setdefault("usageUnit", "kg")
        item.setdefault("lossRate", 0.05)
    for item in draft["processes"]:
        item.setdefault("name", "加工")
        item.setdefault("fee", 0)
    if not draft.get("category"):
        draft["category"] = "未确定"
    draft = parse_cost_draft(message, draft)
    draft = apply_short_answer_to_last_question(message, draft)

    intent = payload.get("intent") or "assistant"
    create_requested = bool(previous.get("_createRequested")) or (
        explicit_create_requested(message) and not import_existing_style_requested(message)
    )
    draft["_createRequested"] = create_requested
    should_calculate = intent == "costing" or has_cost_signal(draft)
    missing = payload.get("questions") or []
    ready_to_save = False
    missing_field = ""

    if create_requested:
        intent = "style" if not should_calculate else "costing"
        missing_field, missing_question = creation_missing_info(draft)
        missing = [missing_question] if missing_question else []
        should_calculate = not missing
        ready_to_save = not missing

    calculation = calculate_cost(draft) if should_calculate else None
    draft["_readyToSave"] = ready_to_save
    draft["_lastMissingField"] = missing_field if missing else ""
    reply = payload.get("reply") or build_reply(draft, calculation, missing, intent=intent)
    return {
        "reply": reply,
        "intent": intent,
        "needMoreInfo": bool(missing),
        "questions": missing[:1],
        "readyToSave": ready_to_save,
        "costDraft": draft,
        "calculation": calculation,
    }


def is_vague_message(message):
    text = str(message or "").strip()
    return not text or len(text) < 2 or bool(re.fullmatch(r"[\d\s.]+", text))


class CostingChatView(APIView):
    def post(self, request):
        message = request.data.get("message", "")
        context = request.data.get("context") or {}
        previous = context.get("lastCostDraft") or {}
        tenant = get_current_tenant(request.user)
        if not tenant:
            return Response({"detail": "当前账号还没有所属档口，无法保存聊天记录"}, status=status.HTTP_400_BAD_REQUEST)

        AiChatMessage.objects.create(
            tenant=tenant,
            created_by=request.user,
            role=AiChatMessage.Role.USER,
            content=message,
            cost_draft=previous or {},
        )
        if is_vague_message(message) and not previous.get("_lastMissingField") and not previous.get("_createRequested"):
            reply = "老板，只发数字我判断不了是款式、数量还是价格。你可以说：帮我建一款牛仔外套，或者这款面料 26 一公斤。"
            AiChatMessage.objects.create(
                tenant=tenant,
                created_by=request.user,
                role=AiChatMessage.Role.ASSISTANT,
                content=reply,
                intent="assistant",
                cost_draft=previous or {},
                need_more_info=True,
            )
            prune_ai_chat_history(tenant, request.user)
            return Response({
                "reply": reply,
                "intent": "assistant",
                "needMoreInfo": True,
                "questions": [reply],
                "costDraft": previous or {},
                "calculation": None,
            })
        try:
            ai_payload = call_deepseek_assistant(message, context)
            response_payload = normalize_ai_payload(ai_payload, previous, message)
            AiChatMessage.objects.create(
                tenant=tenant,
                created_by=request.user,
                role=AiChatMessage.Role.ASSISTANT,
                content=response_payload["reply"],
                intent=response_payload["intent"],
                cost_draft=response_payload["costDraft"] or {},
                calculation=response_payload["calculation"] or {},
                need_more_info=response_payload["needMoreInfo"],
            )
            prune_ai_chat_history(tenant, request.user)
            return Response(response_payload)
        except RuntimeError as exc:
            detail = str(exc)
            AiChatMessage.objects.create(
                tenant=tenant,
                created_by=request.user,
                role=AiChatMessage.Role.ASSISTANT,
                content=detail,
                need_more_info=True,
            )
            prune_ai_chat_history(tenant, request.user)
            return Response({"detail": detail}, status=status.HTTP_502_BAD_GATEWAY)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return Response({"detail": f"DeepSeek 返回格式无法解析：{exc}"}, status=status.HTTP_502_BAD_GATEWAY)
