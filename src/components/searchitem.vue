<script setup>
    import { defineProps, h, render } from 'vue'
    import ContentWindow from './ContentWindow.vue'
    const API_URL='http://127.0.0.1:5000'
    const props = defineProps({
        title: String,
        link: String,
        img_link: String,
        author: String,
        status: String
    })

    async function get_content(){
        try{
            const response = await fetch(`${API_URL}/contentgetter?novelurl=${props.link}`)
            const result = await response.json()

            if(result.code === 200){
                const lastSlashIndex = result.content_url.lastIndexOf('/');
                //截取从开头到最后一个 '/' 之前的内容，定位text的url时仍需使用
                const halfUrl = result.content_url.slice(0, lastSlashIndex + 1);

                openContentWindow(result.pageTitle, result.tagHtml, halfUrl)
            } else {
                alert('获取目录内容失败：' + (result.msg || '未知错误'))
            }
        }catch(error){
            console.error(error)
        }
    }

    function openContentWindow(pageTitle, tagHtml, halfUrl){
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
        const vnode = h(ContentWindow, {
            content: tagHtml,
            halfUrl: halfUrl,
            windowdoc: newWindow.document
        })
        render(vnode, newWindow.document.getElementById('windowRoot'))
    }
</script>

<template>
    <div id="container">
        <img :src="img_link" alt="小说封面" width="168" height="240"/>
        <h1>{{ title }}</h1>
        <h2 id="aut">{{ author }}</h2>
        <h2 id="sta">{{ status }}</h2>
        <button @click="get_content">阅读</button>
        <div id="box"></div>
    </div>
</template>

<style scoped>
    #container{
        width: 500px;
        float: left;
        position: relative;
        margin: 20px 0 0 0;
    }
    #box{
        box-sizing: border-box;
        position: absolute;
        border: 2px solid orange;
        border-radius: 5px;
        width: 318px;
        height: 240px;
        left: 175px;
        top: 0;
        z-index: -1;
    }
    img{
        float: left;
        border-radius: 5px;
    }
    h1, h2{
        box-sizing: border-box;
        float: left;
        width: 296px;
        margin: 8px 18px 0 18px;
        padding: 0;
        font-size: 24px;
        line-height: 28px;
        font-weight: normal;
    }
    h2{
        font-size: 18px;
        line-height: 22px;
    }
    /* 优先级:style属性>ID选择器>类选择器>标签选择器 */
    #sta{
        margin: 4px 18px 0 18px;
    }
    button{
        position: absolute;
        left: 402px;
        top: 190px;
        border: 0;
        border-radius: 4px;
        background-color:mediumaquamarine;
        width: 80px;
        height: 40px;
        font-size: 20px;
        color: white;
    }
    button:hover{
        background-color: forestgreen;
    }
    button:active{
        background-color: darkgreen;
    }
</style>