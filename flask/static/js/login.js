let model, ctx, videoWidth, videoHeight, video, canvas, canvas2;
var data;
let i = 0,
  j = 0;
let cap, src;
let input_vid = new Array();
let model2, vc;
let newFace = true;
let liveimg;

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
  if (predictions.length > 0) {
    j++;
    console.log("j: " + j + " i: " + i + " newFace: " + newFace);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (i < 1 && j == 30 && newFace == true) {
      let pred = await testLiveness();
      console.log("pre " + pred + " pred score " + pred[0][0]);
      if (pred[0][0] > 0.95) {
        takePicture();
        console.log("data: " + data);
        var form = document.getElementById("myAwesomeForm");
        // Create a FormData and append the file with "image" as parameter name
        var formDataToUpload = new FormData(form);
        formDataToUpload.append("image", data);

        var request = new XMLHttpRequest();
        request.open("POST", "/login2");
        console.log("form: " + formDataToUpload);
        request.send(formDataToUpload);
        i++;
        newFace = false;
      }
    }

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
  video.play();
  
  model2 = await tf.loadLayersModel(
    "http://127.0.0.1:8080/model/new/model.json"
  );

  canvas2 = document.getElementById("canvas");
  video.videoWidth = 100;
  video.videoHeight = 100;

  videoWidth = 100;
  videoHeight = 100;
  video.width = videoWidth;
  video.height = videoHeight;

  canvas = document.getElementById("output");
  canvas.width = videoWidth;
  canvas.height = videoHeight;
  ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(255, 0, 0, 0.5)";

  model = await blazeface.load();
  cap = new cv.VideoCapture(video);
  src = new cv.Mat(video.height, video.width, cv.CV_8UC4);

  // renderPrediction();
  testLiveness();
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

function testLiveness() {
  console.log("inside live func");
  // = new cv.Mat(video.height, video.width, cv.CV_8UC4);
  let temp;
  let inp;
  let inp2;
  let inp3;
  let pred;
  cap.read(src);

  while(true){
    if(input_vid.length<24){
      liveimg = new cv.Mat(video.height, video.width, cv.CV_8UC4);
      cv.cvtColor(src, liveimg, cv.COLOR_BGR2GRAY);
      let numpy_array = Array.from(liveimg.data)
      numpy_array = math.reshape(numpy_array, [100,100])
      // numpy_array = nj.ndarray(numpy_array);
      input_vid.push(numpy_array);
      // console.log(typeof(input_vid))
      // console.log(typeof(liveimg))
      // console.log(input_vid.length)
    }
    else{
      liveimg = new cv.Mat(video.height, video.width, cv.CV_8UC4);
      cv.cvtColor(src, liveimg, cv.COLOR_BGR2GRAY);
      let numpy_array = Array.from(liveimg.data)
      numpy_array = math.reshape(numpy_array, [100,100])
      // numpy_array = nj.ndarray(numpy_array);
      input_vid.push(numpy_array);
      // console.log(input_vid);
      temp = input_vid.slice(-24)
      // console.log(temp)
      // for(let k = 0; k < temp.length; k++) {
      //   for(let p = 0; )
      // }
      // inp = nj.ndarray(temp);
      // console.log(inp)
      // inp2 = nj.divide(inp, 255)
      // for (var k = 0, length = inp.length; k < length; k++) {
      //   inp2[k] = inp[k] / 255;
      // }
      // console.log(inp2);
      inp3 = math.reshape(temp, [1, 24, 100, 100, 1]);
      // console.log(inp3);
      inp3 = math.divide(inp3, 255)
      let tensor = tf.tensor(inp3);
      pred = model2.predict(tensor);
      console.log("pre " + pred.print());
      input_vid = input_vid.slice(-25);
    }
  }
  // // let liveimg2 = new cv.Mat();
  
  // console.log("init var");
  // // cv.resize(src, liveimg, dsize, 0, 0, cv.INTER_LINEAR);
  // console.log("first line done");
  // console.log("cv done");
  // let inp = nj.array([input_vid.slice(-24)]);
  // console.log("inp type: " + typeof inp);
  // console.log(inp.length)
  // console.log(inp.shape)
  // console.log(inp.ndim)
  // let inp2 = nj.array();
  // for (var k = 0, length = inp.length; k < length; k++) {
  //   inp2[k] = array[k] / 255;
  // }
  // let inp3 = inp2.reshape(24, 100, 100, 1);
  // // math.reshape(inp, [1, 24, 100, 100, 1]);
  // console.log("np done");
  // let pred = model2.predict(inp3);
  // console.log("pre " + pred + " pred score " + pred[0][0]);
  // input_vid = input_vid.slice(-25);
  // // return pred;
}

function openCvReady() {
  cv["onRuntimeInitialized"] = () => {
    // do all your work here
    setupPage();
  };
  // setupPage();
}

// setupPage();
