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
  let url = `${__ENV.BACKEND_URL}`;

  let baseParams = {
    headers: {
      "Content-Type": "application/json"
    }
  };

  const routes = [
    {
      route: '/climate/stations',
      description: 'Get climate stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/climate/stations/1/report',
      description: 'Get climate report by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: '/groundwater/level/stations',
      description: 'Get groundwater level stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/groundwater/quality/stations',
      description: 'Get groundwater quality stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/groundwater/level/stations/1/report',
      description: 'Get groundwater level report by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: '/groundwater/quality/stations/1/report',
      description: 'Get groundwater quality report by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: '/streamflow/stations',
      description: 'Get streamflow stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/streamflow/stations/1/report',
      description: 'Get streamflow report by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: 'streamflow/stations/1/report/flow-duration',
      description: 'Get stream report flow duration by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: '/surface-water/stations',
      description: 'Get surface water stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/surface-water/stations/1/report',
      description: 'Get surface water report by station ID',
      params: baseParams,
      status: 200
    },
    {
      route: '/watershed/stations',
      description: 'Get watershed stations',
      params: baseParams,
      status: 200
    },
    {
      route: '/watershed/stations/1/report',
      description: 'Get watershed report by station ID',
      params: baseParams,
      status: 200
    }
  ];


  routes.forEach(route => {
    let fullUrl = `${url}${route.route}`;
    let res = http.get(fullUrl, route.params);
    checkStatus(res, route.description, route.status);
  });
}
