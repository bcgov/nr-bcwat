<template>
    <div class="search-bar-container">
        <div class="search-entry">
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
        <div class="search-results-container">
            <q-list 
                class="search-result"
            >
                <q-item 
                    v-for="result in searchResults"
                    clickable
                    filled
                    @click="() => selectSearchResult(result)"
                >
                    <div v-if="searchType === 'place'">
                        <q-icon name="location_on" />{{ result.properties.name }}
                        <div>
                            <i>{{ result.properties.coordinates.longitude.toFixed(5) }}, {{ result.properties.coordinates.latitude.toFixed(5) }}</i>
                        </div>
                    </div>
                </q-item>
            </q-list>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const emit = defineEmits(['go-to-location']);

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
const loadingResults = ref(false);
const searchResults = ref(false);
const placeholderText = ref('');

onMounted(() => {
    allSearchOptions.value.push(...props.pageSearchOptions);
});

const updateSearchType = (newType) => {
    searchType.value = newType;
    // additional handling for type change. 
}

const searchTermTyping = async (term) => {
    searchTerm.value = term;
    // search by Location Name

    if(searchType.value === 'place'){
        const url = `https://api.mapbox.com/search/geocode/v6/forward?q=${term}&country=CA&language=en&proximity=-127.6476,53.7267&bbox=-139.1072839004,48.2131718507,-114.0340694619,60.1821129075&access_token=${import.meta.env.VITE_APP_MAPBOX_TOKEN}&autocomplete=true&types=address,place,region`;

        try {
            const results = await fetch(url, {
                method: 'GET',
            }).then((res) => {
                return res.json()
            });

            searchResults.value = results.features;
        } catch (error) {
            console.error(error, 'There was an error');
        } finally {
            loadingResults.value = false;
        }
    } 
    // search by latlng
    else if (searchType.value === 'coord') {  
        const coordRegex = new RegExp(/^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/)
        const coordString = term.toString().match(coordRegex);
        
        if(coordString){
            const coordsParsed = coordString[0].replace(' ', '').split(',');
            searchResults.value = coordsParsed;
        }
        loadingResults.value = false;
    } 
}

const selectSearchResult = (result) => {
    searchTerm.value = result.properties.name;
    if(searchType.value === 'place'){
        emit('go-to-location', result.properties.coordinates)
    }
    searchResults.value = [];
}
</script>

<style lang="scss">
.search-bar-container {
    display: flex;
    flex-direction: column;
    position: absolute;
    width: 50%;
    top: 0;
    right: 1rem;
    z-index: 1;

    .search-entry {
        display: flex;
        justify-content: end;

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

    .search-results-container {
        background-color: white;
    }

}
</style>
