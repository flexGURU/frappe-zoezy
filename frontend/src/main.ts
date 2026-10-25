import { FrappeUI, frappeRequest, setConfig } from "frappe-ui"
import { createApp } from "vue"

import App from "./App.vue"
import { syncFavicon } from "./data/branding"
import router from "./router"
import "./index.css"

setConfig("resourceFetcher", frappeRequest)

createApp(App).use(FrappeUI).use(router).mount("#app")
syncFavicon()
