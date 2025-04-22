<template>
    <svg
        xmlns="http://www.w3.org/2000/svg"
        display="block"
        viewBox="0 0 27 41"
    >
        <g transform="translate(3 29)">
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="10.5"
                ry="5.25"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="10.5"
                ry="5.25"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="9.5"
                ry="4.773"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="8.5"
                ry="4.295"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="7.5"
                ry="3.818"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="6.5"
                ry="3.341"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="5.5"
                ry="2.864"
            />
            <ellipse
                opacity=".04"
                cx="10.5"
                cy="5.8"
                rx="4.5"
                ry="2.386"
            />
        </g>
        <path
            class="color-fill"
            d="M27 13.5c0 5.575-6.75 13.5-12.25 21-.733 1-1.767 1-2.5 0C6.75 27 0 19.223 0 13.5 0 6.044 6.044 0 13.5 0S27 6.044 27 13.5z"
            :fill="props.fill"
        />
        <path
            d="M13.5 0C6.044 0 0 6.044 0 13.5c0 5.723 6.75 13.5 12.25 21 .75 1.023 1.767 1 2.5 0C20.25 27 27 19.075 27
            13.5 27 6.044 20.956 0 13.5 0zm0 1C20.415 1 26 6.585 26 13.5c0 2.399-1.504 5.681-3.78 9.238-2.274 3.557-5.515 7.404-8.277
            11.17-.2.273-.33.415-.443.533a4.934 4.934 0 01-.443-.533c-2.773-3.78-5.642-7.594-8.041-11.135C2.616 19.233 1 15.953 1 13.5 1
            6.585 6.585 1 13.5 1z"
            opacity=".25"
        />
        <g transform="translate(8 8)">
            <circle
                opacity=".25"
                cx="5.5"
                cy="5.5"
                r="5.5"
            />
            <circle
                fill="#FFF"
                cx="5.5"
                cy="5.5"
                r="5.5"
            />
        </g>
    </svg>
</template>

<script setup>

const props = defineProps({
    fill: {
        type: String,
        default: '#CCC',
    },
});

</script>
