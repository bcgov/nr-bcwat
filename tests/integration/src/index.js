import dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import assert from "node:assert/strict";
import Ajv from "ajv";

import pkg from "lodash";

dotenv.config();

const { isEqual, omit } = pkg;

const ajv = new Ajv({allErrors: true})

const __filename = fileURLToPath(import.meta.url);

const __dirname = path.dirname(__filename);
const apiName = process.env.API_NAME;
const BASE_URL = process.env.BASE_URL;

async function performEachMethod(BASE_URL, testCase, method, id) {
    let url = BASE_URL + testCase.path;
    if (id && ["GET", "PUT", "PATCH", "DELETE"].includes(method)) {
      url = url.endsWith("/") ? url + id : url + "/" + id;
    }

    let payload;
    if (method === "POST") payload = testCase.data?.post_payload;
    if (method === "PUT") payload = testCase.data?.put_payload;
    if (method === "PATCH") payload = testCase.data?.patch_payload;

    const response = await fetch(url, {
      method,
      headers: {
        ...testCase.headers
      },
      body: payload ? JSON.stringify(payload) : undefined,
    });

    console.info(`Response for ${method} ${url} : ${response.status}`);

    const methodAssertion = testCase.assertions.find(a => a.method === method);
    const responseData = await response.json().catch(() => ({})); // handle empty or invalid JSON

    const data = responseData?.data || responseData;

    if (methodAssertion) {
      if (methodAssertion.status_code) {
        assert.strictEqual(response.status, methodAssertion.status_code);
      }
      if (methodAssertion.body) {
        assert(isEqual(omit(data, testCase.data.id_field), methodAssertion.body));
      }
      if (methodAssertion.schema) {
        const validate = ajv.compile(methodAssertion.schema);
        const valid = validate(data);
        if (!valid) {
          console.error(`Schema validation failed for ${method} ${url}`);
          console.error(validate.errors);
          throw new assert.AssertionError({
            message: "Response schema validation failed",
            actual: data,
            expected: methodAssertion.schema,
            operator: "json-schema"
          });
        }
      }
    }

    if (method === "POST") {
      return data[testCase.data.id_field];
    }
  }

async function performTesting(testSuitesDir, testSuiteFile) {
  console.info(`Running test suite for : ${testSuiteFile}`);
  const testSuitePath = path.join(testSuitesDir, testSuiteFile);
  const testSuite = JSON.parse(await fs.promises.readFile(testSuitePath, "utf-8"));
  for (const testCase of testSuite.tests) {
    let id = null;
    for (const method of testCase.methods) {
      const responseId = await performEachMethod(BASE_URL, testCase, method, id);
      if (responseId) {
        id = responseId;
      }
    }
  }
}

const main = async () => {
  const testSuitesDir = path.join(__dirname, "test_suites");
  const testSuiteFiles = await fs.promises.readdir(testSuitesDir);
  const testFile = testSuiteFiles.find(file => file.includes(apiName));
  await performTesting(testSuitesDir, testFile);
};

try {
  await main();
} catch (e) {
  if (e instanceof assert.AssertionError) {
    console.error(e);
    process.exit(137);
  }
  console.error(e);
  process.exit(137);
}

