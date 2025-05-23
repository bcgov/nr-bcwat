import watershed from '@/constants/watershed.json';
import streamflow from "@/constants/streamflow.json";
import climateStations from "@/constants/climateStations.json";
import groundWaterStations from "@/constants/groundWaterStations.json";
import surfaceWaterStations from "@/constants/surfaceWaterStations.json";

const mockWait = (ms) => {
   return new Promise(resolve => {
      setTimeout(resolve, ms);
   });
} 

export const getAllWatershedStations = async () => {
    return await mockWait(2000).then(() => watershed);
}

export const getStreamflowAllocations = async () => {
    return await mockWait(2000).then(() => streamflow);
}

export const getSurfaceWaterStations = async () => {
    return await mockWait(2000).then(() => surfaceWaterStations);
}

export const getGroundWaterStations = async () => {
    return await mockWait(2000).then(() => groundWaterStations);
}

export const getClimateStations = async () => {
    return await mockWait(2000).then(() => climateStations);
}
