import { getFilteredPoints } from '@/utils/mapHelpers.js';

self.onmessage = (e) => {
    const [pointArray, matchFilters, uniqueFilters] = e.data;
    const results = getFilteredPoints(pointArray, matchFilters, uniqueFilters);
    self.postMessage(results);
}
