import watershed from '@/constants/watershed.json';
import streamflow from "@/constants/streamflow.json";

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
