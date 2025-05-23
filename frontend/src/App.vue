<script setup lang="ts">
import {ref,watch} from "vue";
import {globalStatus} from "./main.ts";
import {usePhotoStore} from "./store/photoList.ts";
import {useDark, useToggle} from "@vueuse/core";
import dayjs from 'dayjs';
const store = globalStatus();
const photoStore = usePhotoStore();
const isDark = useDark();
const toggleDark = useToggle(isDark);
const CACHE_PATH = 'http://127.0.0.1:5656/images/cache/'
const getImageUrl = (url: string) => {
  return CACHE_PATH + url.replace(/\\/g, '/')
}
const dates = ref([])
const years = ref([])
const year_month = ref([])
const getDisplayText = (cell) => {
  // console.log(cell);
  if (cell.type === 'years') {
    // 月份选择模式下显示月份名称
    return cell.text;
  } else if (cell.renderText) {
    // 年份选择模式下显示年份
    return  `${parseInt(cell.text) + 1}月`;
  } else {
    // 日期选择模式下显示日期
    return cell.text;
  }
};

const getCellStyle = (cell) => {
  if (cell.type === 'date') {
    return isHoliday(cell) ? 'text-red-500' : '';
  }
  return '';
};
watch(
    () => photoStore.photoInfo.allDates,
    (newDates) => {
      // 检查 newDates 是否为数组且不为空
      if (Array.isArray(newDates) && newDates.length > 0) {
        dates.value = newDates.map(date =>
            dayjs(date).format('YYYY-MM-DD')
        );
      } else {
        // 处理空值情况，避免渲染错误
        dates.value = [];
      }
      years.value = Array.from(new Set(dates.value.map(date => dayjs(date).year())))
      year_month.value = Array.from(new Set(dates.value.map(date => date.toString().substring(0,7))))
    },
    { immediate: true }
);

const isHoliday = (cell) => {
  const yearsSelect = document.querySelector('.el-date-picker__header-label')?.textContent
  if (cell.renderText){
    if (years.value.includes(parseInt(yearsSelect))){
      return year_month.value.includes(parseInt(yearsSelect)+'-'+(cell.text+1 <=9 && cell.text+1 > 0 ? '0':'')+(cell.text+1).toString())
    }
  }
  else if (cell.dayjs){
    const formattedDate = cell.dayjs.format('YYYY-MM-DD');
    return dates.value.includes(formattedDate);
  }
  else{
    return years.value.includes(cell.text)
  }

};
const selectDate = ref()
watch(selectDate,(newDates)=>{
  const selectTempDate = dayjs(selectDate.value).format('YYYY-MM-DD')
  if (selectTempDate){
    if (dates.value.includes(selectTempDate)){
      photoStore.updatePhotoList(selectTempDate.replace(/-/g,'/'))
    }
  }
})

photoStore.updatePhotoDateInfo()
</script>

<template>
  <div>
    <el-container>
      <el-header class="p-0! border-b-1 border-b-gray-500 border-dashed switch-color" height="4rem">
        <el-row class="h-full" align="middle">
          <el-icon size="64px" class="p-4.5" @click.prevent="store.changeMenuCollapse()">
            <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 6C4 5.44772 4.44772 5 5 5H19C19.5523 5 20 5.44772 20 6C20 6.55228 19.5523 7 19 7H5C4.44772 7 4 6.55228 4 6Z" fill="currentColor"/>
              <path d="M4 18C4 17.4477 4.44772 17 5 17H19C19.5523 17 20 17.4477 20 18C20 18.5523 19.5523 19 19 19H5C4.44772 19 4 18.5523 4 18Z" fill="currentColor"/>
              <path d="M5 11C4.44772 11 4 11.4477 4 12C4 12.5523 4.44772 13 5 13H13C13.5523 13 14 12.5523 14 12C14 11.4477 13.5523 11 13 11H5Z" fill="currentColor"/>
            </svg>
          </el-icon>
          <span class="text-xl select-none">Image Management<sup class="ml-0.5">DEV.1</sup></span>
          <button @click="toggleDark()" class="cursor-pointer border-b-2 border-dotted" >
            <span class="ml-2 text-xl">{{ isDark ? 'Dark Edition' : 'Light Edition' }}</span>
          </button>
        </el-row>
      </el-header>
      <el-container class="h-[calc(100dvh-60px)]">
        <el-aside :class="`
        ${store.isMenuCollapse ? 'w-[4rem]!' : 'w-[20rem]!'}
        pt-5
        border-r-1 border-dashed border-r-gray-500
        switch-color
        transition-w duration-500 ease-in-out
        flex! flex-col
        relative`">
          <div class="relative w-full h-full flex flex-col items-center">
            <transition name="calendar-icon">
              <el-icon class="absolute z-0" :size="`${25/16}rem`" v-if="store.isMenuCollapse">
                <svg  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
                  <path fill="currentColor" d="M128 384v512h768V192H768v32a32 32 0 1 1-64 0v-32H320v32a32 32 0 0 1-64 0v-32H128v128h768v64zm192-256h384V96a32 32 0 1 1 64 0v32h160a32 32 0 0 1 32 32v768a32 32 0 0 1-32 32H96a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h160V96a32 32 0 0 1 64 0zm-32 384h64a32 32 0 0 1 0 64h-64a32 32 0 0 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m192-192h64a32 32 0 0 1 0 64h-64a32 32 0 0 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m192-192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64"></path>
                </svg>
              </el-icon>
            </transition>
            <transition>
              <div class="absolute z-1 w-[18rem] bg-red-500 flex flex-col items-center justify-start" v-if="!store.isMenuCollapse">
                <el-date-picker
                    v-model="selectDate"
                    type="date"
                    placeholder="Pick a Date"
                    format="YYYY/MM/DD"
                    size="default"
                    class="w-full!"
                    :editable=false
                    :default-value=" dates[0] || '2025-01-01'"
                >
                  <template #default="cell">
                    <div class="cell" :class="{ current: cell.isCurrent }">
                      <!-- 根据不同的选择模式显示不同的内容 -->
                      <span
                          :class="`text ${getCellStyle(cell)}`"
                      >{{ getDisplayText(cell) }}
                      </span>
                      <!-- 仅在日期模式下显示节假日标记 -->
                      <span v-if="isHoliday(cell)" class="holiday" />
                    </div>
                  </template>
                </el-date-picker>
              </div>
            </transition>
          </div>
        </el-aside>
        <el-main class="switch-color-light flex! flex-row flex-wrap justify-evenly gap-3">
            <el-image v-for="(item,index) in photoStore.photoList" :key="index" :src="getImageUrl(item.thumbnailPath)" lazy fit='contain' :class="`h-60 w-auto rounded-xl shadow-md`" >
              <template #error>
                <div class="flex items-center justify-center aspect-square h-full w-60 switch-color">
                  <el-icon :size="`${25/16}rem`" class="opacity-50">
                    <svg  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path fill="currentColor" d="M96 896a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h832a32 32 0 0 1 32 32v704a32 32 0 0 1-32 32zm315.52-228.48-68.928-68.928a32 32 0 0 0-45.248 0L128 768.064h778.688l-242.112-290.56a32 32 0 0 0-49.216 0L458.752 665.408a32 32 0 0 1-47.232 2.112M256 384a96 96 0 1 0 192.064-.064A96 96 0 0 0 256 384"></path></svg>
                  </el-icon>
                </div>
              </template>
              <template #placeholder>
                <div class="flex items-center justify-center aspect-square h-full w-60 switch-color">
                  <el-icon :size="`${25/16}rem`" class="opacity-50">
                    <svg  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path fill="currentColor" d="M96 896a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h832a32 32 0 0 1 32 32v704a32 32 0 0 1-32 32zm315.52-228.48-68.928-68.928a32 32 0 0 0-45.248 0L128 768.064h778.688l-242.112-290.56a32 32 0 0 0-49.216 0L458.752 665.408a32 32 0 0 1-47.232 2.112M256 384a96 96 0 1 0 192.064-.064A96 96 0 0 0 256 384"></path></svg>
                  </el-icon>
                </div>
              </template>
            </el-image>
            <div class="h-50 w-50 mr-auto"></div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>


el-container{
    height: 100lvh;
}

.switch-color{
  color:var(--front-view-color-light);
  background-color: var(--back-view-color);
}
.switch-color-light{
  color:var(--front-view-color-light);
  background-color: var(--back-view-color-light);
}

.calendar-icon-enter-from,
.calendar-icon-leave-to {
  opacity: 0;
}
.calendar-icon-enter-to,
.calendar-icon-leave-from {
  opacity: 1;
}
.calendar-icon-enter-active {
  transition: opacity 300ms ease 200ms;

}
.calendar-icon-leave-active {
  transition: opacity 200ms ease;
}
.cell {
  height: 30px;
  padding: 3px 0;
  box-sizing: border-box;
}
.cell .text {
  width: 30px;
  height: 24px;
  display: block;
  margin: 0 auto;
  line-height: 24px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
}
.cell .holiday {
  position: absolute;
  width: 6px;
  height: 6px;
  background: var(--el-color-danger);
  border-radius: 50%;
  bottom: 0px;
  left: 50%;
  transform: translateX(-50%);
}
</style>
