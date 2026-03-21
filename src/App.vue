<script setup>
  import {ref} from 'vue'
  import searchitem from './components/searchitem.vue'
  const API_URL='http://127.0.0.1:5000'
  const searchtype=ref('articlename')
  const searchkey=ref('')
  const searchitems=ref([])
  async function search(){
    if(searchkey.value){
      try{
        const response=await fetch(`${API_URL}/novelgetter?searchtype=${searchtype.value}&searchkey=${encodeURIComponent(searchkey.value)}`)
        const result=await response.json()

        searchitems.value=[]

        result.forEach(element => {
          const novelItem = {
            title: element.title || '未知标题', // 加默认值防止字段缺失
            link: element.link || '',
            img_link: element.img_link || '',
            author: element.author || '未知作者',
            status: element.status || '未知状态'
          }
          searchitems.value.push(novelItem)
        })
      }catch(error){
        console.error("搜索失败：", error)
        searchitems.value=[]
      }
    }
  }
</script>

<template>
  <head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&display=swap" rel="stylesheet">
  </head>
  <h1>轻小说阅读站</h1>
  <div id="searcharea">
    <select v-model="searchtype">
      <option value="articlename">小说标题</option>
      <option value="author">作者名称</option>
    </select>
    <input type="text" v-model="searchkey" placeholder="请输入关键字"/>
    <button @click="search">搜索</button>
  </div>
  <div id="displayarea">
    <searchitem
      v-for="item in searchitems"
      :key="item.title"
      :title="item.title"
      :link="item.link"
      :img_link="item.img_link"
      :author="item.author"
      :status="item.status"
    />
  </div>
</template>

<style>
  #app {
    margin: auto;
    width: 1000px;
  }
</style>
<style scoped>
  .zcool-xiaowei-regular{
    font-family: "ZCOOL XiaoWei", sans-serif;
    font-weight: 400;
    font-style: normal;
  }
  h1{
    margin: 20px 0 10px 0;
    width: 1000px;
    font-family: "ZCOOL XiaoWei";
    font-size: 80px;
    font-weight: normal;
    color: orchid;
    text-align: center;
  }
  select{
    border-radius: 5px;
    border: 2px solid black;
    float: left;
    margin: 10px 10px 0 140px;
    font-size: 20px;
    width: 120px;
    height: 50px;
  }
  input{
    box-sizing: border-box;
    float: left;
    border: 2px solid deepskyblue;
    border-radius: 5px;
    margin: 10px 10px 0 0;
    padding: 15px;
    font-size: 20px;
    width: 480px;
    height: 50px;
  }
  input:focus{
    border-color: blue;
  }
  button{
    border: 0;
    border-radius: 5px;
    margin: 10px 0 0 0;
    background-color: deepskyblue;
    float: left;
    width: 100px;
    height: 50px;
    font-size: 24px;
    color: white;
  }
  button:hover{
    background-color: cornflowerblue;
  }
  button:active{
    background-color: blue;
  }
</style>
