# 服装供应系统 AI 交接文档

本文档用于把当前项目状态交接给没有参与过本项目的 AI 或开发者。

## 1. 项目定位

本项目是一个面向广州服装档口老板的手机端服装成本报价工具。

核心定位不是 ERP，而是：

> 拍个款，填几个数，马上知道这件衣服卖多少钱才不亏。

第一阶段重点是移动端快速算价：

- 拍照或从相册上传款式图
- 选择或自建品类
- 添加多种面料
- 添加多个加工工序
- 填辅料包装费和期望利润
- 自动计算成本、建议报价、最低接单价、利润
- 保存款式到数据库
- 首页显示已保存款式和款式图片
- 用户账号隔离，不同账号互相看不到数据

## 2. 技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Element Plus
- Axios

后端：

- Django 5.2
- Django REST Framework
- DRF Token Authentication
- SQLite 本地开发，后续可换 PostgreSQL

## 3. 项目目录

```text
C:\Users\zhuzhu\Desktop\服装供应系统
├── backend/              Django 后端
├── frontend/             Vue 前端
├── design/               UI 参考图和 HTML
├── logs/                 本地运行日志
├── 需求.md
├── 项目规划.md
├── README.md
└── AI交接文档.md
```

## 4. 当前运行地址

电脑本机：

```text
http://127.0.0.1:5174/
```

手机同 Wi-Fi 访问：

```text
http://192.168.1.3:5174/
```

后端 API：

```text
http://127.0.0.1:8000/api/
http://192.168.1.3:8000/api/
```

## 5. 启动命令

后端：

```powershell
cd C:\Users\zhuzhu\Desktop\服装供应系统\backend
..\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

前端：

```powershell
cd C:\Users\zhuzhu\Desktop\服装供应系统\frontend
npm run dev -- --host 0.0.0.0 --port 5174
```

构建检查：

```powershell
cd C:\Users\zhuzhu\Desktop\服装供应系统\frontend
npm run build
```

后端检查：

```powershell
cd C:\Users\zhuzhu\Desktop\服装供应系统\backend
..\.venv\Scripts\python.exe manage.py check
```

## 6. 已完成功能

### 6.1 账号系统

已完成：

- 注册账号
- 登录账号
- Token 保存到 `localStorage`
- 刷新页面后自动读取 Token 并加载数据
- 退出登录
- 修改个人资料

相关文件：

```text
backend/accounts/models.py
backend/accounts/serializers.py
backend/accounts/views.py
backend/accounts/urls.py
frontend/src/api/http.ts
frontend/src/views/DashboardView.vue
```

### 6.2 数据库存储

已完成：

- 用户账号保存到数据库
- 店铺资料保存到数据库
- 自定义品类保存到数据库
- 款式报价保存到数据库
- 款式图片以 Base64 Data URL 暂存在数据库字段 `image_data`

注意：图片目前是原型方案，后续正式版应改为上传文件或对象存储。

### 6.3 数据隔离

已完成基础隔离：

- 后端模型继承 `TenantOwnedModel`
- 数据带 `tenant`
- 数据带 `created_by`
- 查询 `QuickStyle` 和 `QuickCategory` 时只返回当前登录用户自己的数据
- 前端也通过 `ownerId` 做展示过滤

重要原则：

> 真正的数据隔离必须由后端 API 保证，前端过滤只能作为体验层辅助。

### 6.4 手机端页面

当前所有主要 UI 在：

```text
frontend/src/views/DashboardView.vue
```

包含页面状态：

- `home` 首页
- `photo` 拍照建款
- `cost` 填成本
- `result` 报价结果
- `profile` 我的
- `settings` 设置个人资料
- `asset` 资产管理详情

### 6.5 拍照和相册

已完成：

- “现在拍照”
- “从相册选”
- 保存款式时带上图片
- 首页款式列表显示图片缩略图
- 款式档案显示图片缩略图

### 6.6 算价能力

当前计算逻辑：

```text
面料合计 = sum(面料单价 * 用量)
加工合计 = sum(工序费用)
单件成本 = 面料合计 + 加工合计 + 辅料包装费 + 固定杂费 1.6
建议批发价 = ceil(单件成本 + 期望利润)
最低接单价 = ceil(单件成本 * 1.18)
单件利润 = 建议批发价 - 单件成本
```

已支持：

- 多面料
- 多工序
- 删除面料
- 删除工序
- 自定义品类
- 自定义款式名称
- 辅料包装费
- 期望利润

已删除：

- 损耗率
- 补料米数

原因：用户认为中年档口老板不一定知道损耗该怎么填。

## 7. 后端 API

### 7.1 账号 API

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/me/
PUT  /api/auth/profile/
```

注册请求示例：

```json
{
  "username": "test",
  "password": "123456",
  "display_name": "张老板",
  "shop_name": "锦禾服装报价室",
  "shop_location": "广州 · 沙河档口"
}
```

登录返回：

```json
{
  "token": "...",
  "user": {
    "id": 1,
    "username": "test",
    "display_name": "张老板",
    "shop_name": "锦禾服装报价室",
    "shop_location": "广州 · 沙河档口",
    "phone": ""
  }
}
```

前端请求头：

```text
Authorization: Token <token>
```

### 7.2 快速品类 API

```text
GET  /api/costing/quick-categories/
POST /api/costing/quick-categories/
```

### 7.3 快速款式 API

```text
GET  /api/costing/quick-styles/
POST /api/costing/quick-styles/
```

保存款式请求字段：

```json
{
  "name": "短袖针织 T",
  "category": "T 恤",
  "image_data": "data:image/png;base64,...",
  "fabrics": [
    { "id": 1, "name": "精棉汗布", "price": 22, "usage": 0.82 }
  ],
  "processes": [
    { "id": 3, "name": "裁剪", "fee": 2 },
    { "id": 4, "name": "车缝", "fee": 6.5 }
  ],
  "accessory_pack": 2.2,
  "expected_profit": 7,
  "minimum_price": 31,
  "quote_price": 33,
  "total_cost": 27.74,
  "profit": 5.26
}
```

## 8. 最近修复过的问题

问题：款式保存失败。

原因：

前端 JS 计算金额时出现浮点尾巴，例如：

```text
27.740000000000002
```

后端 Decimal 字段校验失败，返回 `400`。

修复：

- 前端新增 `roundAmount()`，保存前统一保留两位小数
- 后端 `QuickStyleSerializer` 金额字段改为 `FloatField`
- 保存失败时前端显示错误提示

## 9. 重要文件说明

### 9.1 前端主页面

```text
frontend/src/views/DashboardView.vue
```

这是目前最重要的文件，包含：

- 登录注册页
- 手机 App 所有页面
- 算价逻辑
- 保存款式逻辑
- 个人资料设置
- 资产管理页

后续建议拆分成多个组件：

```text
LoginView.vue
HomeView.vue
PhotoStep.vue
CostStep.vue
ResultView.vue
ProfileView.vue
SettingsView.vue
AssetView.vue
```

### 9.2 前端 API

```text
frontend/src/api/http.ts
```

注意这里有自动判断 API 地址：

- 如果前端运行在 `localhost`，请求 `127.0.0.1:8000`
- 如果前端运行在手机访问的局域网 IP，则请求同一 IP 的 `8000`

### 9.3 后端快速算价模型

```text
backend/costing/models.py
```

新增模型：

- `QuickCategory`
- `QuickStyle`

### 9.4 后端快速算价接口

```text
backend/costing/views.py
backend/costing/serializers.py
backend/costing/urls.py
```

## 10. 当前已执行的数据库迁移

新增迁移：

```text
backend/accounts/migrations/0002_user_display_name_user_shop_location_user_shop_name.py
backend/costing/migrations/0002_quickcategory_quickstyle.py
```

已执行：

```powershell
python manage.py migrate
```

## 11. 当前产品规则

- 用户必须注册/登录后使用
- 每个账号只看到自己的款式
- 每个账号只看到自己的自定义品类
- 系统默认品类所有账号可见
- 款式保存后出现在首页
- 点击首页款式会复制成一个新款继续修改
- 我的页面展示当前账号的数据资产
- 资产管理里的每个按钮都能打开真实数据页

## 12. 下一步建议

优先级从高到低：

1. 拆分 `DashboardView.vue`，降低维护难度
2. 图片不要再存 Base64，改成后端文件上传
3. 增加款式详情页，不只是复制旧款
4. 增加删除款式、编辑款式
5. 增加报价记录表，一个款式可以有多次报价
6. 增加客户名称和客户报价
7. 增加后端分页和搜索
8. 增加真实部署配置，优先 Zeabur + PostgreSQL
9. 增加密码修改和找回密码
10. 增加更严格的权限测试，确保账号隔离无漏洞

## 13. 给下一个 AI 的工作提示

请不要把本项目做成传统 ERP。

目标用户是中年服装档口老板，交互必须直接、明显、少字段。优先考虑：

- 一眼知道哪里能点
- 一眼知道哪里能填
- 不要专业术语
- 不要假数据
- 真实保存到数据库
- 不同账号数据隔离
- 手机端优先

当前最应该继续做的是：

> 将前端大文件拆分为多个页面组件，并把图片上传从 Base64 改成后端文件上传。
