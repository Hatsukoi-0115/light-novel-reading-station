<script setup>
  import { ref, defineProps } from 'vue'

  const props = defineProps({
    content: String,
    windowdoc: Object
  })

  // // 字体大小、颜色全都能轻松维护
  // const fontSize = ref(16)
  // const changeFontSize = (type) => {
  //   fontSize.value += type === '+' ? 2 : -2
  //   document.documentElement.style.fontSize = fontSize.value + 'px'
  // }

  // const changeColor = () => {
  //   document.body.style.background = '#f5f5f5'
  // }
</script>

<template>
  <div class="content-page" v-html="content"></div>

  <!-- 你要的自定义功能，直接写组件 -->
  <!-- <div class="tools">
    <button @click="changeFontSize('+')">A+</button>
    <button @click="changeFontSize('-')">A-</button>
    <button @click="changeColor">切换主题色</button>
  </div> -->
</template>

<style scoped>
    .content-page{
        font-size: 20px;
    }
</style>