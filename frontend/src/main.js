import { createApp } from "vue";
import { Quasar } from "quasar";
import router from "./router";
import "@quasar/extras/material-icons/material-icons.css";
import "@quasar/extras/fontawesome-v6/fontawesome-v6.css";
import "@quasar/extras/mdi-v6/mdi-v6.css";
import "quasar/src/css/index.sass";
import App from "./App.vue";

const myApp = createApp(App);

myApp.use(router);

myApp.use(Quasar, {
    plugins: {}, // import Quasar plugins and add here
});

myApp.mount("#app");
