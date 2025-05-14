<template>
    <div class="search-bar-container">
        <q-input 
            :model-value="searchTerm"
            color="white"
            dense 
            @update:model-value="onSearchTermType"
        />
    </div>
</template>

<script setup>
import { ref } from 'vue';


const searchTerm = ref('');

const onSearchTermType = (term) => {
    searchTerm.value = term;
}
</script>

<style lang="scss">
.search-bar-container {
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    z-index: 999 !important;

    input {
        min-width: 20rem;
    }
}
</style>
