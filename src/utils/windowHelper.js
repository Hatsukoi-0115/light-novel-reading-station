import { h, render } from 'vue';

/**
 * 通用打开新窗口函数
 * @param {Object} options 配置项
 * @param {string} options.pageTitle 新窗口标题（必填）
 * @param {import('vue').Component} [options.component=undefined] 要渲染的Vue组件（可选）
 * @param {string} [options.styleContent=''] 额外样式（可选）
 * @param {Object} [options.customProps={}] 组件自定义参数（可选）
 * @returns {Window|null} 新窗口对象
 */

export function openNewWindow({pageTitle, component = undefined, styleContent = '', ...componentProps}){
    if (!pageTitle) {
        throw new Error('pageTitle 是必填参数，请传入新窗口标题！');
    }
    // 1. 打开一个空白新窗口
    const newWindow = window.open('', '_blank');
    if (!newWindow) {
        alert('浏览器阻止了新窗口弹出，请允许弹窗权限');
        return null;
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
                /* 额外自定义样式（可选） */
                ${styleContent}
            </style>
        </head>
        <body>
            <div id="windowRoot"></div>
        </body>
        </html>
    `);
    newWindow.document.close(); // 必须关闭文档，否则内容可能不渲染

    // 3. 把 Vue 组件渲染到新窗口
    if(component){
        const vnode = h(component, {
            ...componentProps,
            windowdoc: newWindow.document
        })
        render(vnode, newWindow.document.getElementById('windowRoot'))
    }
}