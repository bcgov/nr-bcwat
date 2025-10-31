import { reactive } from "vue";

// acts as a data store which will store data while across routing actions etc. 
export const portalHandler = reactive({
    viewType: '',
    updateViewType: (viewType) => {
        portalHandler.viewType = viewType;
    }
});
