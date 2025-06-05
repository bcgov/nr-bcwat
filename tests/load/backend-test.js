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


export default function() {
  let url = `${__ENV.BACKEND_URL}/`;
  let params = {
    headers: {
      "Content-Type": "application/json"
    }
  };
  let res = http.get(url, params);
  checkStatus(res, "Hello World", 200);

  let demoUrl = `${__ENV.BACKEND_URL}/demo`;
  let demoParams = {
    headers: {
      "Content-Type": "application/json"
    }
  };
  let demoRes = http.get(demoUrl, demoParams);
  checkStatus(demoRes, "Demo", 200);

}
