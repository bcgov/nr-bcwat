<template>
    <div class="sidebar">
        <q-list>
            <q-item>
                <router-link id="home" to="/" class="nav-link">
                    <q-icon name="home" size="md" />
                    Home
                </router-link>
            </q-item>
            <q-item>
                <router-link id="watershed" to="/watershed" class="nav-link">
                    <q-icon name="water" size="md" />
                    Watershed
                </router-link>
            </q-item>
        </q-list>
    </div>
</template>

<style lang="scss" scoped>
.sidebar {
    height: 100vh;
    width: $nav-width;

    .nav-link {
        border: 1px solid aqua;
        width: $nav-width;
    }
}
</style>
