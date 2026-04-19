<script setup>
  import { ref, defineProps, h, render, onMounted } from 'vue'
  import TextWindow from './TextWindow.vue'
  const API_URL='http://127.0.0.1:5000'
  const props = defineProps({
    content: String,
    halfUrl: String,
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

  // 绑定所有原网页html的a标签的点击事件（阻止默认跳转，调用get_text）
  onMounted(() => {
    // 这一句才能真正找到新窗口里的 a 标签
    const aTags = props.windowdoc.querySelectorAll('a')
    aTags.forEach(a => {
      a.addEventListener('click', (e) => {
        e.preventDefault()
        const text_url = a.getAttribute('href')
        if (text_url && !text_url.startsWith('http')) {
          get_text(props.halfUrl + text_url)
        }
      })
    })
  })

  //获取章节内容的函数
  async function get_text(url) {
      try {
          // 调用后端接口获取内容
          const response = await fetch(`${API_URL}/textgetter?texturl=${url}`)
          const result = await response.json()
          
          if (result.code === 200) {
            // 重新渲染新窗口内容为章节正文
            openTextWindow(result.pageTitle, result.tagHtml)
          } else {
            alert('获取章节内容失败：' + (result.msg || '未知错误'))
          }
      } catch (error) {
          console.error('获取章节内容出错：', error)
          alert('获取章节内容失败，请重试')
      }
  }

  function openTextWindow(pageTitle, tagHtml){
    // 1. 打开一个空白新窗口
    const newWindow = window.open('', '_blank');
    if (!newWindow) {
        alert('浏览器阻止了新窗口弹出，请允许弹窗权限');
        return;
    }
    
    // 2. 写入并关闭文档（确保内容渲染）
    newWindow.document.write(`
      <!DOCTYPE html>
      <html lang="zh-CN">
      <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>${pageTitle}</title>
          <style>
              body { margin: 20px; font-family: Arial, sans-serif; }
              .content-wrapper { max-width: 1200px; margin: 0 auto; }
              a { color: #1677ff; text-decoration: none; }
              a:hover { text-decoration: underline; }
              table { border-collapse: collapse; width: 100%; }
              table td { padding: 8px; border: 1px solid #eee; }
              .vcss { background-color: #f5f5f5; font-weight: bold; }
          </style>
      </head>
      <body>
          <div id="windowRoot"></div>
      </body>
      </html>
    `);
    newWindow.document.close(); // 必须关闭文档，否则内容可能不渲染

    // 3. 把 Vue 组件渲染到新窗口
    const vnode = h(TextWindow, {
      content: tagHtml,
      window: newWindow.document
    })
    render(vnode, newWindow.document.getElementById('windowRoot'))
  }
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

