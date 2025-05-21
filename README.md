<h1 align="center"> IMAGE_MANAGEMENT </h1>

<div align="center">
    <img alt="Static Badge" src="https://img.shields.io/badge/Vue-3.5.13-gray?style=flat&logo=vue.js&labelColor=black">
    <img alt="Static Badge" src="https://img.shields.io/badge/Vite-6.3.5-gray?style=flat&logo=vite&labelColor=black">
    <img alt="Static Badge" src="https://img.shields.io/badge/Element_Plus-2.9.10-gray?style=flat&logo=elementplus&labelColor=black">
    <img alt="Static Badge" src="https://img.shields.io/badge/Django-5.2.1-gray?style=flat&logo=django&labelColor=black">
    <img src="https://img.shields.io/badge/DEV-1-gray?style=flat&labelColor=red" alt=""/>
</div><br/>

<div align="center"> 基于Vue3+Ts+TailwindCss+Element Plus+Django+DRF的windows本地图片管理工具，包括图片的查看、分类、移动、复制、删除、重命名、元数据修改、固定命名格式批量重命名、按照日期查看等功能</div>

## 开发服务器启动
### 前端
```console
cd fontend
npm install
num run dev
```

### 后端
 - 最好使用虚拟环境
 - 数据库迁移`python manage.py makemigrations` `python manage.py migrate`
 - 执行顺序
```console
pip install -r requirements.txt
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## 功能设计
标红部分为已完成功能

<a href="Function Design/IMAGE_MANAGEMENT.pdf" title="点击查看功能设计思维导图PDF">
  <img 
    src="Function Design/IMAGE_MANAGEMENT.png" 
    alt="功能设计思维导图" 
    title="功能设计思维导图"
    style="border: none;">
</a>
