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
                :placeholder="placeholderText"
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
                <div v-if="searchType === 'place'">
                    <q-item 
                        v-for="result in searchResults"
                        class="result"
                        clickable
                        filled
                        @click="() => selectSearchResult(result)"
                    >
                        <div>{{ result.properties.name }}</div>
                        <div class="q-ml-md">
                            <sub><q-icon class="q-mr-sm" name="location_on" /> <i>{{ result.properties.coordinates.latitude.toFixed(5) }}, {{ result.properties.coordinates.longitude.toFixed(5) }} </i></sub>
                        </div>
                    </q-item>
                </div>
                <div v-else-if="searchType === 'coord'">
                    <q-item
                        v-if="searchResults"
                        class="result"
                        clickable
                        filled
                        @click="() => selectSearchResult(searchResults)"
                    >
                        <div>
                            <q-icon name="location_on" /> {{ parseFloat(searchResults[0]).toFixed(5) }}, {{ parseFloat(searchResults[1]).toFixed(5) }}
                        </div>
                    </q-item>
                </div>
                <div v-else-if="searchResults && searchResults.length > 0">
                    <q-item
                        v-for="result in searchResults"
                        class="result"
                        clickable
                        filled
                        @click="() => selectSearchResult(result)"
                    > 
                        <div> {{ result.properties.name || results.properties.id }}</div>
                        <div class="q-ml-md">
                            <sub><q-icon class="q-mr-sm" name="location_on" /><i>{{ result.geometry.coordinates[0].toFixed(5) }}, {{ result.geometry.coordinates[1].toFixed(5) }} </i></sub>
                        </div>
                    </q-item>
                </div>
            </q-list>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const emit = defineEmits(['go-to-location']);

const props = defineProps({
    pageSearchTypes: {
        type: Array,
        required: true,
    },
    mapPointsData: {
        type: Array,
        default: () => [],
    }
});

// search refs
const allSearchOptions = ref([
    { label: 'Place Name', value: 'place' },
    { label: 'Lng/Lat', value: 'coord' }
]);
const searchType = ref(allSearchOptions[0]);
const searchTerm = ref('');
const loadingResults = ref(false);
const searchResults = ref(null);
const placeholderText = ref('Search');

onMounted(() => {
    // append the page-specific search options to the default search options
    allSearchOptions.value.push(...props.pageSearchTypes.map(el => {
        return {label: el.label, value: el.type }
    }));
});

/**
 * updates the selected search type and resets values to avoid displaying
 * missing or no data while toggling
 * 
 * @param newType the newly-selected search type from the dropdown
 */
const updateSearchType = (newType) => {
    searchTerm.value = '';
    searchResults.value = null;
    searchType.value = newType;
    if(newType === 'coord'){
        placeholderText.value = '49.000, -123.000'
    } else {
        placeholderText.value = 'Search Term';
    }
}

/**
 * uses the provided search term to check the selected data type to search for. 
 * the pageSearchTypes prop should have some properties and handling that might
 * be specific to each page to make this work. 
 * 
 * @param term the current search term to search for
 */
const searchTermTyping = async (term) => {
    if(term === ''){
        searchResults.value = null;
        searchTerm.value = '';
        return;
    }
    searchTerm.value = term;
    // search by Location Name
    if(searchType.value === 'place'){
        searchResults.value = await searchByPlace(term);
    } 
    // search by latlng
    else if (searchType.value === 'coord') {
        searchResults.value = await searchByCoordinates(term);
    } 
    else {
        // only run the search when 3 or more characters are typed in, otherwise we risk
        // needlessly searching many entries multiple times
        if(term.length > 2){
            props.pageSearchTypes.forEach(searchable => {
                if(searchType.value === searchable.type){
                    try{
                        searchResults.value = searchable.searchFn(term);
                    } catch (e) {
                        searchResults.value = null;
                    }
                }
            })
        }
    }
}

/**
 * determines a set of coordinates by using a regular expression to check for 
 * a comma-separated list of coordinates.
 * 
 * @param term the coordinate string to parse from
 */
const searchByCoordinates = async (term) => {
    const coordRegex = new RegExp(/^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/)
    const coordString = term.toString().match(coordRegex);
    
    if(coordString){
        const coordsParsed = coordString[0].replace(' ', '').split(',');
        return coordsParsed;
    }
    loadingResults.value = false;
}

/**
 * searches for a place based on the provided search term using a rate-limited  
 * mapbox forward geolocating API call. This should be more than sufficient. 
 * 
 * @param term the place name to search for
 */
const searchByPlace = async (term) => {
    const url = `https://api.mapbox.com/search/geocode/v6/forward?q=${term}&country=CA&language=en&proximity=-127.6476,53.7267&bbox=-139.1072839004,48.2131718507,-114.0340694619,60.1821129075&access_token=${import.meta.env.VITE_APP_MAPBOX_TOKEN}&autocomplete=true&types=address,place,region`;

    try {
        const results = await fetch(url, {
            method: 'GET',
        }).then((res) => {
            return res.json()
        });

        return results.features;
    } catch (error) {
        console.error(error, 'There was an error');
    } finally {
        loadingResults.value = false;
    }
}


/**
 * handles the selection of a searhc result. The behaviour and result objects may differ
 * and therefore require unique handling in some cases. 
 * 
 * @param result response object from a page-specific data set to be used in handling
 */
const selectSearchResult = (result) => {
    if(searchType.value === 'place'){
        searchTerm.value = result.properties.name;
        emit('go-to-location', [ result.properties.coordinates.longitude, result.properties.coordinates.latitude]);
    }
    else if(searchType.value === 'coord'){
        emit('go-to-location', [ parseFloat(result[1]), parseFloat(result[0]) ]);
    }

    // handling for the passed-in page-specific search types, using their handlers
    props.pageSearchTypes.forEach(searchable => {
        if(searchType.value === searchable.type){
            const [resultData, map] = searchable.selectFn(result);
            onSearchSelect(resultData, map);
        }
    });

    searchResults.value = null;
}

/**
 * flys a map to the provided location using coordinate position mapping. 
 * zoom level is arbitrarily set, but can be increased/decreased as desired.  
 * 
 * @param coordinates map coodinates to fly to 
 * @param map provided map object which is used to move to the coordinates
 */
const onSearchSelect = (coordinates, map) => {
    map.flyTo({
        center: [coordinates[0], coordinates[1]],
        zoom: 10
    })
}
</script>

<style lang="scss">
.search-bar-container {
    display: flex;
    flex-direction: column;
    position: absolute;
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
        max-height: 20rem;
        overflow-y: auto;

        .search-result {
            .q-item {
                display: flex;
            }

            .result {
                display: flex;
                flex-direction: column;
            }
        }
    }

}
</style>
