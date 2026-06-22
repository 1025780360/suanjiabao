<script setup lang="ts">
import { Check, Delete, Plus } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { money, useStore } from '../composables/useStore'

const router = useRouter()
const {
  form,
  currentCategoryName,
  fabricCost,
  processCost,
  singleCost,
  suggestedPrice,
  minimumPrice,
  singleProfit,
  addFabric,
  removeFabric,
  addProcess,
  removeProcess,
} = useStore()

function goResult() {
  router.push({ name: 'result' })
}
</script>

<template>
  <div class="quote-page">
    <header class="quote-hero">
      <div class="quote-topline">
        <span>报价工作台 · {{ currentCategoryName }}</span>
        <button type="button" @click="goResult">
          <el-icon><Check /></el-icon>
          保存
        </button>
      </div>
      <h2>把成本填清楚</h2>

      <section class="price-board">
        <article class="price-main">
          <span>建议报价（单件）</span>
          <strong>¥{{ money(suggestedPrice) }}</strong>
          <em>含利润 ¥{{ money(Number(form.expectedProfit || 0)) }}</em>
        </article>
        <article>
          <span>单件成本（含料工辅）</span>
          <b>¥{{ money(singleCost) }}</b>
          <small>料 ¥{{ money(fabricCost) }}　工 ¥{{ money(processCost) }}</small>
        </article>
        <article>
          <span>最低接单（单件）</span>
          <b>¥{{ money(minimumPrice) }}</b>
          <small>毛利不低于安全线</small>
        </article>
      </section>

      <p class="formula-note">
        建议报价 = 单件成本 ¥{{ money(singleCost) }} + 目标利润 ¥{{ money(Number(form.expectedProfit || 0)) }}，系统自动向上取整。
      </p>
    </header>

    <section class="quote-scroll">
      <label class="style-name-field">
        <span>款式名称</span>
        <input v-model="form.styleName" maxlength="50" placeholder="例如：短袖针织 T" />
        <small>{{ form.styleName.length }} / 50</small>
      </label>

      <section class="cost-panel">
        <div class="panel-title">
          <div>
            <b>面料成本</b>
            <span>当前合计 ¥{{ money(fabricCost) }}</span>
          </div>
          <button type="button" @click="addFabric">
            <el-icon><Plus /></el-icon>
            添加面料
          </button>
        </div>

        <div class="cost-table">
          <div class="table-head">
            <span>面料名称</span>
            <span>单价</span>
            <span>用量</span>
            <span>小计</span>
          </div>
          <article v-for="item in form.fabrics" :key="item.id" class="cost-line">
            <label class="name-cell">
              <input v-model="item.name" aria-label="面料名称" placeholder="面料名称" />
            </label>
            <label>
              <input v-model.number="item.price" type="number" inputmode="decimal" placeholder="0" />
            </label>
            <label>
              <input v-model.number="item.usage" type="number" inputmode="decimal" placeholder="0" />
            </label>
            <strong>¥{{ money(Number(item.price || 0) * Number(item.usage || 0)) }}</strong>
            <button type="button" aria-label="删除面料" @click="removeFabric(item.id)">
              <el-icon><Delete /></el-icon>
            </button>
          </article>
          <div class="table-total">
            <span>面料小计</span>
            <b>¥{{ money(fabricCost) }}</b>
          </div>
        </div>
      </section>

      <section class="cost-panel">
        <div class="panel-title">
          <div>
            <b>工艺加工费</b>
            <span>当前合计 ¥{{ money(processCost) }}</span>
          </div>
          <button type="button" @click="addProcess">
            <el-icon><Plus /></el-icon>
            添加工序
          </button>
        </div>

        <div class="process-list">
          <article v-for="item in form.processes" :key="item.id" class="process-row">
            <input v-model="item.name" aria-label="工序名称" placeholder="工序名称" />
            <label>
              ¥
              <input v-model.number="item.fee" type="number" inputmode="decimal" placeholder="0" />
            </label>
            <button type="button" aria-label="删除工序" @click="removeProcess(item.id)">
              <el-icon><Delete /></el-icon>
            </button>
          </article>
        </div>
      </section>

      <section class="cost-panel compact">
        <div class="panel-title simple">
          <div>
            <b>其他费用</b>
            <span>辅料、包装和目标利润</span>
          </div>
        </div>
        <label class="expense-row">
          <span>
            <small>辅料包装</small>
            <b>吊牌 / 胶袋 / 主唛</b>
          </span>
          <em>¥<input v-model.number="form.accessoryPack" type="number" inputmode="decimal" placeholder="0" /></em>
        </label>
        <label class="expense-row">
          <span>
            <small>目标利润</small>
            <b>按单件利润填写</b>
          </span>
          <em>¥<input v-model.number="form.expectedProfit" type="number" inputmode="decimal" placeholder="0" /></em>
        </label>
      </section>
    </section>

    <footer class="quote-footer">
      <div>
        <span>预计单件利润</span>
        <b>¥{{ money(singleProfit) }}</b>
      </div>
      <button type="button" @click="goResult">查看报价结果</button>
    </footer>
  </div>
</template>

<style scoped>
.quote-page {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  background: linear-gradient(180deg, #07110d 0%, #0a1c15 24%, #fbf2df 24%, #f4e7cd 100%);
}

.quote-hero {
  flex: 0 0 auto;
  padding: 6px 14px 10px;
  color: #fbf2df;
}

.quote-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.quote-topline span {
  color: rgba(251, 242, 223, 0.64);
  font-size: 12px;
  font-weight: 850;
}

.quote-topline button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 38px;
  padding: 0 12px;
  border: 0;
  border-radius: 999px;
  color: #07110d;
  background: var(--gold-gradient);
  font-size: 13px;
  font-weight: 950;
}

.quote-hero h2 {
  margin: 4px 0 8px;
  color: #fff8e8;
  font-size: 22px;
  font-weight: 950;
  line-height: 1;
  letter-spacing: -0.06em;
}

.price-board {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  overflow: hidden;
  border: 1px solid rgba(240, 209, 136, 0.25);
  border-radius: 16px;
  background:
    linear-gradient(145deg, #0d3f2e, #062015);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.price-board article {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  min-height: 68px;
  padding: 8px 8px;
  text-align: center;
}

.price-board article + article {
  border-left: 1px solid rgba(251, 242, 223, 0.12);
}

/* 主卡片：金色强调 */
.price-board .price-main {
  background: linear-gradient(160deg, #f5d78c 0%, #d3a24c 60%, #b87a28 100%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.3);
}

.price-board .price-main span { color: rgba(0,0,0,0.55); }
.price-board .price-main strong { color: #1a1205; text-shadow: none; }
.price-board .price-main em { color: rgba(0,0,0,0.45); }

.price-board span {
  color: rgba(251, 242, 223, 0.7);
  font-size: 10px;
  font-weight: 800;
}

.price-board strong {
  margin-top: 3px;
  color: #f0d188;
  font-size: 24px;
  font-weight: 950;
  line-height: 1;
  letter-spacing: -0.05em;
}

.price-board b {
  margin-top: 4px;
  color: #fff7df;
  font-size: 15px;
  font-weight: 950;
}

.price-board small,
.price-board em {
  margin-top: 3px;
  color: rgba(251, 242, 223, 0.6);
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  line-height: 1.2;
}

.formula-note {
  margin: 4px 2px 0;
  color: rgba(251, 242, 223, 0.5);
  font-size: 10px;
  font-weight: 700;
  line-height: 1.3;
}

.quote-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  align-content: start;
  gap: 8px;
  padding: 14px 14px 70px;
  scrollbar-width: none;
  overscroll-behavior: contain;
}

.quote-scroll::-webkit-scrollbar {
  display: none;
}

.style-name-field {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 14px;
  background: #fffef9;
  border: 1px solid rgba(189,139,57,0.15);
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.style-name-field span,
.panel-title span,
.expense-row small {
  color: rgba(23, 32, 24, 0.5);
  font-size: 10px;
  font-weight: 800;
}

.style-name-field input {
  width: 100%;
  height: 36px;
  padding: 0 36px 0 10px;
  border: 1.5px solid rgba(189, 139, 57, 0.3);
  border-radius: 10px;
  outline: 0;
  background: #fffdf7;
  color: #101410;
  font-size: 15px;
  font-weight: 900;
}

.style-name-field input:focus {
  border-color: #bd8b39;
  box-shadow: 0 0 0 3px rgba(189,139,57,0.1);
}

.style-name-field small {
  position: absolute;
  right: 18px;
  bottom: 16px;
  color: rgba(23, 32, 24, 0.4);
  font-size: 10px;
  font-weight: 700;
}

.cost-panel {
  padding: 10px 12px;
  border-radius: 14px;
  background: #fffef9;
  border: 1px solid rgba(189,139,57,0.12);
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
}

.cost-panel.compact {
  padding-bottom: 8px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(189,139,57,0.1);
}

.panel-title.simple {
  margin-bottom: 4px;
  padding-bottom: 0;
  border-bottom: none;
}

.panel-title b {
  display: block;
  color: #1a1812;
  font-size: 15px;
  font-weight: 950;
  letter-spacing: -0.03em;
}

.panel-title button {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  min-height: 28px;
  padding: 0 8px;
  border: 0;
  border-radius: 8px;
  color: #fbf2df;
  background: linear-gradient(145deg, #0e3a2c, #062015);
  font-size: 10px;
  font-weight: 900;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.cost-table {
  overflow: hidden;
  border-radius: 14px;
  border: 1px solid rgba(189,139,57,0.1);
  background: #fefcf6;
}

.table-head,
.cost-line {
  display: grid;
  grid-template-columns: minmax(80px, 1.1fr) 0.8fr 0.8fr 0.65fr 26px;
  gap: 5px;
  align-items: center;
}

.table-head {
  min-height: 28px;
  padding: 0 8px;
  color: rgba(23, 32, 24, 0.4);
  background: rgba(240,230,210,0.5);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.table-head span:last-child {
  grid-column: 4;
}

.cost-line {
  min-height: 46px;
  padding: 4px 6px 4px 8px;
}

.cost-line + .cost-line,
.table-total {
  border-top: 1px solid rgba(189,139,57,0.08);
}

.cost-line input,
.process-row input,
.expense-row input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #101410;
  font: inherit;
  font-size: 13px;
  font-weight: 850;
  text-overflow: ellipsis;
}

.cost-line label:not(.name-cell),
.process-row label,
.expense-row em {
  display: flex;
  align-items: center;
  min-height: 30px;
  padding: 0 5px;
  border: 1.5px solid rgba(189, 139, 57, 0.2);
  border-radius: 8px;
  background: #fffdf7;
  color: #101410;
  font-size: 12px;
  font-style: normal;
  font-weight: 850;
  overflow: hidden;
}

.name-cell input {
  min-height: 30px;
  padding: 0 8px;
  border: 1.5px solid rgba(189, 139, 57, 0.25);
  border-radius: 8px;
  background: #fffdf7;
  font-size: 13px;
  font-weight: 900;
}
.name-cell input:focus {
  border-color: #bd8b39;
  box-shadow: 0 0 0 2px rgba(189,139,57,0.12);
}

.cost-line strong {
  color: #1a1812;
  text-align: right;
  font-size: 13px;
  font-weight: 900;
}

.cost-line button,
.process-row button {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border: 0;
  border-radius: 6px;
  color: #a08060;
  background: rgba(189,139,57,0.08);
  font-size: 12px;
}

.table-total {
  display: flex;
  min-height: 30px;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  color: rgba(23, 32, 24, 0.45);
  background: rgba(240,230,210,0.4);
  font-size: 11px;
  font-weight: 800;
}

.table-total b {
  color: #bd8b39;
  font-size: 14px;
  font-weight: 950;
}

.process-list {
  display: grid;
  gap: 5px;
}

.process-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 105px 26px;
  gap: 5px;
  align-items: center;
}

.process-row > input {
  min-height: 30px;
  padding: 0 8px;
  border: 1.5px solid rgba(189,139,57,0.15);
  border-radius: 8px;
  background: #fefcf6;
  font-size: 12px;
}

.expense-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 105px;
  gap: 6px;
  align-items: center;
  min-height: 38px;
  margin-top: 4px;
  padding: 6px 8px;
  border-top: 1px dashed rgba(189,139,57,0.12);
  background: rgba(255,255,255,0.3);
  border-radius: 0 0 10px 10px;
}

.expense-row span,
.expense-row b,
.expense-row small {
  display: block;
}

.expense-row b {
  margin-top: 3px;
  color: rgba(23, 32, 24, 0.76);
  font-size: 14px;
}

.quote-footer {
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 6px;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  min-height: 48px;
  padding: 6px 12px;
  border: 1px solid rgba(240, 209, 136, 0.2);
  border-radius: 16px;
  color: #fbf2df;
  background:
    radial-gradient(circle at 92% 0%, rgba(240, 209, 136, 0.12), transparent 30%),
    linear-gradient(160deg, rgba(7,17,13,0.95), rgba(10,34,28,0.92));
  backdrop-filter: blur(12px);
  box-shadow: 0 -6px 18px rgba(0,0,0,0.2);
}

.quote-footer > div {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.quote-footer span {
  color: rgba(251, 242, 223, 0.5);
  font-size: 10px;
  font-weight: 800;
}

.quote-footer b {
  color: #f0d188;
  font-size: 18px;
  font-weight: 950;
  letter-spacing: -0.04em;
}

.quote-footer button {
  min-height: 36px;
  padding: 0 14px;
  border: 0;
  border-radius: 12px;
  color: #161006;
  background: linear-gradient(145deg, #f3d891, #d3a24c);
  font-size: 12px;
  font-weight: 950;
  box-shadow: 0 6px 16px rgba(169, 112, 43, 0.25);
  white-space: nowrap;
}

@media (max-width: 390px) {
  .quote-hero,
  .quote-scroll {
    padding-inline: 12px;
  }

  .price-board article {
    padding-inline: 8px;
  }

  .price-board strong {
    font-size: 28px;
  }

  .table-head,
  .cost-line {
    grid-template-columns: minmax(70px, 1fr) 0.65fr 0.65fr 0.68fr 28px;
    gap: 5px;
  }

  .quote-footer {
    left: 8px;
    right: 8px;
    bottom: 4px;
    min-height: 44px;
    padding: 5px 10px;
    border-radius: 14px;
  }

  .quote-footer b {
    font-size: 16px;
  }

  .quote-footer button {
    min-height: 34px;
    padding: 0 12px;
    font-size: 11px;
  }
}
</style>
