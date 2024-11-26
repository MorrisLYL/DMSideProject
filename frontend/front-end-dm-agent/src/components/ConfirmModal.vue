<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
  >
    <div class="bg-white p-6 rounded-lg shadow-lg w-1/3">
      <h2 class="text-lg font-bold mb-4">{{ title }}</h2>
      <slot></slot>
      <div class="flex justify-end">
        <button
          class="px-4 py-2 mr-2 bg-gray-300 rounded hover:bg-gray-400"
          @click="$emit('cancel')"
        >
          Cancel
        </button>
        <button
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          @click="$emit('save')"
        >
          Save & Process
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    title: {
      type: String,
      default: "Modal",
    },
  },
  emits: ["cancel", "save"],
};
</script>
