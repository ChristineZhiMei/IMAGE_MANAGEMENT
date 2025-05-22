<script setup lang="ts">
import {globalStatus} from "./main.ts";
import {useDark, useToggle} from "@vueuse/core";

const store = globalStatus();

const isDark = useDark();
const toggleDark = useToggle(isDark);
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
          <button @click="toggleDark()" class="cursor-pointer border-b-2 border-dotted">
            <span class="ml-2 text-xl">{{ isDark ? 'Dark Edition' : 'Light Edition' }}</span>
          </button>
        </el-row>
      </el-header>
      <el-container class="h-[calc(100dvh-60px)]">
        <el-aside :class="`
        ${store.isMenuCollapse ? 'w-[4rem]!' : 'w-[20rem]!'}
        border-r-1 border-dashed border-r-gray-500
        switch-color
        transition-w duration-500 ease-in-out`">
          <div class="relative w-full aspect-square flex justify-center items-center ">
            <transition name="calendar-icon">
              <el-icon class="absolute" size="25px" v-if="store.isMenuCollapse">
                <svg  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
                  <path fill="currentColor" d="M128 384v512h768V192H768v32a32 32 0 1 1-64 0v-32H320v32a32 32 0 0 1-64 0v-32H128v128h768v64zm192-256h384V96a32 32 0 1 1 64 0v32h160a32 32 0 0 1 32 32v768a32 32 0 0 1-32 32H96a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h160V96a32 32 0 0 1 64 0zm-32 384h64a32 32 0 0 1 0 64h-64a32 32 0 0 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m192-192h64a32 32 0 0 1 0 64h-64a32 32 0 0 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m192-192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64m0 192h64a32 32 0 1 1 0 64h-64a32 32 0 1 1 0-64"></path>
                </svg>
              </el-icon>
            </transition>
          </div>
        </el-aside>
        <el-main>Main</el-main>
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
</style>
