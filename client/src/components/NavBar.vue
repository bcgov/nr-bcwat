<template>
    <div class="sidebar">
        <router-link
            v-for="link in links"
            :key="link.id"
            :to="link.to"
            class="nav-link"
        >
            <q-icon :name="link.icon" size="md" class="q-mr-md" />
            {{ link.label }}
        </router-link>
    </div>
</template>

<script setup>
const links = [
    {
        id: "home",
        to: "/",
        icon: "home",
        label: "Dashboard",
    },
    {
        id: "watershed",
        to: "/watershed",
        icon: "water",
        label: "Watershed",
    },
];
</script>

<style lang="scss" scoped>
.sidebar {
    height: 100vh;
    width: $nav-width;
    display: flex;
    flex-direction: column;

    .nav-link {
        border: 1px solid transparent;
        color: white;
        font-weight: bold;
        padding: 1em;
        width: $nav-width;

        &:hover {
            background-color: grey;
            border: 1px solid white;
        }

        @media (prefers-color-scheme: light) {
            color: grey;

            &:hover {
                border: 1px solid grey;
                background-color: lightgray;
            }
        }
    }
}
</style>
