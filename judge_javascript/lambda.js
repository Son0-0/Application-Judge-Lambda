const Judge = require("judge");

let successPayload = {
  statusCode: 200,
};

let errorPayload = {
  statusCode: 409,
};

exports.handler = async (event) => {
  try {
    const fileName = event.fileName;
    const problemId = event.problemId;
    const submit = event.submit;

    if (submit === true) {
      await Judge.downloadFile(fileName);
    } else {
      const code = event.code;
      await Judge.createFile(fileName, code);
    }
    const response = await Judge.spawnDFile(fileName, problemId);
    successPayload["body"] = response;
    return successPayload;
  } catch (error) {
    console.log("error: ", error);
    errorPayload["body"] = error.name;
    return errorPayload;
  }
};
