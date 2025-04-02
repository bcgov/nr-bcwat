export const watershedLayer = {
    id: "watershed-layer",
    type: "circle",
    source: "watershed-source",
    paint: {
        // 'circle-color': ['get', 'color'],
        "circle-color": "#0000CD",
        "circle-radius": {
            base: 3,
            stops: [
                [7, 3],
                [9, 5],
                [10, 7],
            ],
        },
        "circle-stroke-color": "#FFF",
        "circle-stroke-width": 1,
    },
};
