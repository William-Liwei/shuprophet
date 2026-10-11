export const colors = ['#167563', '#d19342', '#6086b1', '#af6e81', '#81874a', '#8b76ad', '#c27758', '#5c9b9b']
export const base = {
  color: colors, animationDuration: 350,
  textStyle: { fontFamily: 'Inter, Segoe UI, Microsoft YaHei, sans-serif', color: '#53675d', fontSize: 12 },
  tooltip: { trigger: 'axis', confine: true, renderMode: 'richText', backgroundColor: '#ffffff', borderColor: '#e0e7e2', padding: 12, textStyle: { color: '#304b3d', fontSize: 12 } },
  grid: { left: 40, right: 20, top: 36, bottom: 26, containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, axisLine: { lineStyle: { color: '#dce2dc' } }, axisTick: { show: false }, axisLabel: { color: '#64776b', fontSize: 11 } },
  yAxis: { type: 'value', scale: true, axisLabel: { color: '#64776b', fontSize: 11 }, nameTextStyle: { color: '#64776b', fontSize: 11 }, splitLine: { lineStyle: { color: '#e9eeeb', type: 'dashed' } } },
  legend: { type: 'scroll', top: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, itemGap: 16, textStyle: { color: '#53675d', fontSize: 12 } },
}
export function lines(series, labels) {
  const length = series[0]?.data?.length || 0
  return { ...base, xAxis: { ...base.xAxis, data: labels || Array.from({ length }, (_, i) => i) }, series: series.map(s => ({ type: 'line', symbol: 'none', lineStyle: { width: 2 }, ...s })) }
}
export const number = value => value == null ? '—' : Number(value).toLocaleString('zh-CN', { maximumFractionDigits: 3 })
export const percent = value => value == null ? '—' : `${(value * 100).toFixed(1)}%`
export const date = value => new Date(value).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
