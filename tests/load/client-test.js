import { check } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";


export let errorRate = new Rate("errors");


function checkStatus(response, checkName, statusCode = 200) {
  let success = check(response, {
    [checkName]: (r) => {
      if (r.status === statusCode) {
        return true;
      } else {
        console.error(checkName + " failed. Incorrect response code." + r.status);
        return false;
      }
    }
  });
  errorRate.add(!success, { tag1: checkName });
}

// TODO: Initialize Handling of Pages that do not exist
export default function(token) {
  let baseUrl = `${__ENV.FRONTEND_URL}`;

  let baseResp = http.get(baseUrl);
  checkStatus(baseResp, "frontend", 200);

  let watershedResp = http.get(`${baseUrl}/watershed`);
  checkStatus(watershedResp, "watershed", 200);

  let streamflowResp = http.get(`${baseUrl}/streamflow`);
  checkStatus(streamflowResp, "streamflow", 200);

  let surfaceWaterQualityResp = http.get(`${baseUrl}/surface-water-quality`);
  checkStatus(surfaceWaterQualityResp, "surface-water-quality", 200);

  let groundWaterQualityResp = http.get(`${baseUrl}/ground-water-quality`);
  checkStatus(groundWaterQualityResp, "ground-water-quality", 200);

  let groundWaterLevelResp = http.get(`${baseUrl}/ground-water-level`);
  checkStatus(groundWaterLevelResp, "ground-water-level", 200);

  let climateResp = http.get(`${baseUrl}/climate`);
  checkStatus(climateResp, "climate", 200);

}
