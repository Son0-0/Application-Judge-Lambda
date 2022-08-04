const { spawnSync } = require("child_process");
const fs = require("fs");

const ID = process.env.s3Id;
const SECRET = process.env.s3Secret;
const BUCKET = process.env.s3Bucket;

const AWS = require("aws-sdk");
const s3 = new AWS.S3({
  accessKeyId: ID,
  secretAccessKey: SECRET,
});

const input = require('./input.json');
const output = require('./output.json');

async function downloadFile(fileName) {
  const params = {
    Bucket: BUCKET,
    Key: fileName,
  };

  const file = await s3.getObject(params).promise();
  fs.writeFileSync(`/tmp/${fileName}`, file.Body.toString());
}

async function createFile(fileName, code) {
  fs.writeFileSync(`/tmp/${fileName}`, code);
}

async function spawnDFile(fileName, problemId) {
  console.log(`fileName: ${fileName} problemId: ${problemId}`);

  const msg = [];
  const result = [];
  let index = 0;

  await Promise.all(
    input[problemId].map(async (data) => {
      const child = await spawnSync("node", [`/tmp/${fileName}`], {
        input: data,
        maxBuffer: Math.max(output[problemId][index].length * 2, 1000),
        timeout: 3000,
      });
      if (child.error) {
        const error = child.error.toString().split(" ")[3];
        if (error === "ENOBUFS") msg.push("출력초과");
        else if (error === "ETIMEDOUT") msg.push("시간초과");
        else msg.push(error);
        result.push(false);
      } else {
        if (child.stdout.toString() === output[problemId][index]) {
          result.push(true);
          msg.push(child.stdout.toString());
        } else {
          result.push(false);
          msg.push(child.stdout.toString());
        }
      }
      index += 1;
    })
  );

  let passRate = result.reduce((a, b) => a + b, 0);
  passRate = (passRate / result.length) * 100;

  const returnValue = JSON.stringify({
    results: result,
    passRate: passRate,
    msg: msg,
  });

  return returnValue;
}

module.exports = {
  downloadFile,
  createFile,
  spawnDFile,
};
