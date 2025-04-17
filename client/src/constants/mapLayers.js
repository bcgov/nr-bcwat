export const pointLayer = {
    id: "point-layer",
    type: "circle",
    source: "point-source",
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

export const highlightLayer = {
    id: "highlight-layer",
    type: "circle",
    source: "point-source",
    paint: {
        "circle-color": "orange",
        "circle-opacity": 0.5,
        "circle-radius": {
            base: 6,
            stops: [
                [7, 6],
                [9, 8],
                [10, 10],
            ],
        },
        "circle-stroke-width": 3,
        "circle-stroke-color": "orange",
    },
    filter: false,
};
