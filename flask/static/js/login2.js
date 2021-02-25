let model, ctx, videoWidth, videoHeight, video, canvas, canvas2;
var data;
let i = 0,
  j = 0;
// let cap, src;
// let input_vid = [];
// let model2, vc;
let newFace = true;
var socket = io.connect("http://127.0.0.1:5000");
socket.on("connect", function () {
  console.log("SOCKET CONNECTED");
});

async function setupCamera() {
  video = document.getElementById("video");

  const stream = await navigator.mediaDevices.getUserMedia({
    audio: false,
    video: { facingMode: "user" },
  });
  video.srcObject = stream;

  return new Promise((resolve) => {
    video.onloadedmetadata = () => {
      resolve(video);
    };
  });
}

const renderPrediction = async () => {
  const returnTensors = false;
  const flipHorizontal = true;
  const annotateBoxes = true;
  const predictions = await model.estimateFaces(
    video,
    returnTensors,
    flipHorizontal,
    annotateBoxes
  );
  // console.log("new face: " + newFace + " j: " + j);
  if (predictions.length > 0 && newFace == true) {
    j++;
    // console.log("j: " + j + " i: " + i + " newFace: " + newFace);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // if (i < 1 && j >= 15 && j <= 40 && newFace == true) {
    // let pred = await testLiveness();
    // console.log("pre " + pred + " pred score " + pred[0][0]);
    // if (pred[0][0] > 0.95) {
    socket.emit("test liveness", {
      data: canvas2.toDataURL("image/png", 1.0),
    });
    socket.on("liveness prediction", (response) => {
      console.log("pred: " + response);
      if (response > 0.95) {
        takePicture();
        console.log("data: " + data);
        var form = document.getElementById("myAwesomeForm");
        // Create a FormData and append the file with "image" as parameter name
        var formDataToUpload = new FormData(form);
        formDataToUpload.append("image", data);
        fetch("/login2", {
          method: "POST",
          body: formDataToUpload,
        }).then(function (response) {
          console.log(response.json());
        });
        newFace = false;
      }
    });

    // var request = new XMLHttpRequest();
    // request.open("POST", "/login");
    // console.log("form: " + formDataToUpload);
    // request.send(formDataToUpload);

    // i++;
    // }
    // }

    for (let i = 0; i < predictions.length; i++) {
      if (returnTensors) {
        predictions[i].topLeft = predictions[i].topLeft.arraySync();
        predictions[i].bottomRight = predictions[i].bottomRight.arraySync();
        if (annotateBoxes) {
          predictions[i].landmarks = predictions[i].landmarks.arraySync();
        }
      }

      const start = predictions[i].topLeft;
      const end = predictions[i].bottomRight;
      const size = [end[0] - start[0], end[1] - start[1]];
      ctx.fillStyle = "rgba(255, 0, 0, 0.5)";
      ctx.fillRect(start[0], start[1], size[0], size[1]);

      if (annotateBoxes) {
        const landmarks = predictions[i].landmarks;

        ctx.fillStyle = "blue";
        for (let j = 0; j < landmarks.length; j++) {
          const x = landmarks[j][0];
          const y = landmarks[j][1];
          ctx.fillRect(x, y, 5, 5);
        }
      }
    }
  } else {
    newFace = true;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    i = 0;
    j = 0;
  }

  requestAnimationFrame(renderPrediction);
};

const setupPage = async () => {
  await setupCamera();
  // vc = new cv.VideoCapture(video);
  // src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
  video.play();
  // model2 = await tf.loadLayersModel(
  //   "http://127.0.0.1:8080/model/new/model.json"
  // );

  canvas2 = document.getElementById("canvas");
  // video.videoWidth = 100;
  // video.videoHeight = 100;

  videoWidth = video.videoWidth;
  videoHeight = video.videoHeight;
  video.width = videoWidth;
  video.height = videoHeight;

  canvas = document.getElementById("output");
  canvas.width = videoWidth;
  canvas.height = videoHeight;
  ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(255, 0, 0, 0.5)";

  model = await blazeface.load();

  renderPrediction();
  // testLiveness();
};

function takePicture() {
  var context = canvas2.getContext("2d");
  if (videoWidth && videoHeight) {
    canvas2.width = videoWidth;
    canvas2.height = videoHeight;
    context.drawImage(video, 0, 0, videoWidth, videoHeight);

    data = canvas2.toDataURL("image/png", 1.0);
  } else {
    clearphoto();
  }
}

// function testLiveness() {
//   console.log("inside live func");
//   let liveimg = new cv.Mat(video.height, video.width, cv.CV_8UC4);
//   // let liveimg2 = new cv.Mat();
//   let dsize = new cv.Size(100, 100);
//   console.log("init var");
//   // cv.resize(src, liveimg, dsize, 0, 0, cv.INTER_LINEAR);
//   console.log("first line done");
//   cv.cvtColor(liveimg, liveimg, cv.COLOR_BGR2GRAY);
//   console.log("cv done");
//   input_vid.push(liveimg);
//   let inp = nj.array([input_vid.slice(-24)]);
//   console.log("inp type: " + typeof inp);
//   let inp2 = nj.array();
//   for (var k = 0, length = inp.length; k < length; k++) {
//     inp2[k] = array[k] / 255;
//   }
//   console.log("inp type: " + typeof inp2);
//   let inp3 = inp2.reshape(1, 24, 100, 100, 1);
//   // math.reshape(inp, [1, 24, 100, 100, 1]);
//   console.log("np done");
//   let pred = model2.predict(inp3);
//   console.log("pre " + pred + " pred score " + pred[0][0]);
//   input_vid = input_vid.slice(-25);
//   // return pred;
// }

// function openCvReady() {
//   cv["onRuntimeInitialized"] = () => {
//     // do all your work here
//     setupPage();
//   };
// }

setupPage();
