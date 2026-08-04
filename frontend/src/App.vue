<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-header class="app-header" :height="'auto'">
          <div class="header-content">
            <h1 @click="router.push('/')">GPU维修工单系统</h1>
            <el-menu
              :default-active="route.path"
              mode="horizontal"
              :router="true"
              class="header-menu"
              :ellipsis="false"
            >
              <el-menu-item index="/">
                <el-icon><HomeFilled /></el-icon>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="/tickets">
                <el-icon><List /></el-icon>
                <span>工单列表</span>
              </el-menu-item>
              <el-menu-item v-if="userStore.isAdmin" index="/tickets/add">
                <el-icon><Plus /></el-icon>
                <span>添加工单</span>
              </el-menu-item>
            </el-menu>
            <div class="user-info" v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleCommand">
                <span class="user-dropdown">
                  <el-icon><User /></el-icon>
                  <span>{{ userStore.user?.username }}</span>
                  <el-tag v-if="userStore.isAdmin" size="small" type="danger">管理员</el-tag>
                  <el-tag v-else size="small" type="info">普通用户</el-tag>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

async function handleCommand(command) {
  if (command === 'logout') {
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  height: auto !important;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  min-height: 60px;
}

.header-content h1 {
  color: white;
  font-size: 20px;
  margin-right: 50px;
  cursor: pointer;
  white-space: nowrap;
}

.header-menu {
  background: transparent;
  border: none;
  flex: 1;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.85);
  border-bottom: none;
}

.header-menu .el-menu-item:hover,
.header-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.user-info {
  margin-left: auto;
  color: white;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  cursor: pointer;
}

.user-dropdown .el-tag {
  margin-left: 4px;
}

.app-main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .app-header {
    padding: 10px;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-content h1 {
    font-size: 16px;
    margin-right: 0;
    text-align: center;
  }

  .user-info {
    margin-left: 0;
    margin-top: 10px;
    width: 100%;
    text-align: center;
  }

  .user-dropdown {
    justify-content: center;
  }

  .header-menu {
    width: 100%;
    background: transparent;
    border: none;
  }

  .header-menu .el-menu-item {
    padding: 0 8px;
    font-size: 13px;
    height: 40px;
    line-height: 40px;
    color: rgba(255, 255, 255, 0.85);
    border-bottom: none;
  }

  .header-menu .el-menu-item:hover,
  .header-menu .el-menu-item.is-active {
    background: rgba(255, 255, 255, 0.15);
    color: white;
  }

  .app-main {
    padding: 10px;
  }
}
</style>