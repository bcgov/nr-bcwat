import watershed from '@/constants/watershed.json';
import streamflow from "@/constants/streamflow.json";

export const getAllWatershedStations = async () => {
    return new Promise(res => setTimeout(res(watershed), 2000));
}

export const getStreamflowAllocations = async () => {
    return new Promise(res => setTimeout(res(streamflow), 2000));
}
