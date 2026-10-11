<template><v-chart :option="option" autoresize class="studio-chart" :style="{ height: `${height}px` }" /></template>
<script setup>
defineProps({ option: { type: Object, required: true }, height: { type: Number, default: 280 } })
</script>
