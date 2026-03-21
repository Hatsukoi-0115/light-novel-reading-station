<script setup>
    import { defineProps } from 'vue';
    const API_URL='http://127.0.0.1:5000'
    const props=defineProps(['title','link','img_link','author','status'])

    //获取章节内容的函数
    async function get_text(text_url,halfUrl) {
        try {
            // 调用后端接口获取内容（复用原contentgetter接口，逻辑通用）
            const response = await fetch(`${API_URL}/textgetter?texturl=${halfUrl+text_url}`)
            const result = await response.json()
            
            if (result.code === 200) {
            // 重新渲染新窗口内容为章节正文
                openInNewPage(result.pageTitle,result.tagHtml)
            } else {
            alert('获取章节内容失败：' + (result.msg || '未知错误'))
            }
        } catch (error) {
            console.error('获取章节内容出错：', error)
            alert('获取章节内容失败，请重试')
        }
    }

    //绑定所有a标签的点击事件（阻止默认跳转，调用get_text）
    function bindATagEvents(windowObj,halfUrl) {
        const aTags = windowObj.document.querySelectorAll('a')
        aTags.forEach(a => {
            a.addEventListener('click', (e) => {
                // 阻止a标签默认跳转行为
                e.preventDefault()
                const text_url = a.getAttribute('href')
                if (text_url && !text_url.startsWith('http')) {
                    // 调用get_text，传入目标地址和当前窗口对象
                    get_text(text_url,halfUrl)
                }
            })
        })
    }

    async function get_content(){
        try{
            const response=await fetch(`${API_URL}/contentgetter?novelurl=${props.link}`)
            const result=await response.json()

            if(result.code===200){
                const newWindow = openInNewPage(result.pageTitle,result.tagHtml)

                // 直接绑定事件（document.write后DOM已存在）
                const lastSlashIndex = result.content_url.lastIndexOf('/');
                //截取从开头到最后一个 '/' 之前的内容，定位text的url时仍需使用
                const halfUrl = result.content_url.slice(0, lastSlashIndex+1);
                bindATagEvents(newWindow, halfUrl);
            } else {
            alert('获取目录内容失败：' + (result.msg || '未知错误'))
            }
        }catch(error){
            console.error(error)
        }
    }

    function openInNewPage(pageTitle,tagHtml){
        // 1. 打开一个空白新窗口
        const newWindow = window.open('', '_blank');
        if (!newWindow) {
            alert('浏览器阻止了新窗口弹出，请允许弹窗权限');
            return;
        }
        // 2. 直接写入完整的HTML结构（包含html/head/body）
        const fullHtml = `
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
                <div class="content-wrapper">
                    ${tagHtml} <!-- 直接插入后端返回的table HTML -->
                </div>
            </body>
            </html>
        `;

        // 3. 写入并关闭文档（确保内容渲染）
        newWindow.document.write(fullHtml);
        newWindow.document.close(); // 必须关闭文档，否则内容可能不渲染

        return newWindow
    }
</script>

<template>
    <div id="container">
        <img :src="img_link" alt="小说封面" width="168" height="240"/>
        <h1>{{ title }}</h1>
        <h2 id="aut">{{ author }}</h2>
        <h2 id="sta"">{{ status }}</h2>
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
    h1{
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
        box-sizing: border-box;
        float: left;
        width: 296px;
        margin: 8px 18px 0 18px;
        padding: 0;
        font-size: 20px;
        line-height: 24px;
        font-weight: normal;
    }
    /* 优先级:ID选择器>类选择器 */
    #sta{
        margin: 4px 18px 0 18px;
    }
    button{
        position: absolute;
        left: 188px;
        top: 180px;
        border: 0;
        border-radius: 5px;
        background-color:mediumaquamarine;
        width: 100px;
        height: 50px;
        font-size: 24px;
        color: white;
    }
    button:hover{
        background-color: forestgreen;
    }
    button:active{
        background-color: darkgreen;
    }
</style>