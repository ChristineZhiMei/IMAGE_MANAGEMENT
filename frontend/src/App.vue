<script setup lang="ts">
import {globalStatus} from "./main.ts";
import {useDark, useToggle} from "@vueuse/core";

const store = globalStatus();

const isDark = useDark();
const toggleDark = useToggle(isDark);
</script>

<template>
  <el-container>
    <el-header class="main-nav switch-color-transition" height="64px">
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
    <el-container class="main-view">
      <el-menu
        class="left-menu"
        :collapse="store.isMenuCollapse"
      >
        <el-menu-item>
          <el-icon size="32">
            <svg class="stroke-2" fill="none" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor"/>
            </svg>
          </el-icon>
          <template #title><span class="mx-4">Overview</span></template>
        </el-menu-item>
      </el-menu>
      <el-main>

      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.el-menu--collapse{
    flex-shrink: 0 !important;
}
.left-menu:not(.el-menu--collapse){
    width: 200px;
    flex-shrink: 0 !important;
}
.switch-color-transition{
    transition: background-color .4s ease-in-out ,
                color .4s ease-in-out !important;
}
.main-nav{
    padding: 0;
    border-bottom: gray 1px solid;
    color:var(--front-view-color-light);
    background-color: var(--back-view-color);
}
el-container{
    height: 100lvh;
}
.main-view{
    height: calc(100dvh - 60px);
}
</style>
