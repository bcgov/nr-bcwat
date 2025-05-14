<template>
    <div class="search-bar-container">
        <q-select 
            :model-value="searchType"
            :options="props.searchOptions"
            map-options
            emit-value
            bg-color="white"
            dense 
            @update:model-value="updateSearchType"
        />
        <q-input 
            :model-value="searchTerm"
            placeholder="Search"
            bg-color="white"
            square
            dense 
            filled
            @update:model-value="searchTermTyping"
        />
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
    searchOptions: {
        type: Array,
        default: () => [
            { label: 'Place', value: 'place' },
            { label: 'Lat/Lng', value: 'coord' }
        ],
    },
    mapPointsData: {
        type: Array,
        default: () => [],
    }
});

const searchType = ref(props.searchOptions[0]);
const searchTerm = ref('');
const placeholderText = ref('');

const updateSearchType = (newType) => {
    searchType.value = newType;
    // additional handling for type change. 

}

const searchTermTyping = (term) => {
    searchTerm.value = term;
}
</script>

<style lang="scss">
.search-bar-container {
    display: flex;
    justify-content: end;
    position: absolute;
    width: 100%;
    top: 0;
    left: 0;
    z-index: 999 !important;

    .q-select {
        margin: 0.25rem;
    }

    .q-input {
        margin: 0.25rem;
        min-width: 20rem;
    }
}
</style>
