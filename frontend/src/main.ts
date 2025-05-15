import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'

createApp(App)
    .use(ElementPlus, { size: 'small', zIndex: 3000})
    .mount('#app')
