import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { Button, setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'
import { createPinia } from 'pinia'
import { useUserStore } from './stores/user.js'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)
app.use(createPinia())

app.component('Button', Button)
const { fetchUserResource } = useUserStore()

app.mount('#app')
