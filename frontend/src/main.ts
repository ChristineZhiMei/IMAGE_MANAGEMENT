import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/theme-chalk/dark/css-vars.css'
import {createPinia, defineStore} from "pinia";

export const globalStatus = defineStore('darkCon', {
    state: () => {
        return{
            isMenuCollapse: false
        }
    },
    actions: {
        changeMenuCollapse(){
            this.isMenuCollapse = !this.isMenuCollapse
        }
    }
})


createApp(App)
    .use(ElementPlus, { size: 'small', zIndex: 3000})
    .use(createPinia())
    .mount('#app')
