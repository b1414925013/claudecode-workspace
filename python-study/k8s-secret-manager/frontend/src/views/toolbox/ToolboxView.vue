<template>
  <div>
    <h2 style="margin-bottom: 20px">开发者工具箱</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="JSON 格式化" name="json">
        <el-input v-model="jsonInput" type="textarea" :rows="6" placeholder="输入 JSON" style="margin-bottom: 12px" />
        <el-input-number v-model="jsonIndent" :min="1" :max="8" size="small" style="margin-bottom: 12px" />
        <el-button type="primary" @click="formatJson">格式化</el-button>
        <pre v-if="jsonOutput" style="background: #f5f7fa; padding: 12px; border-radius: 4px; margin-top: 12px">{{ jsonOutput }}</pre>
      </el-tab-pane>
      <el-tab-pane label="Base64" name="b64">
        <el-input v-model="b64Input" type="textarea" :rows="4" placeholder="输入内容" />
        <div style="margin: 12px 0">
          <el-button @click="b64Encode">编码</el-button>
          <el-button @click="b64Decode">解码</el-button>
        </div>
        <el-input v-model="b64Output" type="textarea" :rows="4" readonly />
      </el-tab-pane>
      <el-tab-pane label="URL 编解码" name="url">
        <el-input v-model="urlInput" type="textarea" :rows="4" placeholder="输入内容" />
        <div style="margin: 12px 0">
          <el-button @click="urlEncode">编码</el-button>
          <el-button @click="urlDecode">解码</el-button>
        </div>
        <el-input v-model="urlOutput" type="textarea" :rows="4" readonly />
      </el-tab-pane>
      <el-tab-pane label="时间戳转换" name="ts">
        <el-input v-model="tsInput" placeholder="输入时间戳或日期 (如: 2025-01-01 00:00:00)" style="margin-bottom: 12px" />
        <el-button type="primary" @click="convertTs">转换</el-button>
        <pre v-if="tsOutput" style="background: #f5f7fa; padding: 12px; margin-top: 12px">{{ tsOutput }}</pre>
      </el-tab-pane>
      <el-tab-pane label="UUID 生成" name="uuid">
        <el-input-number v-model="uuidCount" :min="1" :max="50" />
        <el-button type="primary" style="margin-left: 12px" @click="genUuid">生成</el-button>
        <pre v-if="uuidOutput" style="background: #f5f7fa; padding: 12px; margin-top: 12px">{{ uuidOutput }}</pre>
      </el-tab-pane>
      <el-tab-pane label="正则测试" name="regex">
        <el-input v-model="regexPattern" placeholder="正则表达式" style="margin-bottom: 12px" />
        <el-input v-model="regexText" type="textarea" :rows="4" placeholder="测试文本" style="margin-bottom: 12px" />
        <el-button type="primary" @click="testRegex">测试</el-button>
        <pre v-if="regexOutput" style="background: #f5f7fa; padding: 12px; margin-top: 12px">{{ regexOutput }}</pre>
      </el-tab-pane>
      <el-tab-pane label="端口检测" name="port">
        <el-input v-model="portHost" placeholder="主机地址" style="width: 200px; margin-right: 12px" />
        <el-input-number v-model="portNum" :min="1" :max="65535" />
        <el-button type="primary" style="margin-left: 12px" @click="checkPort">检测</el-button>
        <div v-if="portResult !== null" style="margin-top: 12px">
          <el-tag :type="portResult ? 'success' : 'danger'">{{ portResult ? '端口开放' : '端口未开放' }}</el-tag>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-card style="margin-top: 24px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>常用导航链接</span>
          <el-button v-if="isAdmin" size="small" type="primary" @click="showLinkDialog = true">新增链接</el-button>
        </div>
      </template>
      <el-space wrap>
        <el-tag v-for="link in links" :key="link.id" :hit="true" style="cursor: pointer" @click="openLink(link.url)">
          <el-icon style="margin-right: 4px"><Link /></el-icon>
          {{ link.title }}
        </el-tag>
      </el-space>
    </el-card>

    <el-dialog v-model="showLinkDialog" title="新增链接" width="400px">
      <el-form ref="linkFormRef" :model="linkForm" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="linkForm.title" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="linkForm.url" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="linkForm.category" placeholder="如 docs/console/monitor" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLinkDialog = false">取消</el-button>
        <el-button type="primary" @click="saveLink">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { toolboxReq } from '@/api/request'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const isAdmin = ref(auth.user?.role === 'admin')
const activeTab = ref('json')

// JSON
const jsonInput = ref('')
const jsonIndent = ref(2)
const jsonOutput = ref('')

// Base64
const b64Input = ref('')
const b64Output = ref('')

// URL
const urlInput = ref('')
const urlOutput = ref('')

// Timestamp
const tsInput = ref('')
const tsOutput = ref('')

// UUID
const uuidCount = ref(5)
const uuidOutput = ref('')

// Regex
const regexPattern = ref('')
const regexText = ref('')
const regexOutput = ref('')

// Port
const portHost = ref('')
const portNum = ref(3306)
const portResult = ref<boolean | null>(null)

// Links
const links = ref<any[]>([])
const showLinkDialog = ref(false)
const linkFormRef = ref()
const linkForm = ref({ title: '', url: '', category: 'docs' })

async function formatJson() {
  try {
    const res: any = await toolboxReq.post('/tools/json-format', { input: jsonInput.value, indent: jsonIndent.value })
    jsonOutput.value = res.data.output
  } catch {}
}

async function b64Encode() {
  const res: any = await toolboxReq.post('/tools/base64-encode', { input: b64Input.value })
  b64Output.value = res.data.output
}
async function b64Decode() {
  const res: any = await toolboxReq.post('/tools/base64-decode', { input: b64Input.value })
  b64Output.value = res.data.output
}

async function urlEncode() {
  const res: any = await toolboxReq.post('/tools/url-encode', { input: urlInput.value })
  urlOutput.value = res.data.output
}
async function urlDecode() {
  const res: any = await toolboxReq.post('/tools/url-decode', { input: urlInput.value })
  urlOutput.value = res.data.output
}

async function convertTs() {
  const res: any = await toolboxReq.post('/tools/timestamp', { value: tsInput.value })
  tsOutput.value = JSON.stringify(res.data, null, 2)
}

async function genUuid() {
  const res: any = await toolboxReq.get('/tools/uuid', { params: { count: uuidCount.value } })
  uuidOutput.value = res.data.uuids.join('\n')
}

async function testRegex() {
  const res: any = await toolboxReq.post('/tools/regex-test', { pattern: regexPattern.value, text: regexText.value, flags: '' })
  regexOutput.value = JSON.stringify(res.data, null, 2)
}

async function checkPort() {
  const res: any = await toolboxReq.post('/tools/port-check', { host: portHost.value, port: portNum.value, timeout: 3 })
  portResult.value = res.data.open
}

function openLink(url: string) { window.open(url, '_blank') }

async function saveLink() {
  await toolboxReq.post('/links', linkForm.value)
  ElMessage.success('链接已添加')
  showLinkDialog.value = false
  fetchLinks()
}

async function fetchLinks() {
  const res: any = await toolboxReq.get('/links')
  links.value = res.data.items
}

onMounted(fetchLinks)
</script>
