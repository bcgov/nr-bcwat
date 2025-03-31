<template>
    <div class="sidebar">
        <router-link id="home" to="/" class="desktop-only desktop-link">
            <q-icon name="home" size="md" />
            Home
        </router-link>
        <hr />
        <router-link
            id="watershed"
            to="/watershed"
            class="desktop-only desktop-link"
        >
            <q-icon name="watershed" size="md" />
            Watershed
        </router-link>
    </div>
</template>

<style lang="scss" scoped>
.sidebar {
    height: 100vh;
    padding: 2em;
    width: 300px;
}
</style>
