<template>
  <div>
    <h1 class="page-title">{{ $route.meta.title }}</h1>
    <AgentInteraction />
  </div>
</template>

<script setup>
import AgentInteraction from '@/components/AgentInteraction.vue';
</script>