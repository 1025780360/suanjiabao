# 服装成本管理系统

商业化服装成本管理系统，前端使用 Vue 3，后端使用 Django + Django REST Framework。

第一版定位已经调整为手机优先的极简算价工具：不用要求档口老板先建供应商、物料库或 BOM，而是拍个款、填几个数，马上知道这件衣服卖多少钱才不亏。系统在背后自动沉淀历史款式、报价记录、成本记录，后续再逐步长成完整管理系统。

## 目录结构

```text
.
├── backend/          # Django 后端
├── frontend/         # Vue 3 前端
├── 需求.md
└── 项目规划.md
```

## 后端启动

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py runserver
```

后端健康检查地址：

```text
http://127.0.0.1:8000/api/health/
```

## 前端启动

```powershell
cd frontend
npm run dev
```

默认访问地址：

```text
http://localhost:5173/
```

## 当前已完成

- 项目规划文档
- Django 项目骨架
- Vue 3 + TypeScript 项目骨架
- DRF、CORS、环境变量配置
- SaaS 企业租户、用户成员基础模型
- 供应商、物料、款式、工序、BOM、成本单、报价单、订单核心模型
- Django Admin 基础注册
- 前端快速算价页面
- 品类模板、单件成本、建议批发价、最低接单价、数量利润预估

## 下一步

- 保存快速算价记录到后端
- 实现历史款式列表和类似款复制
- 实现拍照上传和款式图片存储
- 增加微信分享报价结果
- 再逐步补登录、权限、供应商、物料、BOM 和 Excel 导入导出
- 准备 Zeabur 部署配置
