import { defineStore } from 'pinia'
import axios from 'axios'
const CACHE_PATH = 'http://127.0.0.1:5656/'
export const usePhotoStore = defineStore('PhotoStore', {
    // ÆäËûÅäÖÃ...
    state:()=>{
        return{
            photoList:{},
            photoInfo:{}
        }
    },
    actions: {
        async updatePhotoList(url:string){
            const res = await axios({
                method: 'get',
                url: CACHE_PATH+'getphotos/'+url,
            })
            console.log(res.data)
            this.photoList = res.data.photoList
        },
        async updatePhotoDateInfo(){
            const res = await axios({
                method: 'get',
                url: CACHE_PATH+'getinfo/',
            })
            console.log(res.data.allDates)
            this.photoInfo = res.data
        }
    }
})