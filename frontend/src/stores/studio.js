import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios from 'axios'

const api = axios.create({ baseURL: '/api/studio', timeout: 30000 })
api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('studio-access-token')
  if (token) config.headers['X-Studio-Token'] = token
  return config
})

export const useStudioStore = defineStore('studio', () => {
  const datasets = ref([]), demos = ref([]), jobs = ref([]), capabilities = ref(null)
  const selectedId = ref(localStorage.getItem('studio-dataset') || '')
  const discoveryId = ref(''), generationId = ref(''), error = ref('')
  const loading = ref(false), connected = ref(false), authRequired = ref(false)
  const selected = computed(() => datasets.value.find(d => d.id === selectedId.value))
  const discoveries = computed(() => jobs.value.filter(j => j.kind === 'discover' && j.config.dataset_id === selectedId.value))
  const discovery = computed(() => discoveries.value.find(j => j.id === discoveryId.value) || discoveries.value.find(j => j.status === 'completed'))
  const generations = computed(() => jobs.value.filter(j => j.kind === 'generate' && j.config.dataset_id === selectedId.value))
  const generation = computed(() => generations.value.find(j => j.id === generationId.value) || generations.value.find(j => j.status === 'completed'))
  const pending = computed(() => jobs.value.filter(j => ['queued', 'running'].includes(j.status)))
  let timer = null, polling = false
  function fail(err) {
    authRequired.value = err.response?.status === 401
    error.value = err.response?.data?.error || '无法连接鼠先知引擎。请启动本地服务后重试。'
  }
  function select(id) {
    selectedId.value = id
    localStorage.setItem('studio-dataset', id)
    discoveryId.value = ''; generationId.value = ''
  }
  async function refresh() {
    loading.value = true; error.value = ''
    try {
      const [library, experiments, engines] = await Promise.all([api.get('/datasets'), api.get('/jobs'), api.get('/capabilities')])
      datasets.value = library.data.datasets; demos.value = library.data.demos
      jobs.value = experiments.data.jobs; capabilities.value = engines.data
      connected.value = true; authRequired.value = false
      if (!selected.value && datasets.value.length) select(datasets.value[0].id)
    } catch (err) { connected.value = false; fail(err) } finally { loading.value = false }
  }
  async function action(path, payload, options = {}) {
    error.value = ''
    try { return (await api.post(path, payload, options)).data } catch (err) { fail(err); throw err }
  }
  async function addDemo(id) {
    const result = await action('/datasets/demo', { demo: id })
    await refresh(); select(result.id)
    return result
  }
  async function upload(file) {
    const form = new FormData(); form.append('file', file)
    const result = await action('/datasets/upload', form)
    await refresh(); select(result.id)
    return result
  }
  async function submit(kind, config) {
    const job = await action(`/${kind}`, config)
    jobs.value.unshift(job)
    if (kind === 'discover') discoveryId.value = job.id
    else generationId.value = job.id
    return job
  }
  async function ask(message, history = []) {
    return action('/assistant', { message, history, dataset_id: selected.value?.id,
      discovery_id: discovery.value?.status === 'completed' ? discovery.value.id : undefined,
      generation_id: generation.value?.status === 'completed' ? generation.value.id : undefined }, { timeout: 60000 })
  }
  async function poll() {
    if (polling || !connected.value || !pending.value.length) return
    polling = true
    try { jobs.value = (await api.get('/jobs')).data.jobs } catch (err) { fail(err) } finally { polling = false }
  }
  function startPolling() { if (!timer) timer = setInterval(poll, 1800) }
  function stopPolling() { clearInterval(timer); timer = null }
  async function download(id) {
    error.value = ''
    try {
      const response = await api.get(`/jobs/${id}/export`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data), link = document.createElement('a')
      link.href = url; link.download = `shuprophet-${id.slice(0, 8)}.zip`; link.click()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (err) {
      if (err.response?.data instanceof Blob) { try { err.response.data = JSON.parse(await err.response.data.text()) } catch { /* fallback */ } }
      fail(err)
    }
  }
  function openJob(job) {
    select(job.config.dataset_id)
    if (job.kind === 'discover') discoveryId.value = job.id
    else { generationId.value = job.id; discoveryId.value = job.config.discovery_id }
  }
  return { datasets, demos, jobs, selectedId, discoveryId, generationId, selected, discoveries, discovery,
    generations, generation, capabilities, error, loading, connected, authRequired, pending,
    refresh, select, addDemo, upload, submit, ask, startPolling, stopPolling, download, openJob }
})
