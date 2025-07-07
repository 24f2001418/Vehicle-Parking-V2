<template>
  <div class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ title }}</h2>
      <slot></slot>
      <div class="modal-actions">
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
        <button class="save-btn" @click="$emit('save')">{{ editing ? 'Update' : 'Create' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ title:String, editing:Boolean })
</script>

<style scoped>
.modal{position:fixed;inset:0;background:rgba(0,0,0,.5);display:grid;place-items:center;z-index:999}
.modal-content{background:#fff;padding:28px;width:90%;max-width:500px;border-radius:8px}
.modal-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:14px}
.cancel-btn{background:#f3f4f6;border:1px solid #d1d5db;padding:8px 16px;border-radius:4px}
.save-btn{background:#2563eb;color:#fff;border:none;padding:8px 16px;border-radius:4px}
</style>
