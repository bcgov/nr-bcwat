<template>
    <div class="search-bar-container">
        <q-select 
            :model-value="searchType"
            :options="allSearchOptions"
            map-options
            emit-value
            label="Search Type"
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
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
    pageSearchOptions: {
        type: Array,
        required: true,
    },
    mapPointsData: {
        type: Array,
        default: () => [],
    }
});

const allSearchOptions = ref([
    { label: 'Place', value: 'place' },
    { label: 'Lat/Lng', value: 'coord' }
]);
const searchType = ref(allSearchOptions[0]);
const searchTerm = ref('');
const placeholderText = ref('');

onMounted(() => {
    allSearchOptions.value.push(...props.pageSearchOptions);
});

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
    z-index: 1;

    .q-select {
        min-width: 8rem;
        margin: 0.25rem;

        .ellipsis {
            margin: 0 1rem;
        }
    }

    .q-input {
        margin: 0.25rem;
        min-width: 20rem;
    }
}
</style>
